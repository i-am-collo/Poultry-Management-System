from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.crud.flock import (
    create_flock,
    delete_flock,
    get_flock_by_id_for_farmer,
    get_flocks_by_farmer,
    update_flock,
)
from app.db.database import get_db
from app.models.flock import Flock
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.flock import FlockCreate, FlockResponse, FlockUpdate

router = APIRouter(prefix="/farmers", tags=["Farmers"])


def serialize_flock(flock: Flock) -> FlockResponse:
    return FlockResponse(
        id=flock.id,
        farmer_id=flock.farmer_id,
        bird_type=flock.bird_type,
        breed=flock.breed,
        quantity=flock.quantity,
        age_weeks=flock.age_weeks,
        health_status=flock.health_status,
        daily_feed_kg=flock.daily_feed_kg,
        notes=flock.notes,
        created_at=flock.created_at,
        updated_at=flock.updated_at,
    )


@router.post("/register-flock", status_code=status.HTTP_201_CREATED, response_model=FlockResponse)
def register_flock(
    payload: FlockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    flock = create_flock(db, current_user.id, payload)
    return serialize_flock(flock)


@router.get("/flocks", response_model=list[FlockResponse])
def list_flocks(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    flocks = get_flocks_by_farmer(db, current_user.id)
    return [serialize_flock(flock) for flock in flocks]


@router.put("/flocks/{flock_id}", response_model=FlockResponse)
def update_flock_record(
    flock_id: int,
    payload: FlockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    flock = get_flock_by_id_for_farmer(db, flock_id, current_user.id)
    if not flock:
        raise HTTPException(status_code=404, detail="Flock not found")

    updated = update_flock(db, flock, payload)
    return serialize_flock(updated)


@router.delete("/flocks/{flock_id}", response_model=MessageResponse)
def remove_flock(
    flock_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    flock = get_flock_by_id_for_farmer(db, flock_id, current_user.id)
    if not flock:
        raise HTTPException(status_code=404, detail="Flock not found")

    delete_flock(db, flock)
    return {"message": "Flock deleted successfully"}
