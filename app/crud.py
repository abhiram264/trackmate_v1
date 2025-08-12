from sqlmodel import Session, select, and_, or_, func
from sqlalchemy import desc
from app import models, schemas
from typing import List, Optional, Dict, Any, cast
from datetime import date as Date, datetime, timedelta


# ---------- USER CRUD ----------
def create_user(session: Session, user: schemas.UserCreate, password_hash: str) -> models.User:
    db_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=password_hash,
        role=user.role if hasattr(user, "role") else "user"  # default role
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(session: Session, email: str) -> Optional[models.User]:
    statement = select(models.User).where(models.User.email == email)
    return session.exec(statement).first()


def get_user_by_id(session: Session, user_id: int) -> Optional[models.User]:
    statement = select(models.User).where(models.User.id == user_id)
    return session.exec(statement).first()


# ---------- ITEM CRUD ----------
def create_item(session: Session, item: schemas.ItemCreate, owner_id: int) -> models.Item:
    db_item = models.Item(**item.model_dump(), owner_id=owner_id)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def get_items(session: Session) -> List[models.Item]:
    statement = select(models.Item)
    return session.exec(statement).all()


def get_items_with_filters(session: Session, filters: Dict[str, Any]) -> List[models.Item]:
    """
    Get items with comprehensive filtering support.
    
    Args:
        session: Database session
        filters: Dictionary containing filter parameters
            - item_type: Filter by 'lost' or 'found'
            - location: Filter by location
            - date_from: Filter items from this date
            - date_to: Filter items until this date
            - status: Filter by status
            - owner_id: Filter by owner
            - search: Search in name and description
            - limit: Number of items to return
            - offset: Number of items to skip
    """
    statement = select(models.Item)
    
    # Apply filters
    conditions = []
    
    if filters.get("item_type"):
        conditions.append(models.Item.item_type == filters["item_type"])
    
    if filters.get("location"):
        conditions.append(cast(Any, models.Item.location).ilike(f"%{filters['location']}%"))
    
    if filters.get("date_from"):
        conditions.append(models.Item.date >= filters["date_from"])
    
    if filters.get("date_to"):
        conditions.append(models.Item.date <= filters["date_to"])
    
    if filters.get("status"):
        conditions.append(models.Item.status == filters["status"])
    
    if filters.get("owner_id"):
        conditions.append(models.Item.owner_id == filters["owner_id"])
    
    if filters.get("search"):
        search_term = f"%{filters['search']}%"
        conditions.append(
            or_(
                cast(Any, models.Item.name).ilike(search_term),
                cast(Any, models.Item.description).ilike(search_term)
            )
        )
    
    # Apply all conditions
    if conditions:
        statement = statement.where(and_(*conditions))
    
    # Order by most recent first
    statement = statement.order_by(desc(cast(Any, models.Item.date)))
    
    # Apply pagination
    if filters.get("limit"):
        statement = statement.limit(filters["limit"])
    
    if filters.get("offset"):
        statement = statement.offset(filters["offset"])
    
    results = session.exec(statement).all()
    return list(results)


def get_item_by_id(session: Session, item_id: int) -> Optional[models.Item]:
    statement = select(models.Item).where(models.Item.id == item_id)
    return session.exec(statement).first()


def update_item(session: Session, db_item: models.Item, item_data: schemas.ItemUpdate) -> models.Item:
    for key, value in item_data.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def delete_item(session: Session, db_item: models.Item):
    session.delete(db_item)
    session.commit()


def get_items_statistics(session: Session) -> Dict[str, Any]:
    """Get comprehensive statistics about items in the system."""
    
    # Total items count
    total_items = session.exec(select(func.count()).select_from(models.Item)).first()
    
    # Count by type
    lost_count = session.exec(
        select(func.count()).select_from(models.Item).where(models.Item.item_type == "lost")
    ).first()
    
    found_count = session.exec(
        select(func.count()).select_from(models.Item).where(models.Item.item_type == "found")
    ).first()
    
    # Count by status (if you have status field)
    try:
        active_count = session.exec(
            select(func.count()).select_from(models.Item).where(models.Item.status == "active")
        ).first()
        claimed_count = session.exec(
            select(func.count()).select_from(models.Item).where(models.Item.status == "claimed")
        ).first()
        returned_count = session.exec(
            select(func.count()).select_from(models.Item).where(models.Item.status == "returned")
        ).first()
    except AttributeError:
        # If status field doesn't exist, set to None
        active_count = None
        claimed_count = None
        returned_count = None
    
    # Most common locations
    location_stats = session.exec(
        select(models.Item.location, func.count().label('count'))
        .select_from(models.Item)
        .group_by(models.Item.location)
        .order_by(desc('count'))
        .limit(5)
    ).all()
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_items = session.exec(
        select(func.count()).select_from(models.Item).where(models.Item.date >= thirty_days_ago)
    ).first()
    
    return {
        "total_items": total_items or 0,
        "lost_items": lost_count or 0,
        "found_items": found_count or 0,
        "active_items": active_count,
        "claimed_items": claimed_count,
        "returned_items": returned_count,
        "recent_items_30_days": recent_items or 0,
        "top_locations": [{"location": loc, "count": count} for loc, count in location_stats] if location_stats else []
    }


