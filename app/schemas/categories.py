from pydantic import BaseModel


class CategorySchema(BaseModel):
    name: str
    parent_id: int | None