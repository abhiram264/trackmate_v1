from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import List, Optional
import logging
from app import schemas, models, crud
from app.database import get_session
from app.routes.auth import get_current_user

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/claims", tags=["Claims"])

# ==================== CLAIM CREATION & MANAGEMENT ====================

@router.post("/", response_model=schemas.ClaimRead)
def create_claim(
    claim: schemas.ClaimCreate,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a claim for an item.
    
    **Business Rules:**
    - Only authenticated users can create claims
    - Cannot claim your own items
    - Cannot create duplicate claims for the same item
    - Item must exist and be active
    """
    try:
        # Check if item exists
        db_item = crud.get_item_by_id(session, claim.item_id)
        if not db_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Item not found"
            )
        
        # Validate item status (if you have status field)
        if hasattr(db_item, 'status') and db_item.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot claim inactive items"
            )
        
        # Prevent claiming your own item
        if db_item.owner_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Cannot claim your own item"
            )
        
        # Check for existing claims by this user for this item
        existing_claims = crud.get_claims_for_item(session, claim.item_id)
        user_existing_claim = next(
            (c for c in existing_claims if c.claimer_id == current_user.id), None
        )
        
        if user_existing_claim:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already claimed this item"
            )
        
        # Create the claim
        if current_user.id is None:
            raise HTTPException(status_code=401, detail="Invalid user")
        new_claim = crud.create_claim(session, claim, claimer_id=int(current_user.id))
        
        logger.info(f"User {current_user.id} created claim {new_claim.id} for item {claim.item_id}")
        return new_claim
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating claim for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create claim"
        )

# ==================== CLAIM RETRIEVAL (FIXED ORDER) ====================

@router.get("/", response_model=List[schemas.ClaimRead])
def list_claims(
    status_filter: Optional[str] = Query(None, description="Filter by claim status"),
    item_type: Optional[str] = Query(None, description="Filter by item type (lost/found)"),
    my_claims: bool = Query(False, description="Show only my claims"),
    limit: int = Query(25, ge=1, le=100, description="Number of claims to return"),
    offset: int = Query(0, ge=0, description="Number of claims to skip"),
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieve claims with filtering options.
    
    **Access Control:**
    - Regular users can see their own claims and claims for their items
    - Admins can see all claims with filtering
    """
    try:
        logger.info(f"User {current_user.id} (role: {current_user.role}) requesting claims with filters: status={status_filter}, item_type={item_type}, my_claims={my_claims}")
        
        if current_user.role == "admin":
            # Admins can see all claims with filtering
            filters = {
                "status": status_filter,
                "item_type": item_type,
                "user_id": current_user.id if my_claims else None,
                "limit": limit,
                "offset": offset
            }
            claims = crud.get_claims_with_filters(session, filters)
            logger.info(f"Admin retrieved {len(claims)} claims")
            return claims
        else:
            # Regular users can see their own claims + claims for their items
            if current_user.id is None:
                raise HTTPException(status_code=401, detail="Invalid user")
            user_claims = crud.get_claims_by_user(session, int(current_user.id))
            
            # Also get claims for items they own
            user_items = crud.get_items_with_filters(session, {"owner_id": int(current_user.id)})
            item_claims = []
            for item in user_items:
                item_claims.extend(crud.get_claims_for_item(session, int(item.id)))
            
            # Combine and deduplicate
            all_claims = user_claims + [claim for claim in item_claims if claim.id not in [c.id for c in user_claims]]
            
            # Apply filtering
            if status_filter:
                all_claims = [c for c in all_claims if hasattr(c, 'status') and c.status == status_filter]
            
            # Apply pagination
            paginated_claims = all_claims[offset:offset + limit]
            
            logger.info(f"User retrieved {len(paginated_claims)} claims")
            return paginated_claims
            
    except Exception as e:
        logger.error(f"Error retrieving claims for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve claims"
        )

# 🔥 SPECIFIC ROUTES BEFORE GENERIC ONES - FIXED ORDER

@router.get("/stats/overview")
def get_claims_statistics(
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    """Get statistics about claims (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        return crud.get_claims_statistics(session)
    except Exception as e:
        logger.error(f"Error retrieving claims statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )

@router.get("/item/{item_id}", response_model=List[schemas.ClaimRead])
def get_claims_for_item(
    item_id: int,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieve all claims for a specific item.
    
    **Access Control:**
    - Item owners can see all claims for their items
    - Admins can see all claims
    - Regular users cannot access this endpoint
    """
    try:
        # Check if item exists
        db_item = crud.get_item_by_id(session, item_id)
        if not db_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        # Check permissions
        if current_user.role != "admin" and db_item.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view claims for this item"
            )
        
        claims = crud.get_claims_for_item(session, item_id)
        return claims
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving claims for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve claims"
        )