def bulk_update_item_status(session: Session, item_ids: List[int], new_status: str) -> int:
    """Bulk update status for multiple items."""
    try:
        # Get all items with the given IDs
        statement = select(models.Item).where(cast(Any, models.Item.id).in_(item_ids))
        items_to_update = session.exec(statement).all()
        
        updated_count = 0
        for item in items_to_update:
            item.status = new_status
            session.add(item)
            updated_count += 1
        
        session.commit()
        return updated_count
    
    except AttributeError:
        # If status field doesn't exist in your model, raise an error
        raise ValueError("Status field not found in Item model")


def bulk_delete_items(session: Session, item_ids: List[int]) -> int:
    """Bulk delete multiple items."""
    statement = select(models.Item).where(models.Item.id.in_(item_ids))
    items_to_delete = session.exec(statement).all()
    
    deleted_count = 0
    for item in items_to_delete:
        session.delete(item)
        deleted_count += 1
    
    session.commit()
    return deleted_count


# ---------- CLAIM CRUD ----------
def create_claim(session: Session, claim: schemas.ClaimCreate, claimer_id: int) -> models.Claim:
    db_claim = models.Claim(**claim.model_dump(), claimer_id=claimer_id)
    session.add(db_claim)
    session.commit()
    session.refresh(db_claim)
    return db_claim


def get_claims_for_item(session: Session, item_id: int) -> List[models.Claim]:
    statement = select(models.Claim).where(models.Claim.item_id == item_id)
    results = session.exec(statement).all()
    return list(results)


def get_claims_by_user(session: Session, user_id: int) -> List[models.Claim]:
    """Get all claims made by a specific user."""
    statement = select(models.Claim).where(models.Claim.claimer_id == user_id)
    results = session.exec(statement).all()
    return list(results)


def get_claim_by_id(session: Session, claim_id: int) -> Optional[models.Claim]:
    """Get a specific claim by ID."""
    statement = select(models.Claim).where(models.Claim.id == claim_id)
    return session.exec(statement).first()


def get_claims_with_filters(session: Session, filters: Dict[str, Any]) -> List[models.Claim]:
    """Get claims with comprehensive filtering support."""
    statement = select(models.Claim)
    
    # Apply filters
    conditions = []
    
    if filters.get("status"):
        conditions.append(models.Claim.status == filters["status"])
    
    if filters.get("item_type"):
        # Join with items table to filter by item type
        statement = statement.join(models.Item, cast(Any, (models.Claim.item_id == models.Item.id)))
        conditions.append(models.Item.item_type == filters["item_type"])
    
    if filters.get("user_id"):
        conditions.append(models.Claim.claimer_id == filters["user_id"])
    
    # Apply all conditions
    if conditions:
        statement = statement.where(and_(*conditions))
    
    # Order by most recent first
    statement = statement.order_by(desc(cast(Any, models.Claim.created_at)))
    
    # Apply pagination
    if filters.get("limit"):
        statement = statement.limit(filters["limit"])
    
    if filters.get("offset"):
        statement = statement.offset(filters["offset"])
    
    results = session.exec(statement).all()
    return list(results)


def update_claim_status(session: Session, claim_id: int, status: str) -> Optional[models.Claim]:
    """Update claim status."""
    db_claim = get_claim_by_id(session, claim_id)
    if db_claim:
        try:
            db_claim.status = status
            # Update timestamp if field exists
            if hasattr(db_claim, 'updated_at'):
                db_claim.updated_at = datetime.utcnow()
            session.add(db_claim)
            session.commit()
            session.refresh(db_claim)
            return db_claim
        except AttributeError:
            # If status field doesn't exist in Claim model
            raise ValueError("Status field not found in Claim model")
    return None


