"""FO7 - Runs the NASA import in the background, on demand and automatically every day.

The first import covers 3 years (~150 NASA calls, much longer than any HTTP
timeout), so imports always run in a background thread, one at a time.
"""

import threading

from dao.user_dao import UserDao
from service.import_service import ImportService
from utils.log_utils import get_logger

logger = get_logger(__name__)

DAY_S = 24 * 3600

# Only one NASA import at a time (manual button and daily import share it)
_import_lock = threading.Lock()


def is_running() -> bool:
    """Tells whether a NASA import is currently running."""
    return _import_lock.locked()


def start_import(user_id: int, refresh: bool = True) -> bool:
    """Starts ImportService.import_update in a background thread.

    Args:
        user_id: The user recorded as the author of the import.
        refresh: Also re-import the next days (see ImportService.import_update).

    Returns:
        bool: True if the import was started, False if one is already running.
    """
    if not _import_lock.acquire(blocking=False):
        return False
    try:
        threading.Thread(target=_run, args=(user_id, refresh), daemon=True).start()
    except Exception:
        _import_lock.release()
        raise
    return True


def _run(user_id: int, refresh: bool) -> None:
    try:
        result = ImportService().import_update(user_id=user_id, refresh=refresh)
        logger.info(f"Background import finished: {result}")
    except Exception as e:
        logger.error(f"Background import failed: {e}")
    finally:
        _import_lock.release()


class DailyImportScheduler:
    """Starts an import when the API starts, then every `interval_s` seconds.

    The import is recorded in the name of the first administrator.
    """

    def __init__(self, interval_s: int = DAY_S):
        self._interval_s = interval_s
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Starts the scheduler thread (it does nothing if already started)."""
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info(f"Automatic NASA import every {self._interval_s} s")

    def stop(self) -> None:
        """Stops the scheduler (a running import finishes in the background)."""
        self._stop.set()

    def _loop(self) -> None:
        while not self._stop.is_set():
            self.trigger()
            self._stop.wait(self._interval_s)

    @staticmethod
    def trigger() -> bool:
        """Starts one automatic import.

        Returns:
            bool: True if an import was started.
        """
        try:
            admins = [user for user in UserDao().find_all() if user.role == "admin"]
        except Exception as e:
            logger.error(f"Automatic import skipped, database unavailable: {e}")
            return False
        if not admins:
            logger.warning("Automatic import skipped: no administrator account")
            return False
        started = start_import(admins[0].user_id, refresh=True)
        if not started:
            logger.info("Automatic import skipped: an import is already running")
        return started
