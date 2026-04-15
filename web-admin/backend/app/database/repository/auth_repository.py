from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..entity.models import TokenBlocklist


def get_token_block(session: Session, jti: str) -> TokenBlocklist | None:
    return session.execute(select(TokenBlocklist).where(TokenBlocklist.jti == jti)).scalar_one_or_none()


def add_token_block(session: Session, jti: str) -> TokenBlocklist:
    token = TokenBlocklist(jti=jti)
    session.add(token)
    return token


__all__ = ["add_token_block", "get_token_block"]
