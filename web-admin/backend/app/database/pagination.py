from __future__ import annotations

from math import ceil

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session


def paginate_scalars(session: Session, statement: Select, page: int, per_page: int) -> dict:
    page = max(page, 1)
    per_page = max(per_page, 1)

    total = session.execute(
        select(func.count()).select_from(statement.order_by(None).subquery())
    ).scalar_one()

    offset = (page - 1) * per_page
    items = session.execute(statement.limit(per_page).offset(offset)).scalars().all()
    pages = ceil(total / per_page) if total else 0

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }


__all__ = ["paginate_scalars"]
