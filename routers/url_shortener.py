from fastapi import APIRouter, status, Depends

from models.url_shortener import Url

router = APIRouter()


@router.get("/{short_code}", status_code=status.HTTP_200_OK)
async def get_url(url: Url = Depends(Url.by_shortcode)) -> str:
    return url["url"]


@router.post("/shorten", response_model=Url, status_code=status.HTTP_201_CREATED)
async def create_url(url: Url = Depends(Url.find_or_create)) -> Url:
    return url
