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
        first_arg: str | None = None,
        name: str | None = None,
        absolute_magnitude: float | None = None,
        diameter_min: float | None = None,
        diameter_max: float | None = None,
        hazardous: bool = False,
        url_nasa: str | None = None,
        origin: str = "USER",
        date_update: datetime | str | None = None,
        neo_id: int | None = None,
        nasa_id: str | None = None,
    ) -> Neo | None:
        """Creates a new NEO in the system.

        Supports both positional signatures:
          - create(name, absolute_magnitude, ...)
          - create(nasa_id, name, absolute_magnitude, ...)
          - create(name="...", ...)
        """
        if name is not None:
            resolved_name = name
            resolved_nasa_id = first_arg if first_arg is not None else nasa_id
        else:
            resolved_name = first_arg
            resolved_nasa_id = nasa_id

        if not resolved_name or not str(resolved_name).strip():
            raise ValueError("NEO name cannot be empty")

        if isinstance(date_update, str):
            try:
                resolved_date = datetime.fromisoformat(date_update)
            except Exception:
                resolved_date = datetime.now()
        elif isinstance(date_update, datetime):
            resolved_date = date_update
        else:
            resolved_date = datetime.now()

        new_neo = Neo(
            nasa_id=resolved_nasa_id,
            name=str(resolved_name).strip(),
            absolute_magnitude=float(absolute_magnitude) if absolute_magnitude is not None else None,
            diameter_min=float(diameter_min) if diameter_min is not None else None,
            diameter_max=float(diameter_max) if diameter_max is not None else None,
            hazardous=bool(hazardous),
            url_nasa=url_nasa,
            origin=origin,
            date_update=resolved_date,
            neo_id=neo_id,
        )

        success = self._neo_dao.create(new_neo)
        return new_neo if success else None

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
