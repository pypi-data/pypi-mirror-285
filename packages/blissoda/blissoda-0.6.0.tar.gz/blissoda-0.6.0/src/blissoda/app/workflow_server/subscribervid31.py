import logging
from typing import Iterator, Tuple, Dict

from ...exceptions import VersionError

try:
    from blissdata.scan import Scan
    from blissdata import redis_engine
    from blissdata.beacon.data import BeaconData
    from blissdata.redis_engine.search import get_next_scan
except ImportError as e:
    raise VersionError(str(e)) from e

logger = logging.getLogger(__name__)


def scan_iterator(session_name) -> Iterator[Tuple[str, int, Dict]]:
    logger.info(f"Started listening to Bliss session '{session_name}'")
    _ensure_redis()

    since = None
    while True:
        since, key = get_next_scan(since=since)
        scan = Scan.load(key)
        if scan.session != session_name:
            continue
        if scan.info.get("is-scan-sequence") or scan.info.get("group"):
            continue
        workflows = scan.info.get("workflows")
        if not workflows:
            continue
        filename = scan.info.get("filename")
        yield filename, scan.number, workflows


def _ensure_redis() -> None:
    url = BeaconData().get_redis_data_db()
    redis_engine.set_redis_url(url)
