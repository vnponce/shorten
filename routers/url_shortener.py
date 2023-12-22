from fastapi import APIRouter, status

from database import database, url_table
from libs.url import generate_url
from models.url_shortener import Url, UrlIn

router = APIRouter()

@router.post("/url-shortener", response_model=Url, status_code=status.HTTP_201_CREATED)
async def create_post(url_in: UrlIn):
    data = {**url_in.model_dump(), "short_url": generate_url(url_in.url)}
    query = url_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}
