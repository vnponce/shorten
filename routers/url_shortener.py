from fastapi import APIRouter, status

from database import database, url_table
from libs.url import generate_url, to_shortcode
from models.url_shortener import Url, UrlIn

router = APIRouter()


@router.get("/url-shortener/{short_code}", status_code=status.HTTP_200_OK)
async def create_post(short_code: str):
    query = url_table.select().where(url_table.c.short_code == short_code)
    record = await database.fetch_one(query)
    return record["url"]


@router.post("/url-shortener", response_model=Url, status_code=status.HTTP_201_CREATED)
async def create_post(url_in: UrlIn):
    query = url_table.select().where(url_table.c.url == url_in.url)
    record = await database.fetch_one(query)

    if record is not None:
        return record

    data = {**url_in.model_dump(), "short_code": generate_url(url_in.url)}
    query = url_table.insert().values(data)
    await database.execute(query)
    return {**data}
