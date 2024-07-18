from typing import Tuple
import os


def get_dataset_dir(dataset_filename: str) -> str:
    return os.path.dirname(os.path.abspath(dataset_filename))


def get_collection_dir(dataset_filename: str) -> str:
    return _abs_join(get_dataset_dir(dataset_filename), "..")


def get_raw_dir(dataset_filename: str) -> str:
    return _abs_join(get_collection_dir(dataset_filename), "..")


def get_proposal_dir(dataset_filename: str) -> str:
    dirname = get_raw_dir(dataset_filename)
    if os.path.basename(dirname) == "raw":
        # version 2
        return _abs_join(dirname, "..")
    # version 1: proposal == raw
    return dirname


def get_processed_dir(dataset_filename: str) -> str:
    version, dirname = get_directory_version(dataset_filename)
    if version == 3:
        return _abs_join(dirname, "..", "PROCESSED_DATA")
    if version == 2:
        return _abs_join(dirname, "..", "processed")
    return _abs_join(dirname, "processed")


def get_processed_subdir(dataset_filename, *subdirs) -> str:
    return os.path.join(get_processed_dir(dataset_filename), *subdirs)


def get_workflows_dir(dataset_filename: str) -> str:
    return get_processed_subdir(dataset_filename, "workflows")


def get_nobackup_dir(dataset_filename: str) -> str:
    version, dirname = get_directory_version(dataset_filename)
    if version == 3:
        return _abs_join(dirname, "..", "NOBACKUP")
    if version == 2:
        return _abs_join(dirname, "..", "_nobackup")
    return _abs_join(dirname, "_nobackup")


def get_directory_version(dataset_filename: str) -> Tuple[int, str]:
    """Returns directory structure version number and the raw data directory"""
    dirname = get_raw_dir(dataset_filename)
    if os.path.basename(dirname) == "RAW_DATA":
        return 3, dirname
    if os.path.basename(dirname) == "raw":
        return 2, dirname
    # proposal == raw
    return 1, dirname


def get_session_dir(dataset_filename: str) -> str:
    return _abs_join(get_proposal_dir(dataset_filename), "..")


def _abs_join(*args):
    return os.path.abspath(os.path.join(*args))
