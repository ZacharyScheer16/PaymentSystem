"""Shared SQLAlchemy declarative base. Every ORM model in models/ inherits from this."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
