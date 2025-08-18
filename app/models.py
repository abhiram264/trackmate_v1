from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, DateTime, text
from datetime import datetime, date

# ---------- USER MODEL ----------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    email: str = Field(max_length=255)
    password_hash: str = Field(max_length=255)
    role: str = Field(default="user", max_length=50)  # "user" or "admin"
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    )

    items: List["Item"] = Relationship(back_populates="owner")
    claims: List["Claim"] = Relationship(back_populates="claimer")


# ---------- ITEM MODEL ----------
class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    date: date
    location: str = Field(max_length=100)
    item_type: str = Field(sa_column=Column("type", String(10), nullable=False))  # maps to DB column 'type'
    image_url: Optional[str] = Field(default=None, max_length=512)
    status: str = Field(default="active", max_length=50)

    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    owner: Optional[User] = Relationship(back_populates="items")

    claims: List["Claim"] = Relationship(back_populates="item")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    )


# ---------- CLAIM MODEL ----------
class Claim(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id")
    claimer_id: int = Field(foreign_key="user.id")
    message: str = Field(max_length=500)
    status: str = Field(default="pending", max_length=50)  # "pending", "approved", "rejected"
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=False), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    )

    item: Optional[Item] = Relationship(back_populates="claims")
    claimer: Optional[User] = Relationship(back_populates="claims")