# 🔥 GENERIC ROUTE COMES LAST - AFTER ALL SPECIFIC ROUTES

@router.get("/{claim_id}", response_model=schemas.ClaimRead)
def get_claim(
    claim_id: int,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific claim by ID."""
    try:
        db_claim = crud.get_claim_by_id(session, claim_id)
        if not db_claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Claim not found"
            )
        
        # Check permissions
        if (current_user.role != "admin" and 
            db_claim.claimer_id != current_user.id):
            # Also check if user is the item owner
            db_item = crud.get_item_by_id(session, db_claim.item_id)
            if not db_item or db_item.owner_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view this claim"
                )
        
        return db_claim
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving claim {claim_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve claim"
        )

# ==================== CLAIM STATUS MANAGEMENT ====================

@router.put("/{claim_id}/status", response_model=schemas.ClaimRead)
def update_claim_status(
    claim_id: int,
    status_update: schemas.ClaimStatusUpdate,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update claim status (approve, reject, etc.).
    
    **Access Control:**
    - Only item owners and admins can update claim status
    - Cannot update your own claims
    """
    try:
        db_claim = crud.get_claim_by_id(session, claim_id)
        if not db_claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Claim not found"
            )
        
        # Get the item to check ownership
        db_item = crud.get_item_by_id(session, db_claim.item_id)
        if not db_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated item not found"
            )
        
        # Check permissions
        if (current_user.role != "admin" and 
            db_item.owner_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this claim"
            )
        
        # Prevent updating your own claims
        if db_claim.claimer_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update status of your own claim"
            )
        
        # Update claim status
        updated_claim = crud.update_claim_status(
            session, claim_id, status_update.status
        )
        
        logger.info(f"User {current_user.id} updated claim {claim_id} status to {status_update.status}")
        return updated_claim
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating claim {claim_id} status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update claim status"
        )

# ==================== CLAIM DELETION ====================

@router.delete("/{claim_id}")
def delete_claim(
    claim_id: int,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete a claim.
    
    **Access Control:**
    - Users can delete their own claims
    - Admins can delete any claim
    - Item owners can delete claims for their items
    """
    try:
        db_claim = crud.get_claim_by_id(session, claim_id)
        if not db_claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Claim not found"
            )
        
        # Check permissions
        can_delete = (
            current_user.role == "admin" or 
            db_claim.claimer_id == current_user.id
        )
        
        # Also allow item owner to delete claims
        if not can_delete:
            db_item = crud.get_item_by_id(session, db_claim.item_id)
            if db_item and db_item.owner_id == current_user.id:
                can_delete = True
        
        if not can_delete:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this claim"
            )
        
        # Delete the claim
        success = crud.delete_claim(session, claim_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete claim"
            )
        
        logger.info(f"User {current_user.id} deleted claim {claim_id}")
        return {"message": "Claim deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting claim {claim_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete claim"
        )

# ==================== BULK OPERATIONS ====================

# @router.post("/bulk-approve")
# def bulk_approve_claims(
#     claim_ids: List[int],
#     session: Session = Depends(get_session),
#     current_user: models.User = Depends(get_current_user)
# ):
#     """Bulk approve multiple claims (admin only)."""
#     if current_user.role != "admin":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Admin access required"
#         )
    
#     try:
#         approved_count = crud.bulk_update_claims_status(session, claim_ids, "approved")
#         logger.info(f"Admin {current_user.id} approved {approved_count} claims")
#         return {
#             "message": f"Successfully approved {approved_count} claims",
#             "approved_count": approved_count
#         }
#     except Exception as e:
#         logger.error(f"Error bulk approving claims: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to approve claims"
#         )