def delete_claim(session: Session, claim_id: int) -> bool:
    """Delete a claim."""
    db_claim = get_claim_by_id(session, claim_id)
    if db_claim:
        session.delete(db_claim)
        session.commit()
        return True
    return False


def get_claims_statistics(session: Session) -> Dict[str, Any]:
    """Get comprehensive statistics about claims in the system."""
    
    # Total claims count
    total_claims = session.exec(select(func.count()).select_from(models.Claim)).first()
    
    # Count by status (if you have status field)
    try:
        pending_claims = session.exec(
            select(func.count()).select_from(models.Claim).where(models.Claim.status == "pending")
        ).first()
        approved_claims = session.exec(
            select(func.count()).select_from(models.Claim).where(models.Claim.status == "approved")
        ).first()
        rejected_claims = session.exec(
            select(func.count()).select_from(models.Claim).where(models.Claim.status == "rejected")
        ).first()
        completed_claims = session.exec(
            select(func.count()).select_from(models.Claim).where(models.Claim.status == "completed")
        ).first()
    except AttributeError:
        # If status field doesn't exist, set to None
        pending_claims = None
        approved_claims = None
        rejected_claims = None
        completed_claims = None
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    try:
        claims_this_month = session.exec(
            select(func.count()).select_from(models.Claim).where(models.Claim.created_at >= thirty_days_ago)
        ).first()
    except AttributeError:
        # If created_at field doesn't exist, set to 0
        claims_this_month = 0
    
    return {
        "total_claims": total_claims or 0,
        "pending_claims": pending_claims,
        "approved_claims": approved_claims,
        "rejected_claims": rejected_claims,
        "completed_claims": completed_claims,
        "claims_this_month": claims_this_month or 0,
        "average_response_time_hours": None  # You can implement this later
    }


def bulk_update_claims_status(session: Session, claim_ids: List[int], new_status: str) -> int:
    """Bulk update status for multiple claims."""
    try:
        # Get all claims with the given IDs
        statement = select(models.Claim).where(cast(Any, models.Claim.id).in_(claim_ids))
        claims_to_update = session.exec(statement).all()
        
        updated_count = 0
        for claim in claims_to_update:
            claim.status = new_status
            # Update timestamp if field exists
            if hasattr(claim, 'updated_at'):
                claim.updated_at = datetime.utcnow()
            session.add(claim)
            updated_count += 1
        
        session.commit()
        return updated_count
    
    except AttributeError:
        # If status field doesn't exist in your model, raise an error
        raise ValueError("Status field not found in Claim model")


# ---------- ADVANCED SEARCH FUNCTIONS ----------
def search_similar_items(session: Session, item_id: int, similarity_threshold: float = 0.5) -> List[models.Item]:
    """
    Find items similar to the given item (for matching lost/found items).
    This is a basic implementation - you can enhance with ML similarity search.
    """
    # Get the reference item
    reference_item = get_item_by_id(session, item_id)
    if not reference_item:
        return []
    
    # Find items of opposite type (lost vs found) with similar names/descriptions
    opposite_type = "found" if reference_item.item_type == "lost" else "lost"
    
    # Simple text similarity search
    reference_words = set(reference_item.name.lower().split() + reference_item.description.lower().split())
    
    statement = select(models.Item).where(
        and_(
            models.Item.item_type == opposite_type,
            models.Item.id != item_id
        )
    )
    
    potential_matches = session.exec(statement).all()
    similar_items = []
    
    for item in potential_matches:
        item_words = set(item.name.lower().split() + item.description.lower().split())
        
        # Calculate simple Jaccard similarity
        intersection = len(reference_words.intersection(item_words))
        union = len(reference_words.union(item_words))
        
        if union > 0:
            similarity = intersection / union
            if similarity >= similarity_threshold:
                similar_items.append(item)
    
    return similar_items


def get_items_by_date_range(session: Session, start_date: Date, end_date: Date, item_type: Optional[str] = None) -> List[models.Item]:
    """Get items within a specific date range."""
    statement = select(models.Item).where(
        and_(
            models.Item.date >= start_date,
            models.Item.date <= end_date
        )
    )
    
    if item_type:
        statement = statement.where(models.Item.item_type == item_type)
    
    results = session.exec(statement.order_by(desc(cast(Any, models.Item.date)))).all()
    return list(results)
