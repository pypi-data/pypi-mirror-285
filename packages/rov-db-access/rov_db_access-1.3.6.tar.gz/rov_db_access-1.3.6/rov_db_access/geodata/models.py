from geoalchemy2 import Geometry
from sqlalchemy import JSON
from typing import Optional
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    """Base Class of the model"""


class RiskHazard():
    id: Mapped[int] = mapped_column(primary_key=True)
    geom: Mapped[Geometry] = mapped_column(Geometry("POLYGON", srid=4326))
    data: Mapped[Optional[JSON]] = mapped_column(type_=JSON)
    risk_weight: Mapped[float] = mapped_column(server_default="0")


class FloodHazard(RiskHazard, Base):
    __tablename__ = "flood:hazard"
    __table_args__ = {"schema": "risks"}

    def __repr__(self) -> str:
        return f"FloodHazard (id={self.id!r}, risk_weight={self.risk_weight!r}"


class RMHazard(RiskHazard, Base):
    __tablename__ = "rm:hazard"
    __table_args__ = {"schema": "risks"}

    def __repr__(self) -> str:
        return f"RMHazard (id={self.id!r}, risk_weight={self.risk_weight!r}"


class TsunamiHazard(RiskHazard, Base):
    __tablename__ = "tsunami:hazard"
    __table_args__ = {"schema": "risks"}

    def __repr__(self) -> str:
        return f"TsunamiHazard (id={self.id!r}, risk_weight={self.risk_weight!r}"


class VolcanicHazard(RiskHazard, Base):
    __tablename__ = "volcanic:hazard"
    __table_args__ = {"schema": "risks"}

    def __repr__(self) -> str:
        return f"VolcanicHazard (id={self.id!r}, risk_weight={self.risk_weight!r}"


class VolcanicHazardPyroclast(RiskHazard, Base):
    __tablename__ = "volcanic:hazard_pyroclast"
    __table_args__ = {"schema": "risks"}

    def __repr__(self) -> str:
        return f"VolcanicHazardPyroclast (id={self.id!r}, risk_weight={self.risk_weight!r}"


class WildfireHazard(RiskHazard, Base):
    __tablename__ = "wildfire:hazard"
    __table_args__ = {"schema": "risks"}

    def __repr__(self) -> str:
        return f"WildfireHazard (id={self.id!r}, risk_weight={self.risk_weight!r}"

