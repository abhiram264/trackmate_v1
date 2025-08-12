from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime, date as Date
from enum import Enum


# ---------- ENUMS ----------
class ItemTypeEnum(str, Enum):
    LOST = "lost"
    FOUND = "found"


class ItemStatusEnum(str, Enum):
    ACTIVE = "active"
    CLAIMED = "claimed"
    RETURNED = "returned"


class ClaimStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class UserRoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"


# ---------- USER SCHEMAS ----------
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    role: Optional[UserRoleEnum] = UserRoleEnum.USER


class UserRead(UserBase):
    id: int
    role: str
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None


# ---------- ITEM SCHEMAS ----------
class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    item_type: ItemTypeEnum
    location: str = Field(..., min_length=1, max_length=100)
    date: Date
    image_url: Optional[str] = None

    @validator('date')
    def validate_date(cls, v):
        if v > Date.today():  # Fixed: Use Date.today() instead of date.today()
            raise ValueError('Date cannot be in the future')
        return v


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    item_type: Optional[ItemTypeEnum] = None
    location: Optional[str] = Field(None, min_length=1, max_length=100)
    date: Optional[Date] = None
    image_url: Optional[str] = None
    status: Optional[ItemStatusEnum] = None

    @validator('date')
    def validate_date(cls, v):
        if v and v > Date.today():  # Fixed: Use Date.today() instead of date.today()
            raise ValueError('Date cannot be in the future')
        return v


class ItemRead(ItemBase):
    id: int
    owner_id: int
    status: Optional[str] = "active"
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ItemWithOwner(ItemRead):
    """Item schema that includes owner information"""
    owner: UserRead


class ItemStatistics(BaseModel):
    """Schema for item statistics"""
    total_items: int
    lost_items: int
    found_items: int
    active_items: Optional[int] = None
    claimed_items: Optional[int] = None
    returned_items: Optional[int] = None
    recent_items_30_days: int
    top_locations: List[dict]


# ---------- CLAIM SCHEMAS ----------
class ClaimBase(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)


class ClaimCreate(ClaimBase):
    item_id: int = Field(..., gt=0)


class ClaimUpdate(BaseModel):
    message: Optional[str] = Field(None, min_length=1, max_length=500)
    status: Optional[ClaimStatusEnum] = None


class ClaimStatusUpdate(BaseModel):
    status: ClaimStatusEnum
    admin_notes: Optional[str] = Field(None, max_length=300)


class ClaimRead(ClaimBase):
    id: int
    item_id: int
    claimer_id: int
    status: Optional[str] = "pending"
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ClaimWithItem(ClaimRead):
    """Claim schema that includes item information"""
    item: ItemRead


class ClaimWithUser(ClaimRead):
    """Claim schema that includes claimer information"""
    claimer: UserRead


class ClaimWithDetails(ClaimRead):
    """Claim schema that includes both item and claimer information"""
    item: ItemRead
    claimer: UserRead


class ClaimStatistics(BaseModel):
    """Schema for claim statistics"""
    total_claims: int
    pending_claims: int
    approved_claims: int
    rejected_claims: int
    completed_claims: int
    claims_this_month: int
    average_response_time_hours: Optional[float] = None


# ---------- BULK OPERATION SCHEMAS ----------
class BulkItemUpdate(BaseModel):
    item_ids: List[int] = Field(..., min_length=1)
    status: ItemStatusEnum


class BulkClaimUpdate(BaseModel):
    claim_ids: List[int] = Field(..., min_length=1)
    status: ClaimStatusEnum
    admin_notes: Optional[str] = Field(None, max_length=300)


class BulkDeleteRequest(BaseModel):
    item_ids: List[int] = Field(..., min_length=1)


# ---------- RESPONSE SCHEMAS ----------
class MessageResponse(BaseModel):
    message: str


class BulkUpdateResponse(BaseModel):
    message: str
    updated_count: int
    status: Optional[str] = None


class BulkDeleteResponse(BaseModel):
    message: str
    deleted_count: int


# ---------- FILTER SCHEMAS ----------
class ItemFilters(BaseModel):
    """Schema for item filtering parameters"""
    item_type: Optional[ItemTypeEnum] = None
    location: Optional[str] = None
    date_from: Optional[Date] = None  # Fixed: Use Date instead of date
    date_to: Optional[Date] = None    # Fixed: Use Date instead of date
    status: Optional[ItemStatusEnum] = None
    owner_only: bool = False
    search: Optional[str] = None
    limit: int = Field(25, ge=1, le=100)
    offset: int = Field(0, ge=0)

    @validator('date_to')
    def validate_date_range(cls, v, values):
        date_from = values.get('date_from')
        if date_from and v and date_from > v:
            raise ValueError('date_from cannot be after date_to')
        return v


class ClaimFilters(BaseModel):
    """Schema for claim filtering parameters"""
    status: Optional[ClaimStatusEnum] = None
    item_type: Optional[ItemTypeEnum] = None
    my_claims: bool = False
    limit: int = Field(25, ge=1, le=100)
    offset: int = Field(0, ge=0)


# ---------- AUTHENTICATION SCHEMAS ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    email: Optional[str] = None


# ---------- IMAGE UPLOAD SCHEMAS ----------
class ImageUploadResponse(BaseModel):
    message: str
    image_url: str
    image_id: Optional[str] = None


# ---------- SEARCH SCHEMAS ----------
class SearchFilters(BaseModel):
    """Schema for advanced search parameters"""
    query: str = Field(..., min_length=1, max_length=200)
    item_type: Optional[ItemTypeEnum] = None
    location: Optional[str] = None
    date_from: Optional[Date] = None  # Fixed: Use Date instead of date
    date_to: Optional[Date] = None    # Fixed: Use Date instead of date
    similarity_threshold: float = Field(0.5, ge=0.1, le=1.0)
    limit: int = Field(10, ge=1, le=50)


class SimilarItemsResponse(BaseModel):
    """Schema for similar items search results"""
    reference_item: ItemRead
    similar_items: List[ItemRead]
    similarity_scores: List[float]


# ---------- NOTIFICATION SCHEMAS ----------
class NotificationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=300)
    notification_type: str  # "claim_created", "claim_approved", "item_matched", etc.


class NotificationCreate(NotificationBase):
    user_id: int
    related_item_id: Optional[int] = None
    related_claim_id: Optional[int] = None


class NotificationRead(NotificationBase):
    id: int
    user_id: int
    related_item_id: Optional[int] = None
    related_claim_id: Optional[int] = None
    is_read: bool = False
    created_at: datetime

    class Config:
        orm_mode = True


# ---------- VALIDATION HELPERS ----------
def validate_item_type_transition(current_type: str, new_type: str) -> bool:
    """Validate if item type transition is allowed"""
    return current_type != new_type


def validate_claim_status_transition(current_status: str, new_status: str) -> bool:
    """Validate if claim status transition is allowed"""
    valid_transitions = {
        "pending": ["approved", "rejected"],
        "approved": ["completed"],
        "rejected": [],
        "completed": []
    }
    return new_status in valid_transitions.get(current_status, [])
