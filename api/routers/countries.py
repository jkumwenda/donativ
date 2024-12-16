import math
from sqlalchemy import or_
from core.database import get_db
from models.models import Country
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query


router = APIRouter()


@router.get("/")
async def get_countries(
    db: Session = Depends(get_db),
    skip: int = Query(default=1, ge=1),
    limit: int = 10,
    search: str = "",
):
    search_filter = or_(
        Country.country.ilike(f"%{search}%"),
        Country.short_code.ilike(f"%{search}%"),
    )

    countries_query = db.query(Country).filter(search_filter)

    total_count = countries_query.count()
    countries = countries_query.offset(
        (skip - 1) * limit).limit(limit).all()

    pages = math.ceil(total_count / limit)
    return {"pages": pages, "data": countries}
