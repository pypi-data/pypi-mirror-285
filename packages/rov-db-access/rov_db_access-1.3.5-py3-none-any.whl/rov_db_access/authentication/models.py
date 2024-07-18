from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    """Base Class of the model"""


class Organization(Base):
    __tablename__ = "organization"
    __table_args__ = {"schema": "admin"}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    bucket: Mapped[str] = mapped_column(server_default='upload-tif-images-test')
    workspace: Mapped[str] = mapped_column(server_default='rovisen')
    users: Mapped[List["User"]] = relationship(
        back_populates='organization',
        order_by="User.id"
    )

    def __repr__(self) -> str:
        return f"Organization(id={self.id!r}, name={self.name!r}, #users={len(self.users)!r})"


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "admin"}
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    display_name: Mapped[str]
    password: Mapped[str]
    logged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    organization_id: Mapped[int] = mapped_column(ForeignKey("admin.organization.id"))
    organization: Mapped["Organization"] = relationship(back_populates="users")
    roles: Mapped[List["Role"]] = relationship(secondary="admin.association_user_role")
    is_active: Mapped[bool] = mapped_column(server_default='True')
    email: Mapped[str] = mapped_column(unique=True)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, logged_at={self.logged_at!r})"


class Role(Base):
    __tablename__ = "role"
    __table_args__ = {"schema": "admin"}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    def __repr__(self) -> str:
        return f"Role(id={self.id!r}, name={self.name!r})"


class AssociationUserRole(Base):
    __tablename__ = "association_user_role"
    __table_args__ = {"schema": "admin"}
    user_id: Mapped[int] = mapped_column(ForeignKey("admin.user.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("admin.role.id"), primary_key=True)

    def __repr__(self) -> str:
        return f"AssociationUserRole(user_id={self.user_id!r}, role_id={self.role_id!r})"


class UnverifiedUser(Base):
    __tablename__ = "unverified_user"
    __table_args__ = {"schema": "admin"}
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    display_name: Mapped[str]
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"UnverifiedUser(id={self.id!r}, username={self.username!r})"
