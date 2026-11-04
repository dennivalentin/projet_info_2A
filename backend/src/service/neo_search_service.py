# service/neo_service.py

from dao.neo_dao import NeoDao
from utils.log_utils import log


class NeoService:

    @log
    def search_neos(self, name=None, neo_id=None, diameter_min_m=None, diameter_max_m=None,
                    hazardous=None, next_approach_from=None, next_approach_to=None,
                    sort_by="name", order="asc", limit=50, offset=0) -> list[dict]:
        if diameter_min_m is not None and diameter_max_m is not None \
                and diameter_min_m > diameter_max_m:
            raise ValueError("diameter_min_m ne peut pas dépasser diameter_max_m")
        if next_approach_from and next_approach_to and next_approach_from > next_approach_to:
            raise ValueError("next_approach_from doit précéder next_approach_to")

        # l'API parle en mètres (plus naturel), ta base stocke des km
        to_km = lambda m: None if m is None else m / 1000

        return NeoDao().search(
            name=name, neo_id=neo_id,
            diameter_min_km=to_km(diameter_min_m), diameter_max_km=to_km(diameter_max_m),
            hazardous=hazardous,
            next_approach_from=next_approach_from, next_approach_to=next_approach_to,
            sort_by=sort_by, order=order, limit=limit, offset=offset,
        )