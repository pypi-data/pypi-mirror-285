from pprint import pformat
from dataclasses import dataclass
from itertools import zip_longest
from collections.abc import MutableMapping
from typing import (
    Callable,
    Any,
    Iterator,
    Mapping,
    Iterable,
    Dict,
    Optional,
    NamedTuple,
    List,
)

import numpy

try:
    from bliss import current_session
except ImportError:
    current_session = None
try:
    from bliss.common.utils import autocomplete_property
except ImportError:
    autocomplete_property = property
try:
    from bliss.config.settings import HashObjSetting
except ImportError:
    try:
        from blissdata.settings import HashObjSetting
    except ImportError:
        HashObjSetting = None


@dataclass
class ParameterInfo:
    name: str
    category: str = "parameters"
    hidden: Optional[bool] = None
    doc: Optional[str] = None

    def __post_init__(self):
        if self.hidden is None:
            self.hidden = self.name.startswith("_")


class ParameterValue(NamedTuple):
    value: Any
    doc: Optional[str] = None


class WithPersistentParameters:
    """Adds parameters as properties that will be stored in Redis

    .. code:: python

        class MyClass(WithPersistentParameters, parameters=["a", "b"])
            pass

        myobj = MyClass()
        myobj.a = 10
        myobj.b = None  # remove
    """

    _PARAMETERS: Dict[str, ParameterInfo] = dict()

    def __init__(self, **defaults) -> None:
        if current_session is None:
            raise ModuleNotFoundError("No module named 'bliss'")
        self._parameters = HashObjSetting(
            f"blissoda:{current_session.name}:{self.__class__.__name__}"
        )
        for name, value in defaults.items():
            if self._get_parameter(name) is None:
                self._set_parameter(name, value)

    def __init_subclass__(cls, parameters=None, **kw) -> None:
        super().__init_subclass__(**kw)
        if parameters:
            extra_parameters = list()
            for p in parameters:
                if isinstance(p, str):
                    p = ParameterInfo(name=p)
                elif isinstance(p, Mapping):
                    p = ParameterInfo(**p)
                extra_parameters.append(p)
            extra_parameters = {p.name: p for p in extra_parameters}
        else:
            extra_parameters = dict()
        cls._PARAMETERS = {**cls._PARAMETERS, **extra_parameters}
        for name in extra_parameters:
            add_parameter_property(cls, name)

    def __dir__(self) -> Iterable[str]:
        return list(super().__dir__()) + [
            name for name, param in self._PARAMETERS.items() if not param.hidden
        ]

    def _info_categories(self) -> Dict[str, dict]:
        categories = dict()
        all_values = self._parameters.get_all()
        for name, param in self._PARAMETERS.items():
            if param.hidden:
                continue
            category = categories.setdefault(param.category, dict())
            value = all_values.get(name, None)
            category[name] = ParameterValue(value=value, doc=param.doc)
        return categories

    def __info__(self) -> str:
        return "\n\n".join(
            [
                f"{name.capitalize()}:\n {_format_info_category(category)}"
                for name, category in self._info_categories().items()
                if category
            ]
        )

    def _get_parameter(self, name):
        v = self._parameters.get(name)
        if isinstance(v, dict):
            return RedisDictWrapper(name, self._parameters.get, self._set_parameter)
        return v

    def _set_parameter(self, name, value):
        if isinstance(value, RemoteDictWrapper):
            value = value.to_dict()
        self._parameters[name] = value

    def _del_parameter(self, name):
        self._parameters[name] = None

    def _raise_when_missing(self, *names):
        for name in names:
            if self._get_parameter(name) is None:
                raise AttributeError(f"parameter '{name}' is not set")


def add_parameter_property(cls, name):
    if hasattr(cls, name):
        return
    method = autocomplete_property(lambda self: self._get_parameter(name))
    setattr(cls, name, method)
    method = getattr(cls, name).setter(
        lambda self, value: self._set_parameter(name, value)
    )
    setattr(cls, name, method)


class RemoteDictWrapper(MutableMapping):
    """Whenever you get, set or delete the value, the entire dictionary is pushed/pull from a remote source"""

    def __dir__(self) -> Iterable[str]:
        return list(super().__dir__()) + list(self)

    def _get_all(self) -> dict:
        raise NotImplementedError

    def _set_all(self, value: Mapping) -> dict:
        raise NotImplementedError

    def to_dict(self) -> dict:
        return self._get_all()

    def __str__(self):
        return str(self._get_all())

    def __repr__(self):
        return repr(self._get_all())

    def __getitem__(self, key: str) -> Any:
        value = self._get_all()[key]
        if isinstance(value, dict):
            value = MemoryDictWrapper(self, key)
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        adict = self._get_all()
        if isinstance(value, RemoteDictWrapper):
            value = value.to_dict()
        adict[key] = value
        return self._set_all(adict)

    def __delitem__(self, key: str) -> None:
        adict = self._get_all()
        del adict[key]
        return self._set_all(adict)

    def __iter__(self) -> Iterator[Any]:
        return self._get_all().__iter__()

    def __len__(self) -> int:
        return self._get_all().__len__()


class RedisDictWrapper(RemoteDictWrapper):
    def __init__(self, name: str, getter: Callable, setter: Callable) -> None:
        self._name = name
        self._getter = getter
        self._setter = setter

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("_name", "_getter", "_setter"):
            return super().__setattr__(name, value)
        self[name] = value

    def _get_all(self) -> dict:
        adict = self._getter(self._name)
        if adict is None:
            return dict()
        return adict

    def _set_all(self, value: Mapping) -> None:
        self._setter(self._name, value)


class MemoryDictWrapper(RemoteDictWrapper):
    def __init__(self, parent: RemoteDictWrapper, name: str):
        self._parent = parent
        self._name = name

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("_name", "_parent"):
            return super().__setattr__(name, value)
        self[name] = value

    def _get_all(self) -> dict:
        return self._parent._get_all()[self._name]

    def _set_all(self, value: Mapping) -> None:
        self._parent[self._name] = value


def _format_info_category(category: Dict) -> str:
    if not category:
        return ""

    rows: List[List[List[str]]] = list()
    for name, pvalue in category.items():
        ldoc = []
        if isinstance(pvalue, ParameterValue):
            value = pvalue.value
            if pvalue.doc:
                ldoc = str(pvalue.doc or "")
                ldoc = [ldoc[i : i + 60] for i in range(0, len(ldoc), 60)]
        else:
            value = pvalue
        lvalue = pformat(value, width=60).split("\n")
        rows.append([[str(name)], lvalue, ldoc])

    lengths = numpy.array(
        [[max(len(s) for s in lines) if lines else 0 for lines in row] for row in rows]
    )
    fmt = "   ".join(["{{:<{}}}".format(n) for n in lengths.max(axis=0)])

    lines = [
        fmt.format(*svalues)
        for row in rows
        for svalues in zip_longest(*row, fillvalue="")
    ]

    return "\n ".join(lines)
