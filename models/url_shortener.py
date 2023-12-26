from pydantic import BaseModel, ConfigDict, computed_field, AnyUrl, AfterValidator
from typing_extensions import Annotated

from database import url_table, database
from libs.url import generate_url, DEFAULT_SHORT_CODE_SIZE, traverse_md5

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
    async def generate_unique_short_code(cls, url: str) -> str:
        md5_for_url = generate_url(url, size=32)
        short_code = md5_for_url[:DEFAULT_SHORT_CODE_SIZE]
        starting_index = 1

        while True:
            record = await cls.by_shortcode(short_code)

            if record is None:
                break
            short_code = traverse_md5(starting_index, md5_for_url)

        return short_code

    @classmethod
    async def by_shortcode(cls, short_code: str):
        query = url_table.select().where(url_table.c.short_code == short_code)
        return await database.fetch_one(query)

    @classmethod
    async def by_url(cls, url: str):
        query = url_table.select().where(url_table.c.url == url)
        return await database.fetch_one(query)

    @classmethod
    async def find_or_create(cls, url_in: UrlIn):
        record = await cls.by_url(url_in.url)

        if record is not None:
            return {**record, "short_url": cls.short_url}

        short_code = await cls.generate_unique_short_code(url_in.url)

        data = {**url_in.model_dump(), "short_code": short_code}
        query = url_table.insert().values(data)
        await database.execute(query)
        return {**data, "short_url": cls.short_url}
