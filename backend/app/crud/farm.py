from sqlalchemy.orm import Session
from app.models.farms import Farm
from app.schemas.farm import FarmCreate, FarmUpdate


def create_farm(db: Session, farmer_id: int, payload: FarmCreate) -> Farm:
    """Create a new farm record for a farmer"""
    farm = Farm(
        farmer_id=farmer_id,
        farm_name=payload.farm_name,
        location=payload.location,
        size=payload.size,
        phone=payload.phone,
        description=payload.description,
    )
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


def get_farm_by_id(db: Session, farm_id: int, farmer_id: int) -> Farm | None:
    """Get a farm by ID, ensuring it belongs to the farmer"""
    return db.query(Farm).filter(
        Farm.id == farm_id,
        Farm.farmer_id == farmer_id
    ).first()


def get_farm_by_farmer(db: Session, farmer_id: int) -> Farm | None:
    """Get the farm for a specific farmer (assumes one farm per farmer)"""
    return db.query(Farm).filter(Farm.farmer_id == farmer_id).first()


def get_farms_by_farmer(db: Session, farmer_id: int) -> list[Farm]:
    """Get all farms for a farmer"""
    return db.query(Farm).filter(Farm.farmer_id == farmer_id).all()


def update_farm(db: Session, farm: Farm, payload: FarmUpdate) -> Farm:
    """Update a farm record"""
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(farm, field, value)
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


def delete_farm(db: Session, farm_id: int, farmer_id: int) -> bool:
    """Delete a farm"""
    farm = get_farm_by_id(db, farm_id, farmer_id)
    if farm:
        db.delete(farm)
        db.commit()
        return True
    return False
