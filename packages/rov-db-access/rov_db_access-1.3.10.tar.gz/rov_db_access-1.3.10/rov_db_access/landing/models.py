from datetime import datetime
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    """Base Class of the model"""


class Articles(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    content: Mapped[str]
    location: Mapped[Optional[Geometry]] = mapped_column(Geometry("POINT", srid=4326))
    zoom: Mapped[float] = mapped_column(server_default="1")
    date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"Articles (id={self.id!r},  title={self.title!r})"


class Members(Base):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    profession: Mapped[str]
    description: Mapped[Optional[str]]
    photo_url: Mapped[str]
    linkedin: Mapped[Optional[str]]
    github: Mapped[Optional[str]]
    order: Mapped[int] = mapped_column(server_default="999")
    job: Mapped[str]

    def __repr__(self) -> str:
        return f"Members (id={self.id!r},  name={self.name!r})"


class Newsletter(Base):
    __tablename__ = "newsletter"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    content: Mapped[str]
    author: Mapped[str]
    is_published: Mapped[bool] = mapped_column(server_default='False')
    date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"Newsletter (id={self.id!r},  title={self.title!r})"


class Subscribers(Base):
    __tablename__ = "subscribers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"Subscribers (id={self.id!r},  name={self.name!r})"