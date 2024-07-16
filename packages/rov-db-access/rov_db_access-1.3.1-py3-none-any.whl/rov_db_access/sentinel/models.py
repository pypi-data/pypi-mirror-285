from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from geoalchemy2 import Geometry


class Base(DeclarativeBase):
    """Base Class of the model"""


class Tiles(Base):
    """Tile model"""
    __tablename__ = "tiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    geom: Mapped[Geometry] = mapped_column(Geometry("POLYGON", srid=4326))
    required: Mapped[bool]
