"""Import of the NEOs and their close approaches from the NASA NeoWs API."""

import os
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

from business_object.approach import Approach
from business_object.import_bo import Import
from business_object.neo import Neo
from dao.approach_dao import ApproachDao
from dao.db_connection import DBConnection
from dao.import_dao import ImportDao
from dao.neo_dao import NeoDao
from utils.log_utils import get_logger, log

load_dotenv()
logger = get_logger(__name__)

NASA_FEED_URL = "https://api.nasa.gov/neo/rest/v1/feed"
MAX_DAYS_PER_CALL = 7  # limit of the NASA /feed endpoint
REQUEST_TIMEOUT_S = 30
MAX_RATE_LIMIT_RETRIES = 3  # DEMO_KEY is limited to 30 calls/hour and 50 calls/day
RATE_LIMIT_PAUSE_S = 60
DATA_PATH = Path(__file__).resolve().parents[3] / "data"


class ImportService:
    """Business logic of the NASA data import (NEOs and close approaches)."""

    @log
    def import_neo_range(
        self,
        start_date: date,
        end_date: date,
        user_id: int | None = 1,
        trigger_type: str = "MANUAL",
    ) -> dict:
        """Imports the NEOs approaching the Earth between two dates.

        The NASA API returns at most 7 days per call, so the period is split
        into windows. Each import is recorded in the import table with its
        status ('running', then 'success' or 'failed') and its counters.

        Args:
            start_date: First day of the period.
            end_date: Last day of the period.
            user_id: User who triggered the import.
            trigger_type: How the import was triggered ('MANUAL' or 'USUAL').

        Returns:
            dict: status, number of API calls, of NEOs and of approaches imported.

        Raises:
            RuntimeError: If the NASA API answers with an error, or keeps
                answering 429 (rate limit) after MAX_RATE_LIMIT_RETRIES pauses.
        """
        import_task = Import(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            trigger_type=trigger_type,
            status="running",
            nb_calls=0,
            nb_neo=0,
            nb_approaches=0,
        )
        import_dao = ImportDao()
        import_dao.create(import_task)

        last_saved_day = None  # end of the last window fully saved
        try:
            window_start = start_date
            while window_start <= end_date:
                window_end = min(window_start + timedelta(days=MAX_DAYS_PER_CALL), end_date)
                feed = self._fetch_feed(window_start, window_end, import_task)
                self._save_feed(feed, import_task)
                last_saved_day = window_end
                window_start = window_end + timedelta(days=1)
                time.sleep(0.2)  # be gentle with the NASA API
            import_task._status = "success"
        except Exception:
            if last_saved_day is None:
                import_task._status = "failed"
            else:
                # Some windows were saved (e.g. the NASA quota ran out in the middle):
                # the import is recorded as 'partial', ending at the last saved day,
                # so that the next import resumes from there instead of starting again
                import_task._status = "partial"
                import_task._end_date = last_saved_day
            raise
        finally:
            # Always record the final status, even when the import failed
            import_dao.update(import_task)

        return {
            "status": import_task._status,
            "nb_calls": import_task._nb_calls,
            "nb_neo": import_task._nb_neo,
            "nb_approaches": import_task._nb_approaches,
        }

    def _fetch_feed(self, window_start: date, window_end: date, import_task: Import) -> dict:
        """Calls the NASA /feed endpoint for one window of at most 7 days.

        Returns:
            dict: The "near_earth_objects" part of the answer ({date: [neo, ...]}).

        Raises:
            RuntimeError: On an API error or when the rate limit never resets.
        """
        params = {
            "start_date": window_start.strftime("%Y-%m-%d"),
            "end_date": window_end.strftime("%Y-%m-%d"),
            "api_key": os.getenv("NASA_API_KEY", "DEMO_KEY"),
        }
        logger.info(f"NASA import from {params['start_date']} to {params['end_date']}")

        for _attempt in range(MAX_RATE_LIMIT_RETRIES + 1):
            import_task._nb_calls += 1
            response = requests.get(NASA_FEED_URL, params=params, timeout=REQUEST_TIMEOUT_S)
            if response.status_code != 429:
                break
            logger.warning(f"NASA rate limit reached, pause of {RATE_LIMIT_PAUSE_S} s")
            time.sleep(RATE_LIMIT_PAUSE_S)
        else:
            raise RuntimeError("NASA API rate limit reached: set your own NASA_API_KEY")

        if response.status_code != 200:
            raise RuntimeError(f"NASA API error ({response.status_code}): {response.text}")
        return response.json().get("near_earth_objects", {})

    def _save_feed(self, feed: dict, import_task: Import) -> None:
        """Saves the NEOs of a NASA feed and their approaches, updating the counters."""
        neo_dao = NeoDao()
        approach_dao = ApproachDao()
        for date_str, neo_list in feed.items():
            for item in neo_list:
                neo = self._neo_from_nasa(item, date_str)
                if not neo_dao.create(neo):  # insert, or update if the NEO is already known
                    continue
                import_task._nb_neo += 1
                for approach_data in item.get("close_approach_data", []):
                    approach = self._approach_from_nasa(approach_data, neo.neo_id)
                    if approach_dao.create(approach):
                        import_task._nb_approaches += 1

    @staticmethod
    def _neo_from_nasa(item: dict, date_str: str) -> Neo:
        """Builds a Neo from one object of the NASA feed (diameters in km)."""
        diameter = item["estimated_diameter"]["kilometers"]
        return Neo(
            nasa_id=item["id"],
            name=item["name"],
            absolute_magnitude=float(item["absolute_magnitude_h"]),
            diameter_min=float(diameter["estimated_diameter_min"]),
            diameter_max=float(diameter["estimated_diameter_max"]),
            hazardous=bool(item["is_potentially_hazardous_asteroid"]),
            url_nasa=item["nasa_jpl_url"],
            origin="NASA",
            date_update=datetime.strptime(date_str, "%Y-%m-%d"),
        )

    @staticmethod
    def _approach_from_nasa(data: dict, neo_id: int) -> Approach:
        """Builds an Approach from one close_approach_data entry of the NASA feed.

        The exact time ("2026-Nov-11 17:25") is used when NASA gives it,
        otherwise the approach is dated at midnight of its day.
        """
        day = datetime.strptime(data["close_approach_date"], "%Y-%m-%d")
        approach_date = day
        if data.get("close_approach_date_full"):
            try:
                approach_date = datetime.strptime(
                    data["close_approach_date_full"], "%Y-%b-%d %H:%M"
                )
            except ValueError:
                pass  # unexpected format: keep the day at midnight
        return Approach(
            neo_id=neo_id,
            approach_day=day.date(),
            approach_date=approach_date,
            body=data["orbiting_body"],
            distance=float(data["miss_distance"]["kilometers"]),
            speed=float(data["relative_velocity"]["kilometers_per_hour"]),
        )

    @log
    def import_all(self, user_id: int = 1) -> dict:
        """Full import: from 2 years ago to 1 year ahead (first launch)."""
        today = date.today()
        start = today - timedelta(days=730)
        end = today + timedelta(days=365)
        return self.import_neo_range(start, end, user_id=user_id, trigger_type="MANUAL")

    @log
    def import_update(self, user_id: int = 1) -> dict:
        """Imports only what is missing since the last successful import.

        With no successful import yet, the full import is run instead.

        Returns:
            dict: The result of the import, or status 'up_to_date'.
        """
        today = date.today()
        last_import = ImportDao().find_last_successful_import()

        if last_import is None:
            return self.import_all(user_id=user_id)

        last_end = last_import._end_date
        if today + timedelta(days=365) < last_end + timedelta(days=1):
            return {"status": "up_to_date", "nb_calls": 0, "nb_neo": 0, "nb_approaches": 0}

        return self.import_neo_range(
            last_end + timedelta(days=1),
            today + timedelta(days=365),
            user_id=user_id,
            trigger_type="USUAL",
        )

    @log
    def reset_database(self) -> bool:
        """Re-creates all the tables (init_db.sql) and loads the seed data (pop_db.sql).

        Raises:
            FileNotFoundError: If init_db.sql is missing.
        """
        sql_path = DATA_PATH / "init_db.sql"
        if not sql_path.exists():
            raise FileNotFoundError(f"init_db.sql not found at {sql_path}")

        sql_content = sql_path.read_text(encoding="utf-8")

        # Seed data (admin account, test users...): init_db.sql creates no user
        pop_path = DATA_PATH / "pop_db.sql"
        if pop_path.exists():
            sql_content += "\n" + pop_path.read_text(encoding="utf-8")

        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(sql_content)
        logger.info("Database successfully reset via init_db.sql and pop_db.sql")
        return True
