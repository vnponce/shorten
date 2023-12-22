from pydantic import BaseModel, ConfigDict


class UrlIn(BaseModel):
    url: str


class Url(UrlIn):
    # to read a sqlAlchemy object with dot notation
    # instead of Object['a'] -> Object.a
    model_config = ConfigDict(from_attributes=True)

    id: int
    short_url: str
