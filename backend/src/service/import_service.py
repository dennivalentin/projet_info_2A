from datetime import datetime, timedelta, date
import os
from pathlib import Path
from dao.db_connection import DBConnection
from pprint import pprint
import time
from dotenv import load_dotenv
import requests

from business_object.approach import Approach
from business_object.import_bo import Import
from business_object.neo import Neo
from dao.approach_dao import ApproachDao
from dao.import_dao import ImportDao
from dao.neo_dao import NeoDao
from utils.log_utils import get_logger, log

load_dotenv()
logger = get_logger(__name__)


class ImportService:

    @log
    def import_neo_range(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: int | None = 1,
        trigger_type: str = "MANUAL",
    ) -> dict:
        """
        Import data from API between two date. And add the NEO's approach to the approach table

        Parameters
        ----------
        start_date : datetime
        end_date : datetime
        user_id : int
        trigger_type : str, How the import has been triggered

            Dates given to the NASA API to get the import from endpoint /v1/feed
            Maximum 7 days

        Return
        ------
        Dict : with information about the import
        """
        api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")
        base_url = "https://api.nasa.gov/neo/rest/v1/feed"

        neo_dao = NeoDao()
        import_dao = ImportDao()
        approach_dao = ApproachDao()

        current_start = start_date

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
        import_dao.create(import_task)

        try:
            while current_start <= end_date:
                current_end = min(current_start + timedelta(days=7), end_date)

                params = {
                    "start_date": current_start.strftime("%Y-%m-%d"),
                    "end_date": current_end.strftime("%Y-%m-%d"),
                    "api_key": api_key,
                }

                print(
                    f"Importation from {params['start_date']} to"
                    f" {params['end_date']}"
                )

                import_task._nb_calls += 1
                response = requests.get(base_url, params=params)

                if response.status_code == 429:
                    print("Api limits reached (Rate Limit). 60s break")
                    time.sleep(60)
                    continue
                elif response.status_code != 200:
                    raise RuntimeError(
                        f"Erreur API ({response.status_code}) : {response.text}"
                    )

                data = response.json()
                near_earth_objects = data.get("near_earth_objects", {})

                for date_str, neo_list in near_earth_objects.items():
                    for item in neo_list:
                        diam = item["estimated_diameter"]["kilometers"]
                        neo = Neo(
                            item["id"],
                            item["name"],
                            float(item["absolute_magnitude_h"]),
                            float(diam["estimated_diameter_min"]),
                            float(diam["estimated_diameter_max"]),
                            bool(item["is_potentially_hazardous_asteroid"]),
                            item["nasa_jpl_url"],
                            "NASA",
                            datetime.strptime(date_str, "%Y-%m-%d"),
                        )

                        if neo_dao.create(neo):
                            import_task._nb_neo += 1
                            neo_id = neo._neo_id

                            for app_data in item.get("close_approach_data", []):
                                day_str = app_data["close_approach_date"]
                                full_date_str = app_data.get("close_approach_date_full")

                                approach_day = datetime.strptime(
                                    day_str, "%Y-%m-%d"
                                ).date()

                                if full_date_str:
                                    try:
                                        approach_date = datetime.strptime(
                                            full_date_str, "%Y-%b-%d %H:%M"
                                        )
                                    except ValueError:
                                        approach_date = datetime.strptime(
                                            day_str, "%Y-%m-%d"
                                        )
                                else:
                                    approach_date = datetime.strptime(
                                        day_str, "%Y-%m-%d"
                                    )

                                approach = Approach(
                                    neo_id=neo_id,
                                    approach_day=approach_day,
                                    approach_date=approach_date,
                                    body=app_data["orbiting_body"],
                                    distance=float(
                                        app_data["miss_distance"]["kilometers"]
                                    ),
                                    speed=float(
                                        app_data["relative_velocity"][
                                            "kilometers_per_hour"
                                        ]
                                    ),
                                )

                                if approach_dao.create(approach):
                                    import_task._nb_approaches += 1

                current_start = current_end + timedelta(days=1)
                time.sleep(0.2)

            import_task._status = "success"

        except Exception as e:
            import_task._status = "failed"
            raise e

        finally:
            import_dao.update(import_task)

        return {
            "status": import_task._status,
            "nb_calls": import_task._nb_calls,
            "nb_neo": import_task._nb_neo,
            "nb_approaches": import_task._nb_approaches,
        }

    @log
    def import_all(self) -> dict:
        """Manual import over 3 years"""
        today = date.today()
        start = today - timedelta(days=730)
        end = today + timedelta(days=365)
        return self.import_neo_range(start, end, user_id=1, trigger_type="MANUAL")

    @log
    def import_update(self, user_id: int = 1) -> dict:
        """usual import and if nothing available in database, we import the complete data"""
        today = date.today()
        last_import = ImportDao().find_last_successful_import()

        if last_import is None:
            return self.import_all()

        last_end = last_import._end_date

        if today + timedelta(days=365) < last_end + timedelta(days=1):
            return {
                "status": "up_to_date",
                "nb_calls": 0,
                "nb_neo": 0,
                "nb_approaches": 0,
            }

        return self.import_neo_range(last_end + timedelta(days=1), today + timedelta(days=365), user_id= user_id, trigger_type="USUAL")


    @log
    def reset_database(self) -> bool:
        """Run init_db.sql to reset"""

        sql_path = Path(__file__).resolve().parents[3] / "data" / "init_db.sql"

        if not sql_path.exists():
            raise FileNotFoundError(f"init_db.sql not found at {sql_path.resolve()}")

        with open(sql_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                cur.execute(sql_content)
        
        logger.info("Database successfully reset via init_db.sql")
        return True
