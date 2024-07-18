from geoalchemy2 import Geometry
from typing import List
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy import JSON

from rov_db_access.authentication.models import Organization, User, Base


class Image(Base):
    __tablename__ = "image"
    __table_args__ = {"schema": "gis"}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]]
    url: Mapped[str]
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())

    data: Mapped[Optional[JSON]] = mapped_column(type_=JSON)

    user_id: Mapped[int] = mapped_column(ForeignKey("admin.user.id"))
    user: Mapped["User"] = relationship()

    organization_id: Mapped[int] = mapped_column(ForeignKey("admin.organization.id"))
    organization: Mapped["Organization"] = relationship()

    bbox: Mapped[Geometry] = mapped_column(Geometry("POLYGON", srid=4326))
    footprint: Mapped[Optional[Geometry]] = mapped_column(Geometry("POLYGON", srid=4326))

    def __repr__(self) -> str:
        return f"Image (id={self.id!r}, name={self.name!r}, url={self.url!r}, user_id={self.user_id!r}, organization_id={self.organization_id!r})"


class InferenceModel(Base):
    __tablename__ = "inference_model"
    __table_args__ = {"schema": "gis"}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    title: Mapped[str]
    description: Mapped[str]
    img_url: Mapped[str]
    price: Mapped[float] = mapped_column(server_default='0')
    type: Mapped[str] = mapped_column(server_default='model')
    min_resolution: Mapped[float]
    config: Mapped[Optional[JSON]] = mapped_column(type_=JSON)
    current_version: Mapped[str] = mapped_column(server_default="v1")

    def __repr__(self) -> str:
        return f"InferenceModel (id={self.id!r}, name={self.name!r}, price={self.price!r}, config={self.config!r})"


class Mosaic(Base):
    __tablename__ = "mosaic"
    __table_args__ = {"schema": "gis"}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[Optional[str]]
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    coverage_store: Mapped[str] = mapped_column(unique=True)

    organization_id: Mapped[int] = mapped_column(ForeignKey("admin.organization.id"))
    organization: Mapped["Organization"] = relationship()

    def __repr__(self) -> str:
        return f"Mosaic (id={self.id!r}, name={self.name!r}, organization_id={self.organization_id!r})"


class Process(Base):
    __tablename__ = "process"
    __table_args__ = {"schema": "gis"}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    status: Mapped[str] = mapped_column(server_default="queued")
    type: Mapped[str] = mapped_column(server_default="on demand")
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    runtime: Mapped[int] = mapped_column(server_default="0")
    area: Mapped[float] = mapped_column(server_default="0")
    cost_estimated: Mapped[float] = mapped_column(server_default="0")
    config: Mapped[Optional[JSON]] = mapped_column(type_=JSON)

    geom: Mapped[Optional[Geometry]] = mapped_column(Geometry("POLYGON", srid=4326))
    mask: Mapped[Optional[Geometry]] = mapped_column(Geometry("POLYGON", srid=4326))

    inference_model_id: Mapped[int] = mapped_column(ForeignKey("gis.inference_model.id"))
    inference_model: Mapped["InferenceModel"] = relationship()

    organization_id: Mapped[int] = mapped_column(ForeignKey("admin.organization.id"))
    organization: Mapped["Organization"] = relationship()

    user_id: Mapped[int] = mapped_column(ForeignKey("admin.user.id"))
    user: Mapped["User"] = relationship()

    runs: Mapped[List["Run"]] = relationship(
       back_populates="process",
       order_by="Run.id",
       cascade="all, delete"
    )

    def __repr__(self) -> str:
        return f"Process(id={self.id!r}, name={self.name!r}, status={self.status!r}, inference_model_id={self.inference_model_id!r}), user_id={self.user_id!r})"


class ResultsRaster(Base):
    __tablename__ = "results_raster"
    __table_args__ = {"schema": "gis"}
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str]
    data: Mapped[Optional[JSON]] = mapped_column(type_=JSON)
    bbox: Mapped[Optional[Geometry]] = mapped_column(Geometry("POLYGON", srid=4326))

    run_data_id: Mapped[int] = mapped_column(ForeignKey("gis.run_data.id", ondelete="CASCADE"))
    run_data: Mapped["RunData"] = relationship(back_populates="results_raster")

    def __repr__(self) -> str:
        return f"ResultsRaster(id={self.id!r}, url={self.url!r}, run_data_id={self.run_data_id!r})"


