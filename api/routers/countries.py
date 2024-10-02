from fastapi import APIRouter, Depends, Query
from models import Country
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy import or_
import math

router = APIRouter()


@router.get("/")
async def get_countries(
    db: Session = Depends(get_db),
    skip: int = Query(default=1, ge=1),
    limit: int = 10,
    search: str = "",
):
    offset = (skip - 1) * limit
    query = (
        db.query(Country)
        .filter(
            or_(
                Country.country.ilike(f"%{search}%"),
                Country.short_code.ilike(f"%{search}%"),
            )
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    total_count = (
        db.query(Country)
        .filter(
            or_(
                Country.country.ilike(f"%{search}%"),
                Country.short_code.ilike(f"%{search}%"),
            )
        )
        .count()
    )
    pages = math.ceil(total_count / limit)
    return {"pages": pages, "data": query}
