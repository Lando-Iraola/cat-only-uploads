from datetime import datetime

from pydantic import BaseModel


class Cat(BaseModel):
    timestamp: datetime
    is_cat: False
    cat_url: str

