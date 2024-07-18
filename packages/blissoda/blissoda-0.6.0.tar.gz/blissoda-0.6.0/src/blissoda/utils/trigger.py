try:
    from bliss.scanning.scan_meta import get_user_scan_meta
    from bliss.scanning.scan_meta import META_TIMING
except ImportError:

    def get_user_scan_meta():
        raise ImportError("bliss is required")


def register_workflow_category(category: str = "workflows", timing: str = None):
    scan_meta_obj = get_user_scan_meta()
    if category not in scan_meta_obj.categories_names():
        scan_meta_obj.add_categories({category})
    if timing:
        timing = META_TIMING[timing.upper()]
    else:
        timing = META_TIMING.PREPARED
    scan_meta_obj.workflows.timing = timing
    scan_meta_obj.workflows.set("@NX_class", {"@NX_class": "NXcollection"})
    return scan_meta_obj.workflows


def unregister_workflow_category(category: str = "workflows") -> None:
    scan_meta_obj = get_user_scan_meta()
    try:
        # Before Bliss 1.11
        keys = list(scan_meta_obj._metadata.keys())
        for key in keys:
            if key.name.lower() == category:
                scan_meta_obj._metadata.pop(key)
    except Exception:
        pass
    # Since Bliss 1.11
    scan_meta_obj.remove_categories({category})
    try:
        _ = list(scan_meta_obj._metadata_keys())
    except AttributeError:
        pass
