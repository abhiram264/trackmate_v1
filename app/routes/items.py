from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlmodel import Session
from typing import List, Optional, cast
import shutil
import os
import uuid
import logging
from datetime import date as Date
from pathlib import Path
from app import schemas, models, crud
from app.database import get_session
from app.routes.auth import get_current_user

# Setup logging
logger = logging.getLogger(__name__)

# File upload configuration
UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Main items router
router = APIRouter(prefix="/items", tags=["Items"])


def validate_image(image: UploadFile) -> None:
    """Validate uploaded image file."""
    if not image.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    filename = cast(str, image.filename)
    
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    image.file.seek(0, 2)  # Seek to end
    file_size = image.file.tell()
    image.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")


def save_uploaded_file(image: UploadFile, item_type: str, user_id: int) -> str:
    """Save uploaded file with secure filename."""
    validate_image(image)
    
    file_ext = os.path.splitext(cast(str, image.filename))[1].lower()
    secure_filename = f"{item_type}_{user_id}_{uuid.uuid4()}{file_ext}"
    image_path = Path(UPLOAD_DIR) / secure_filename
    
    try:
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        return str(image_path)
    except Exception as e:
        # Clean up partial file if save failed
        if image_path.exists():
            image_path.unlink()
        logger.error(f"Failed to save image: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save image")
    finally:
        image.file.close()


# ==================== UNIFIED ITEMS ENDPOINTS WITH FILTERING ====================

