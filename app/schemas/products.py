from pydantic import BaseModel


class ProductSchema(BaseModel):
    name: str
    description: str
    price: float
    image_url: str
    stock: int
    category_id: int
    rating: float = 0.0
    is_active: bool = True