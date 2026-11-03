from fastapi import APIRouter, HTTPException, Query, status

from schema.neosearch import (
    NeoCreateRequest,
    NeoDetailModel,
    NeoModel,
    NeoSearchCriteria,
)
from service.neo_service import NeoService
from utils.log_utils import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/search",
    response_model=list[NeoModel],
    summary="Search Near-Earth Objects",
    description="Search for NEOs matching criteria such as name, size, hazard flag, and close approaches.",
)
def search_neos(criteria: NeoSearchCriteria) -> list[NeoModel]:
    """Search NEOs using multiple filter criteria."""
    try:
        service = NeoService()
        criteria_dict = criteria.model_dump(exclude_none=True)
        neos = service.search(criteria_dict)
        return [NeoModel(**neo.to_dict()) for neo in neos]
    except Exception as e:
        logger.error(f"Error in search_neos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute search: {str(e)}",
        )


@router.get(
    "/{neo_id}",
    response_model=NeoDetailModel,
    summary="Get NEO details and approaches",
    description="Retrieve full details for a specific NEO, including all historical and upcoming close approaches.",
)
def get_neo_detail(neo_id: int) -> NeoDetailModel:
    """Get full details of a single NEO."""
    service = NeoService()
    details = service.get_neo_details(neo_id)
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NEO with ID {neo_id} not found",
        )
    return NeoDetailModel(**details)


@router.post(
    "",
    response_model=NeoModel,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user-observed NEO",
    description="Create an amateur-observed NEO with origin 'USER'.",
)
def create_neo(neo_in: NeoCreateRequest) -> NeoModel:
    """Submit a newly observed NEO."""
    try:
        service = NeoService()
        created = service.create(
            name=neo_in.name,
            absolute_magnitude=neo_in.absolute_magnitude,
            diameter_min=neo_in.diameter_min,
            diameter_max=neo_in.diameter_max,
            hazardous=neo_in.hazardous,
        )
        if not created:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to create NEO. Please check input values.",
            )
        return NeoModel(**created.to_dict())
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve),
        )
    except Exception as e:
        logger.error(f"Error creating NEO: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create NEO: {str(e)}",
        )


@router.get(
    "",
    response_model=list[NeoModel],
    summary="List Near-Earth Objects",
    description="List NEOs with pagination support.",
)
def list_neos(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[NeoModel]:
    """List NEOs paginated."""
    try:
        service = NeoService()
        neos = service.list_all(limit=limit, offset=offset)
        return [NeoModel(**neo.to_dict()) for neo in neos]
    except Exception as e:
        logger.error(f"Error listing NEOs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list NEOs: {str(e)}",
        )
