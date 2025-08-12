from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, DateTime
from datetime import datetime, date

# ---------- USER MODEL ----------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    password_hash: str
    role: str = Field(default="user")  # "user" or "admin"
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default="CURRENT_TIMESTAMP")
    )

    items: List["Item"] = Relationship(back_populates="owner")
    claims: List["Claim"] = Relationship(back_populates="claimer")


# ---------- ITEM MODEL ----------
class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    date: date
    location: str
    item_type: str = Field(sa_column=Column("type", String, nullable=False))  # maps to DB column 'type'
    image_url: Optional[str] = None
    status: str = Field(default="active")

    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    owner: Optional[User] = Relationship(back_populates="items")

    claims: List["Claim"] = Relationship(back_populates="item")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default="CURRENT_TIMESTAMP")
    )


# ---------- CLAIM MODEL ----------
class Claim(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id")
    claimer_id: int = Field(foreign_key="user.id")
    message: str
    status: str = Field(default="pending")  # "pending", "approved", "rejected"
    created_at: datetime = Field(
    default_factory=datetime.utcnow,
    sa_column=Column(DateTime(timezone=True), nullable=False, server_default="CURRENT_TIMESTAMP")
)

    item: Optional[Item] = Relationship(back_populates="claims")
    claimer: Optional[User] = Relationship(back_populates="claims")
