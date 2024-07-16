from geoalchemy2 import Geometry
from sqlalchemy import String, ForeignKey, DateTime, func
from typing import List
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from rov_db_access.authentication.models import User, Base


class AssociationBatchLayer(Base):
    __tablename__ = "association_batch_layer"
    __table_args__ = {"schema": "label_studio"}
    batch_id: Mapped[int] = mapped_column(ForeignKey("label_studio.batch.id"), primary_key=True)
    layer_id: Mapped[int] = mapped_column(ForeignKey("label_studio.layer.id"), primary_key=True)

    # association between Popject -> Association -> Type
    # project_associations: Mapped[List["AssociationProjectType"]] = relationship(back_populates='type')

    # many-to-many relationship to Type, bypassing the `Association` class
    # projects: Mapped[List["Project"]] = relationship(
    #     secondary="association_project_type",
    #     back_populates="types"
    # )

    def __repr__(self) -> str:
        return f"AssociationBatchLayer(batch_id={self.batch_id!r}, layer_id={self.layer_id!r})"


class AssociationProjectType(Base):
    __tablename__ = "association_project_type"
    __table_args__ = {"schema": "label_studio"}
    project_id: Mapped[int] = mapped_column(ForeignKey("label_studio.project.id"), primary_key=True)
    type_id: Mapped[int] = mapped_column(ForeignKey("label_studio.type.id"), primary_key=True)

    # project: Mapped["Project"] = relationship(back_populates="types_associations")
    ##type: Mapped["Type"] = relationship(back_populates="project_associations")

    def __repr__(self) -> str:
        return f"AssociationProjectType(project_id={self.project_id!r}, type_id={self.type_id!r})"


class AssociationProjectUserRole(Base):
    __tablename__ = "association_project_user_role"
    __table_args__ = {"schema": "label_studio"}
    user_id: Mapped[int] = mapped_column(ForeignKey("admin.user.id"), primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("label_studio.project.id"), primary_key=True)
    role_rl_id: Mapped[int] = mapped_column(ForeignKey("label_studio.role_rl.id"), primary_key=True)
    user: Mapped["User"] = relationship()
    project: Mapped["Project"] = relationship(back_populates="user_role_associations")
    role_rl: Mapped["RoleRL"] = relationship()

    def __repr__(self) -> str:
        return f"AssociationProjectUserRole(user_id={self.user_id!r}, project_id={self.project_id!r}, role_rl_id={self.role_rl_id!r}, user={self.user!r}, project={self.project!r}, role_rl={self.role_rl!r})"


class AssociationTaskImage(Base):
    __tablename__ = "association_task_image"
    __table_args__ = {"schema": "label_studio"}
    task_id: Mapped[int] = mapped_column(ForeignKey("label_studio.task.id"), primary_key=True)
    image_rl_id: Mapped[int] = mapped_column(ForeignKey("label_studio.image_rl.id"), primary_key=True)

    def __repr__(self) -> str:
        return f"AssociationTaskImage(task_id={self.task_id!r}, image_rl_id={self.image_rl_id!r})"


class Batch(Base):
    __tablename__ = "batch"
    __table_args__ = {"schema": "label_studio"}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    project_id: Mapped[int] = mapped_column(ForeignKey("label_studio.project.id"))
    project: Mapped["Project"] = relationship(back_populates="batches")

    layers: Mapped[List["Layer"]] = relationship(
        secondary="label_studio.association_batch_layer"
    )
    tasks: Mapped[List["Task"]] = relationship(
        back_populates='batch',
        order_by="Task.id"
    )

    def __repr__(self) -> str:
        return f"Batch(id={self.id!r}, name={self.name!r}, layers={self.layers!r}, created_at={self.created_at!r}, project={self.project!r}, tasks={self.tasks!r})"


class ImageRL(Base):
    __tablename__ = "image_rl"
    __table_args__ = {"schema": "label_studio"}
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str]
    in_storage: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"ImageRL(id={self.id!r}, url={self.url!r}, in_storage={self.in_storage!r})"


