from pydantic import BaseModel


class FavouriteCreateModel(BaseModel):
    user_id: int
    neo_id: int
