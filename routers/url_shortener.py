from fastapi import APIRouter, status, Depends

from database import database, url_table
from models.url_shortener import Url, UrlIn

router = APIRouter()


@router.get("/{short_code}", status_code=status.HTTP_200_OK)
async def create_post(url: Url = Depends(Url.get_url_from_short_code)):
    return url["url"]


@router.post("/shorten", response_model=Url, status_code=status.HTTP_201_CREATED)
async def create_post(url_in: UrlIn):
    record = await Url.get_url_from_url(url_in.url)

    if record is not None:
        return {**record, "short_url": f"https://s.com/{record.short_code}"}

    short_code = await Url.generate_unique_short_code(url_in.url)

    data = {**url_in.model_dump(), "short_code": short_code}
    query = url_table.insert().values(data)
    await database.execute(query)
    return {**data, "short_url": f"https://s.com/{short_code}"}
