from .base import db


def get_session():
    return db.session


def remove_session():
    db.session.remove()


__all__ = ["get_session", "remove_session"]