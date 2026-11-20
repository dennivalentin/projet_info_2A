from datetime import datetime

from business_object.neo import Neo
from dao.approach_dao import ApproachDao
from dao.neo_dao import NeoDao
from utils.log_utils import get_logger, log

logger = get_logger(__name__)


class NeoService:
    """Service handling business logic for Near-Earth Objects (NEOs)."""

    def __init__(self, neo_dao: NeoDao | None = None, approach_dao: ApproachDao | None = None):
        self._neo_dao = neo_dao or NeoDao()
        self._approach_dao = approach_dao or ApproachDao()

    @log
    def create(
        self,
        name: str,
        absolute_magnitude: float | None = None,
        diameter_min: float | None = None,
        diameter_max: float | None = None,
        hazardous: bool = False,
    ) -> Neo | None:
        """Creates a NEO declared by a user (F4).

        The NEO has the origin 'USER' and no NASA id: the NASA imports never
        overwrite it.

        Args:
            name: Name of the NEO.
            absolute_magnitude: Absolute magnitude (H), if known.
            diameter_min: Estimated minimum diameter in km, if known.
            diameter_max: Estimated maximum diameter in km, if known.
            hazardous: True if the NEO is potentially hazardous.

        Returns:
            The created Neo, or None if the DAO could not save it.

        Raises:
            ValueError: If the name is empty or the diameters are not valid.
        """
        if not name or not name.strip():
            raise ValueError("NEO name cannot be empty")
        for diameter in (diameter_min, diameter_max):
            if diameter is not None and diameter <= 0:
                raise ValueError("A diameter must be positive")
        if diameter_min is not None and diameter_max is not None and diameter_min > diameter_max:
            raise ValueError("The minimum diameter cannot be larger than the maximum diameter")

        new_neo = Neo(
            nasa_id=None,
            name=name.strip(),
            absolute_magnitude=absolute_magnitude,
            diameter_min=diameter_min,
            diameter_max=diameter_max,
            hazardous=hazardous,
            url_nasa=None,
            origin="USER",
            date_update=datetime.now(),
        )

        success = self._neo_dao.create(new_neo)
        if not success:
            return None
        return new_neo

    @log
    def search(self, search_criteria: dict) -> list[Neo]:
        """Search for NEOs matching criteria.

        Args:
            search_criteria: Dictionary containing filter parameters.

        Returns:
            List of matching Neo objects.
        """
        return self._neo_dao.find(search_criteria)

    @log
    def find_by_id(self, neo_id: int) -> Neo | None:
        """Retrieve a NEO by its internal ID.

        Args:
            neo_id: Internal ID.

        Returns:
            Neo if found, None otherwise.
        """
        return self._neo_dao.find_by_id(neo_id)

    @log
    def list_all(self, limit: int = 100, offset: int = 0) -> list[Neo]:
        """Retrieve all NEOs with pagination.

        Args:
            limit: Maximum items to return.
            offset: Items to skip.

        Returns:
            List of Neo objects.
        """
        return self._neo_dao.find_all(limit=limit, offset=offset)

    @log
    def get_neo_details(self, neo_id: int) -> dict | None:
        """Retrieve full details of a NEO along with its close approaches.

        Args:
            neo_id: Internal ID of the NEO.

        Returns:
            Dictionary containing NEO details and close approaches list, or None if not found.
        """
        neo = self._neo_dao.find_by_id(neo_id)
        if not neo:
            return None

        approaches = self._approach_dao.find_by_neo_id(neo_id)

        data = neo.to_dict()
        data["approaches"] = [approach.to_dict() for approach in approaches]
        return data
