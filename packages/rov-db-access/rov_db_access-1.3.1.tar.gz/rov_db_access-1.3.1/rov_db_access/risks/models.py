from datetime import datetime
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rov_db_access.authentication.models import User, Base as GisBase


class UserResultsHistory(GisBase):
    __tablename__ = "user_results_history"
    __table_args__ = {"schema": "risks"}
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("admin.user.id"))
    user: Mapped["User"] = relationship()
    name: Mapped[str]
    address: Mapped[str]
    location: Mapped[Geometry] = mapped_column(Geometry("POINT", srid=4326))
    data: Mapped[Optional[JSON]] = mapped_column(type_=JSON)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    saved: Mapped[Optional[bool]] = mapped_column(server_default="false")

    def __repr__(self) -> str:
        return f"UserResultsHistory (id={self.id!r}, name={self.name!r}, address={self.address!r} user_id={self.user_id!r}, location={self.location!r}, data={self.data!r}, created_at={self.created_at!r})"
