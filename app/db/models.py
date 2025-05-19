from sqlmodel import SQLModel, Field

class Country(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    url: str