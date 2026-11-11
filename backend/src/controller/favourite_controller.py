from fastapi import APIRouter, Depends, HTTPException

from schema.favourite_model import FavouriteCreateModel
from service.favourite_service import FavouriteService
from utils.log_utils import get_logger
from utils.security import check_same_user, get_current_user

router = APIRouter(prefix="/favourites", tags=["Favourites"])
logger = get_logger(__name__)


@router.post("/", status_code=201)
def add_favourite(param: FavouriteCreateModel, current_user=Depends(get_current_user)):
    """Add a Neo to the user's favourite"""
    check_same_user(current_user, param.user_id)
    service = FavouriteService()
    logger.info(f"Adding favourite: neo_id={param.neo_id} for user_id={param.user_id}")
    res = service.add_favourite(neo_id=param.neo_id, user_id=param.user_id)
    if not res:
        raise HTTPException(status_code=400, detail="Impossible to add it as favourite")
    return {"message": "Favourite added"}


@router.delete("/{user_id}/{neo_id}")
def remove_favourite(user_id: int, neo_id: int, current_user=Depends(get_current_user)):
    """Delete a Neo from the favourite"""
    check_same_user(current_user, user_id)
    service = FavouriteService()
    logger.info(f"Removing favourite: neo_id={neo_id} for user_id={user_id}")
    res = service.remove_favourite(neo_id=neo_id, user_id=user_id)
    if not res:
        raise HTTPException(status_code=404, detail="No favourite deleted")
    return {"message": "Favorite deleted"}


@router.get("/user/{user_id}")
def list_favourites_by_user(user_id: int, current_user=Depends(get_current_user)):
    """List of all the favourite of a user"""
    check_same_user(current_user, user_id)
    service = FavouriteService()
    logger.info(f"Listing favourites for user_id={user_id}")
    favourites = service.list_all_favourite_by_user(user_id)
    return [neo.to_dict() for neo in favourites]


@router.get("/user/{user_id}/approaches")
def get_favourite_approaches(user_id: int, current_user=Depends(get_current_user)):
    """Get the favourite approaches of a user"""
    check_same_user(current_user, user_id)
    service = FavouriteService()
    logger.info(f"Fetching approaches for user_id={user_id}")
    approaches_dict = service.approches_favourite(user_id)
    return {
        neo_id: [approach.to_dict() for approach in approaches]
        for neo_id, approaches in approaches_dict.items()
    }


@router.get("/user/{user_id}/neo/{neo_id}/graph")
def get_favourite_graph(user_id: int, neo_id: int, current_user=Depends(get_current_user)):
    """Gives the picture of a graph"""
    check_same_user(current_user, user_id)
    service = FavouriteService()
    logger.info(f"Generating graph for neo_id={neo_id} of user_id={user_id}")
    try:
        image_base64 = service.graph_favourite(user_id=user_id, neo_id=neo_id)
        return {"image": image_base64}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except KeyError:
        raise HTTPException(status_code=404, detail="This Neo is not in your favourite")
