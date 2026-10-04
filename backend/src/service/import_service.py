import requests
import os
import time
from dotenv import load_dotenv
from pprint import pprint
from dao.neo_dao import NeoDao
from business_object.neo import Neo
from datetime import datetime, timedelta

load_dotenv()

"""
API_KEY = os.getenv("NASA_API_KEY")

URL = "https://api.nasa.gov/neo/rest/v1/feed"
params = {
        "start_date": "2026-10-01",
        "end_date": "2026-10-03",
        "api_key": API_KEY  # La variable sécurisée est injectée ici
    }
    
response = requests.get(URL, params=params)
data = response.json()
#pprint(data["near_earth_objects"]["2026-10-03"][1])

neo = Neo(data["near_earth_objects"]["2026-10-03"][1]["id"],
          data["near_earth_objects"]["2026-10-03"][1]["name"],
          data["near_earth_objects"]["2026-10-03"][1]["absolute_magnitude_h"],
          data["near_earth_objects"]["2026-10-03"][1]["estimated_diameter"]["kilometers"]["estimated_diameter_min"],
          data["near_earth_objects"]["2026-10-03"][1]["estimated_diameter"]["kilometers"]["estimated_diameter_max"],
          data["near_earth_objects"]["2026-10-03"][1]["is_potentially_hazardous_asteroid"],
          data["near_earth_objects"]["2026-10-03"][1]["nasa_jpl_url"],
          False,
          datetime(2026, 3, 3))



NeoDao().create(neo)
"""


def import_neo_range(start_date: datetime, end_date: datetime):
    api_key = os.getenv("NASA_API_KEY")
    base_url = "https://api.nasa.gov/neo/rest/v1/feed"

    neo_dao = NeoDao()

    current_start = start_date

    while current_start < end_date:
        current_end = min(
            current_start + timedelta(days=7), end_date
        )  # the seven days allowed by neowsapp

        params = {
            "start_date": current_start.strftime("%Y-%m-%d"),
            "end_date": current_end.strftime("%Y-%m-%d"),
            "api_key": api_key,
        }

        print(f"Importation from {params['start_date']} to {params['end_date']}")

        response = requests.get(base_url, params=params)

        if response.status_code == 429:
            print("Api limits reached (Rate Limit). 60s break")
            time.sleep(60)
            continue
        elif response.status_code != 200:
            print(f"Erreur API ({response.status_code}) : {response.text}")
            break

        data = response.json()
        near_earth_objects = data.get("near_earth_objects", {})

        for date_str, neo_list in near_earth_objects.items():
            for item in neo_list:
                neo = Neo(
                    item["id"],
                    item["name"],
                    item["absolute_magnitude_h"],
                    item["estimated_diameter"]["kilometers"]["estimated_diameter_min"],
                    item["estimated_diameter"]["kilometers"]["estimated_diameter_max"],
                    item["is_potentially_hazardous_asteroid"],
                    item["nasa_jpl_url"],
                    False,
                    datetime.strptime(date_str, "%Y-%m-%d"),
                )

                neo_dao.create(neo)

        current_start = current_end + timedelta(days=1)

        time.sleep(0.2)  # to let some time between two imports

    print("Importation over 3 years done")


if __name__ == "__main__":
    today = datetime.today()
    # 2 years before (365 * 2) 1 after (365)
    start = today - timedelta(days=730)
    end = today + timedelta(days=365)

    import_neo_range(start, end)
