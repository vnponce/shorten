from pydantic import BaseModel, ConfigDict, computed_field, AnyUrl, AfterValidator
from typing_extensions import Annotated

from database import url_table, database
from libs.url import generate_url, DEFAULT_SHORT_CODE_SIZE, move_one_place_to_the_right

# This is a little hack since pydantic sends a "pydantic_core.Url" object instead of a string, the database is
# expecting to get a string that triggers a Sql not supported type error Taken from this comment
# [https://github.com/pydantic/pydantic/discussions/6395#discussioncomment-7159870] from discussion
# " How can I integrate pydantic v2 URLs in code? #6395 "
UrlString = Annotated[AnyUrl, AfterValidator(lambda v: str(v))]


class UrlIn(BaseModel):
    url: UrlString


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
        full_short_code = generate_url(url, size=32)
        short_code = full_short_code[:DEFAULT_SHORT_CODE_SIZE]
        starting_index = 1

        while True:
            query = url_table.select().where(url_table.c.short_code == short_code)
            record = await database.fetch_one(query)
            if record is None:
                break
            short_code = move_one_place_to_the_right(starting_index, full_short_code)

        return short_code
