from pydantic import BaseModel

class Country(BaseModel):
    name: str
    id: int
    url: str