@router.post("/", response_model=schemas.ItemRead)
def create_item(
    name: str = Form(..., min_length=1, max_length=100),
    description: str = Form(..., min_length=1, max_length=500),
    item_type: str = Form(...),
    location: str = Form(..., min_length=1, max_length=100),
    date: Date = Form(...),
    image: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new lost or found item with optional image."""
    
    # Validate item_type
    valid_types = {"lost", "found"}
    if item_type.lower() not in valid_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid item_type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Validate date
    today = Date.today()
    if item_type.lower() == "found" and date > today:
        raise HTTPException(status_code=400, detail="Found date cannot be in the future")
    
    # Save image if provided
    image_path = None
    if image:
        if current_user.id is None:
            raise HTTPException(status_code=401, detail="Invalid user")
        image_path = save_uploaded_file(image, item_type.lower(), int(current_user.id))
    
    # Create item
    item_data = schemas.ItemCreate(
        name=name.strip(),
        description=description.strip(),
        item_type=schemas.ItemTypeEnum(item_type.lower()),
        location=location.strip(),
        date=date,
        image_url=image_path
    )
    
    try:
        if current_user.id is None:
            raise HTTPException(status_code=401, detail="Invalid user")
        return crud.create_item(session, item_data, owner_id=int(current_user.id))
    except Exception as e:
        # Clean up uploaded file if database operation fails
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        logger.error(f"Failed to create item for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create item")


@router.get("/", response_model=List[schemas.ItemRead])
def list_items(
    item_type: Optional[str] = Query(None, description="Filter by item type: 'lost' or 'found'"),
    location: Optional[str] = Query(None, description="Filter by location"),
    date_from: Optional[Date] = Query(None, description="Filter items from this date"),
    date_to: Optional[Date] = Query(None, description="Filter items until this date"),
    status: Optional[str] = Query(None, description="Filter by status: 'active', 'claimed', 'returned'"),
    owner_only: bool = Query(False, description="Show only items owned by current user"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    limit: int = Query(25, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    session: Session = Depends(get_session),
    current_user: Optional[models.User] = Depends(get_current_user)
):
    """
    Retrieve items with comprehensive filtering options.
    
    **Usage Examples:**
    - Get all items: `/items`
    - Get lost items only: `/items?item_type=lost`
    - Get found items only: `/items?item_type=found`
    - Get items in library: `/items?location=library`
    - Get recent lost items: `/items?item_type=lost&date_from=2025-01-01`
    - Search for wallet: `/items?search=wallet`
    - Get user's own items: `/items?owner_only=true`
    """
    
    # Validate item_type filter
    if item_type and item_type.lower() not in {"lost", "found"}:
        raise HTTPException(status_code=400, detail="Invalid item_type. Must be 'lost' or 'found'")
    
    # Validate status filter
    valid_statuses = {"active", "claimed", "returned"}
    if status and status.lower() not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    # Validate date range
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from cannot be after date_to")
    
    filters = {
        "item_type": item_type.lower() if item_type else None,
        "location": location,
        "date_from": date_from,
        "date_to": date_to,
        "status": status.lower() if status else None,
        "owner_id": current_user.id if owner_only and current_user else None,
        "search": search,
        "limit": limit,
        "offset": offset
    }
    
    return crud.get_items_with_filters(session, filters)


@router.get("/stats")
def get_items_statistics(
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    """Get comprehensive statistics about items in the system."""
    return crud.get_items_statistics(session)


@router.get("/{item_id}", response_model=schemas.ItemRead)
def get_item(
    item_id: int,
    session: Session = Depends(get_session)
):
    """Get a single item by ID."""
    db_item = crud.get_item_by_id(session, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.get("/{item_id}/image")
def get_item_image(
    item_id: int,
    session: Session = Depends(get_session)
):
    """Serve the image file for an item."""
    db_item = crud.get_item_by_id(session, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if not db_item.image_url or not os.path.exists(db_item.image_url):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(
        db_item.image_url,
        media_type="image/jpeg",
        filename=f"item_{item_id}_image.jpg"
    )


@router.put("/{item_id}", response_model=schemas.ItemRead)
def update_item(
    item_id: int,
    item_data: schemas.ItemUpdate,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    """Update an item. Only the owner or admin can update."""
    db_item = crud.get_item_by_id(session, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check permissions
    if db_item.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this item")
    
    try:
        return crud.update_item(session, db_item, item_data)
    except Exception as e:
        logger.error(f"Failed to update item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update item")


@router.put("/{item_id}/image", response_model=schemas.ItemRead)
def update_item_image(
    item_id: int,
    image: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    """Update the image for an item."""
    db_item = crud.get_item_by_id(session, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check permissions
    if db_item.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this item")
    
    # Save new image
    if current_user.id is None:
        raise HTTPException(status_code=401, detail="Invalid user")
    image_path = save_uploaded_file(image, db_item.item_type, int(current_user.id))
    
    # Remove old image if exists
    if db_item.image_url and os.path.exists(db_item.image_url):
        try:
            os.remove(db_item.image_url)
        except Exception as e:
            logger.warning(f"Failed to delete old image {db_item.image_url}: {str(e)}")
    
    # Update item with new image path
    try:
        item_update = schemas.ItemUpdate.model_validate({"image_url": image_path})
        return crud.update_item(session, db_item, item_update)
    except Exception as e:
        # Clean up new image if database update fails
        if os.path.exists(image_path):
            os.remove(image_path)
        logger.error(f"Failed to update item image {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update item image")


@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    """Delete an item. Only the owner or admin can delete."""
    db_item = crud.get_item_by_id(session, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check permissions
    if db_item.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this item")

    # Clean up image file if exists
    if db_item.image_url and os.path.exists(db_item.image_url):
        try:
            os.remove(db_item.image_url)
        except Exception as e:
            logger.warning(f"Failed to delete image file {db_item.image_url}: {str(e)}")

    try:
        crud.delete_item(session, db_item)
        return {"message": "Item deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete item")


# # ==================== BULK OPERATIONS ====================

# @router.post("/bulk-update-status")
# def bulk_update_status(
#     item_ids: List[int],
#     new_status: str,
#     session: Session = Depends(get_session),
#     current_user: models.User = Depends(get_current_user)
# ):
#     """Bulk update status for multiple items (admin only)."""
#     if current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="Admin access required")
    
#     valid_statuses = {"active", "claimed", "returned"}
#     if new_status.lower() not in valid_statuses:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
#         )
    
#     try:
#         updated_count = crud.bulk_update_item_status(session, item_ids, new_status.lower())
#         return {
#             "message": f"Successfully updated {updated_count} items",
#             "updated_count": updated_count,
#             "new_status": new_status.lower()
#         }
#     except Exception as e:
#         logger.error(f"Failed to bulk update items: {str(e)}")
#         raise HTTPException(status_code=500, detail="Failed to update items")


# @router.delete("/bulk-delete")
# def bulk_delete_items(
#     item_ids: List[int],
#     session: Session = Depends(get_session),
#     current_user: models.User = Depends(get_current_user)
# ):
#     """Bulk delete multiple items (admin only)."""
#     if current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="Admin access required")
    
#     try:
#         deleted_count = crud.bulk_delete_items(session, item_ids)
#         return {
#             "message": f"Successfully deleted {deleted_count} items",
#             "deleted_count": deleted_count
#         }
#     except Exception as e:
#         logger.error(f"Failed to bulk delete items: {str(e)}")
#         raise HTTPException(status_code=500, detail="Failed to delete items")
