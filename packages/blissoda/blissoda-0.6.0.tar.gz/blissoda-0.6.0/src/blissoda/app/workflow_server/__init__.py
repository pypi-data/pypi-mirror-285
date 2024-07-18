import json
import logging
from typing import Optional, Mapping

from ...exceptions import VersionError

# Note: import subscriber first because it might require patching
try:
    # blissdata >=1
    from .subscriberv1 import scan_iterator
except VersionError as exc:
    try:
        # blissdata >0.3.3,<1 (unreleased, branch id31_2.0)
        from .subscribervid31 import scan_iterator
    except VersionError:
        try:
            # blissdata <=0.3.3
            from .subscriberv0 import scan_iterator
        except VersionError:  # noqa F841
            _EXC = exc

            def scan_iterator(*args, **kw):
                raise _EXC


from ewoksjob.client import submit

logger = logging.getLogger(__name__)


def submit_scan_workflow(workflow=None, **kwargs) -> Optional[str]:
    if not workflow:
        return
    future = submit(args=(workflow,), kwargs=kwargs)
    return future.task_id


def main(args) -> None:
    for filename, scan_nb, workflows in scan_iterator(args.session):
        for wfname, nxprocess in workflows.items():
            if not isinstance(nxprocess, Mapping):
                continue
            try:
                job_id = submit_scan_workflow(
                    **json.loads(nxprocess["configuration"]["data"])
                )
            except Exception:
                logger.exception(
                    f"Error when submitting workflow '{wfname}' for scan {scan_nb} of file '{filename}'"
                )
            else:
                if job_id is not None:
                    logger.info(
                        f"Submitted workflow '{wfname}' (JOB ID {job_id}) for scan {scan_nb} of file '{filename}'"
                    )
