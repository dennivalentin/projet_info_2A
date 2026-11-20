"""Unit tests of the background NASA import (FO7). ImportService and UserDao are mocked."""

import threading
from unittest.mock import MagicMock, patch

import pytest

from business_object.user import User
from service import import_scheduler
from service.import_scheduler import DailyImportScheduler, start_import


@pytest.fixture
def blocked_import():
    """Replaces ImportService with an import that runs until `release` is set."""
    release = threading.Event()
    service = MagicMock()
    service.import_update.side_effect = lambda **kwargs: release.wait(5)
    with patch.object(import_scheduler, "ImportService", return_value=service):
        yield service, release
    release.set()


def _wait_until_finished():
    for _ in range(100):
        if not import_scheduler.is_running():
            return
        threading.Event().wait(0.02)


def test_only_one_import_at_a_time(blocked_import):
    service, release = blocked_import

    assert start_import(user_id=1) is True
    assert import_scheduler.is_running()
    assert start_import(user_id=1) is False  # the first one is still running

    release.set()
    _wait_until_finished()
    assert not import_scheduler.is_running()
    service.import_update.assert_called_once_with(user_id=1, refresh=True)


def test_a_failed_import_releases_the_lock():
    service = MagicMock()
    service.import_update.side_effect = RuntimeError("NASA down")
    with patch.object(import_scheduler, "ImportService", return_value=service):
        assert start_import(user_id=1) is True
        _wait_until_finished()
    assert not import_scheduler.is_running()


def test_daily_import_is_recorded_for_the_first_admin(blocked_import):
    service, release = blocked_import
    users = [
        User(user_id=3, username="bob", role="user"),
        User(user_id=1, username="admin", role="admin"),
    ]
    with patch.object(import_scheduler, "UserDao") as user_dao:
        user_dao.return_value.find_all.return_value = users
        assert DailyImportScheduler.trigger() is True
    release.set()
    _wait_until_finished()
    service.import_update.assert_called_once_with(user_id=1, refresh=True)


def test_daily_import_is_skipped_without_admin():
    with patch.object(import_scheduler, "UserDao") as user_dao:
        user_dao.return_value.find_all.return_value = [User(user_id=3, username="bob", role="user")]
        assert DailyImportScheduler.trigger() is False
    assert not import_scheduler.is_running()
