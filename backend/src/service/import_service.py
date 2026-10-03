import requests
import os
from dotenv import load_dotenv
from pprint import pprint


load_dotenv()


API_KEY = os.getenv("NASA_API_KEY")

URL = "https://api.nasa.gov/neo/rest/v1/feed"
params = {
        "start_date": "2026-10-01",
        "end_date": "2026-10-03",
        "api_key": API_KEY  # La variable sécurisée est injectée ici
    }
    
response = requests.get(URL, params=params)
data = response.json()
pprint(data["near_earth_objects"]["2026-10-03"][1])