class Label(Base):
    __tablename__ = "label"
    __table_args__ = {"schema": "label_studio"}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]]
    time: Mapped[Optional[int]]
    status: Mapped[str]
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    geom = mapped_column(Geometry("POLYGON", srid=4326))

    task_id: Mapped[int] = mapped_column(ForeignKey("label_studio.task.id"))
    task: Mapped["Task"] = relationship(back_populates="labels")

    user_id: Mapped[int] = mapped_column(ForeignKey("admin.user.id"))
    user: Mapped["User"] = relationship()

    type_id: Mapped[int] = mapped_column(ForeignKey("label_studio.type.id"))
    type: Mapped["Type"] = relationship()

    def __repr__(self) -> str:
        return f"Label(id={self.id!r}, name={self.name!r}, time={self.time!r}, status={self.status!r}, created_at={self.created_at!r}, modified_at={self.modified_at!r}, geom={self.geom!r}, task={self.task!r}, user={self.user!r}, type={self.type!r})"


class Layer(Base):
    __tablename__ = "layer"
    __table_args__ = {"schema": "label_studio"}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    url: Mapped[str]

    def __repr__(self) -> str:
        return f"Layer(id={self.id!r}, name={self.name!r}, url={self.url!r})"


class Project(Base):
    __tablename__ = "project"
    __table_args__ = {"schema": "label_studio"}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    # association between Popject -> Association -> Type
    # types_associations: Mapped[List["AssociationProjectType"]] = relationship(back_populates='project')

    # many-to-many relationship to Type, bypassing the `Association` class
    types: Mapped[List["Type"]] = relationship(
        secondary="label_studio.association_project_type",
        order_by="Type.name"
    )
    user_role_associations: Mapped[List["AssociationProjectUserRole"]] = relationship(
        back_populates='project'
    )
    batches: Mapped[List["Batch"]] = relationship(
        back_populates='project',
        order_by='Batch.id'
    )

    def __repr__(self) -> str:
        return f"Project(id={self.id!r}, name={self.name!r}, types={self.types!r}, batches={self.batches!r})"


class RoleRL(Base):
    __tablename__ = "role_rl"
    __table_args__ = {"schema": "label_studio"}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    def __repr__(self) -> str:
        return f"RoleRL(id={self.id!r}, name={self.name!r})"


class Task(Base):
    __tablename__ = "task"
    __table_args__ = {"schema": "label_studio"}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    time: Mapped[Optional[int]]
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    status: Mapped[str]
    bbox: Mapped[Optional[Geometry]] = mapped_column(Geometry("POLYGON", srid=4326))
    comments: Mapped[Optional[str]]
    is_valid: Mapped[bool] = mapped_column(server_default='True')

    batch_id: Mapped[int] = mapped_column(ForeignKey("label_studio.batch.id"))
    batch: Mapped["Batch"] = relationship(back_populates="tasks")

    images_rl: Mapped[List[ImageRL]] = relationship(
        secondary="label_studio.association_task_image",
        order_by="ImageRL.id"
    )

    labels: Mapped[List["Label"]] = relationship(
        back_populates="task",
        order_by="Label.id"
    )

    def __repr__(self) -> str:
        return f"Task(id={self.id!r}, name={self.name!r}, time={self.time!r}, created_at={self.created_at!r}, modified_at={self.modified_at!r}, status={self.status!r}, comments={self.comments!r}, images_rl={self.images_rl!r}, bbox={self.bbox!r}, labels={self.labels!r})"


class Type(Base):
    __tablename__ = "type"
    __table_args__ = {"schema": "label_studio"}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    colour: Mapped[str] = mapped_column(String(7), default='#000000')

    # association between Popject -> Association -> Type
    # project_associations: Mapped[List["AssociationProjectType"]] = relationship(back_populates='type')

    # many-to-many relationship to Type, bypassing the `Association` class
    # projects: Mapped[List["Project"]] = relationship(
    #     secondary="association_project_type",
    #     back_populates="types"
    # )

    def __repr__(self) -> str:
        return f"Type(id={self.id!r}, name={self.name!r}, colour={self.colour!r})"


