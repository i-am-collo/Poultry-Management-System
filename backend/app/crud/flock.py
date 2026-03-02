from sqlalchemy.orm import Session

from app.models.flock import Flock
from app.schemas.flock import FlockCreate, FlockUpdate


def create_flock(db: Session, farmer_id: int, payload: FlockCreate) -> Flock:
    flock = Flock(
        farmer_id=farmer_id,
        bird_type=payload.bird_type,
        breed=payload.breed,
        quantity=payload.quantity,
        age_weeks=payload.age_weeks,
        health_status=payload.health_status,
        daily_feed_kg=payload.daily_feed_kg,
        notes=payload.notes,
    )
    db.add(flock)
    db.commit()
    db.refresh(flock)
    return flock


def get_flocks_by_farmer(db: Session, farmer_id: int) -> list[Flock]:
    return (
        db.query(Flock)
        .filter(Flock.farmer_id == farmer_id)
        .order_by(Flock.created_at.desc())
        .all()
    )


def get_flock_by_id_for_farmer(db: Session, flock_id: int, farmer_id: int) -> Flock | None:
    return (
        db.query(Flock)
        .filter(Flock.id == flock_id, Flock.farmer_id == farmer_id)
        .first()
    )


def update_flock(db: Session, flock: Flock, payload: FlockUpdate) -> Flock:
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(flock, field, value)

    db.add(flock)
    db.commit()
    db.refresh(flock)
    return flock


def delete_flock(db: Session, flock: Flock) -> None:
    db.delete(flock)
    db.commit()
