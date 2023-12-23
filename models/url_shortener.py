from pydantic import BaseModel, ConfigDict, computed_field

from database import url_table, database
from libs.url import generate_url


class UrlIn(BaseModel):
    url: str


class Url(UrlIn):
    # to read a sqlAlchemy object with dot notation
    # instead of Object['a'] -> Object.a
    model_config = ConfigDict(from_attributes=True)

    short_code: str

    @computed_field
    @property
    def short_url(self) -> str:
        return "https://s.com/" + self.short_code

    @classmethod
    async def generate_unique_short_code(cls, url: str):
        short_code = generate_url(url)
        starting_index = 1
        while True:
            query = url_table.select().where(url_table.c.short_code == short_code)
            record = await database.fetch_one(query)
            if record is None:
                break
            starting_index += 1
            short_code = generate_url(url, size=7, starting_index=starting_index)

        return short_code