class ResultsVector(Base):
    __tablename__ = "results_vector"
    __table_args__ = {"schema": "gis"}
    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[Optional[JSON]] = mapped_column(type_=JSON)
    geom: Mapped[Geometry] = mapped_column(Geometry("GEOMETRY", srid=4326))

    run_data_id: Mapped[int] = mapped_column(ForeignKey("gis.run_data.id", ondelete="CASCADE"))
    run_data: Mapped["RunData"] = relationship(back_populates="results_vector")

    def __repr__(self) -> str:
        return f"ResultsVector(id={self.id!r}, data={self.data!r}, geom={self.geom!r}, run_data_id={self.run_data_id!r})"


class Run(Base):
    __tablename__ = "run"
    __table_args__ = {"schema": "gis"}
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(server_default="queued")
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    engine: Mapped[str] = mapped_column(server_default="local")
    runtime: Mapped[int] = mapped_column(server_default="0")
    cost: Mapped[float] = mapped_column(server_default="0")
    inference_model_version: Mapped[str] = mapped_column(server_default="v1")

    input_id: Mapped[int] = mapped_column(ForeignKey("gis.run_data.id", ondelete="CASCADE"), nullable=False)
    input: Mapped["RunData"] = relationship("RunData", foreign_keys=[input_id])

    output_id: Mapped[int] = mapped_column(ForeignKey("gis.run_data.id", ondelete="CASCADE"), nullable=False)
    output: Mapped[Optional["RunData"]] = relationship("RunData", foreign_keys=[output_id])

    inference_model_id: Mapped[int] = mapped_column(ForeignKey("gis.inference_model.id"))
    inference_model: Mapped["InferenceModel"] = relationship()

    process_id: Mapped[int] = mapped_column(ForeignKey("gis.process.id", ondelete="CASCADE"))
    process: Mapped["Process"] = relationship()

    def __repr__(self) -> str:
        return f"Run(id={self.id!r}, status={self.status!r}, process_id={self.process_id!r}) inference_model_id={self.inference_model_id!r}, input_id={self.input_id}, output_id={self.output_id})"

    def serialize(self):
        return {
            "id": self.id,
            "status": self.status,
            "created_at": self.created_at,
            "finished_at": self.finished_at,
            "engine": self.engine,
            "runtime": self.runtime,
            "cost": self.cost,
            "input_id": self.input_id,
            "output_id": self.output_id,
            "inference_model_id": self.inference_model_id,
            "process_id": self.process_id
        }


class RunData(Base):
    __tablename__ = "run_data"
    __table_args__ = {"schema": "gis"}
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(server_default='undefined')
    status: Mapped[str] = mapped_column(server_default='ready')
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())

    data: Mapped[Optional[JSON]] = mapped_column(type_=JSON)

    user_id: Mapped[int] = mapped_column(ForeignKey("admin.user.id"))
    user: Mapped["User"] = relationship()

    organization_id: Mapped[int] = mapped_column(ForeignKey("admin.organization.id"))
    organization: Mapped["Organization"] = relationship()

    used_by: Mapped[List["Run"]] = relationship(
        back_populates="input",
        foreign_keys="Run.input_id"
    )

    origin_run: Mapped[Optional["Run"]] = relationship(
        back_populates="output",
        foreign_keys="Run.output_id"
    )

    results_vector: Mapped[List["ResultsVector"]] = relationship(
       back_populates="run_data",
       order_by="ResultsVector.id",
       cascade="all, delete"
    )

    results_raster: Mapped[List["ResultsRaster"]] = relationship(
        back_populates="run_data",
        order_by="ResultsRaster.id",
        cascade="all, delete"
    )

    def __repr__(self) -> str:
        return f"RunData (id={self.id!r}, user_id={self.user_id!r}, status={self.status}, data={self.data}"

    def serialize(self):
        return {
            "id": self.id,
            "type": self.type,
            "status": self.status,
            "created_at": self.created_at,
            "data": self.data,
            "user_id": self.user_id,
            "organization_id": self.organization_id
        }

# class GeomTest(Base):
#     __tablename__ = "geom_test"
#     __table_args__ = {"schema": "gis"}
#     id: Mapped[int] = mapped_column(primary_key=True)
#     geom: Mapped[Geometry] = mapped_column(Geometry("GEOMETRY", srid=4326))

#     def __repr__(self) -> str:
#         return f"GeomTest (id={self.id!r}, geom={self.geom!r})"
