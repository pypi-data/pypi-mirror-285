from geoalchemy2 import Geometry
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    """Base Class of the model"""


class BuildingsNico(Base):
    __tablename__ = "pompeya_buildings_nico_merged"
    id: Mapped[int] = mapped_column(primary_key=True)
    geom: Mapped[Geometry] = mapped_column(Geometry("MULTIPOLYGON", srid=32719))

    def __repr__(self) -> str:
        return f"Buildings_Nico (id={self.id!r},  geom={self.geom!r})"


class BuildingsPost(Base):
    __tablename__ = "buildings_instances_post_pompeya"
    id: Mapped[int] = mapped_column(primary_key=True)
    geom: Mapped[Geometry] = mapped_column(Geometry("POLYGON", srid=4326))

    def __repr__(self) -> str:
        return f"Buildings_Post (id={self.id!r},  geom={self.geom!r})"