from pydantic import BaseModel


class FavouriteCreateModel(BaseModel):
    """Payload to add a NEO to the favourites of a user."""

    user_id: int
    neo_id: int
