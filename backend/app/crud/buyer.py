from sqlalchemy.orm import Session
from app.models.buyer import BuyerProfile
from app.schemas.product import BuyerRegisterRequest


def create_buyer_profile(
    db: Session, buyer_id: int, payload: BuyerRegisterRequest
) -> BuyerProfile:
    """Create a buyer profile"""
    buyer_profile = BuyerProfile(
        buyer_id=buyer_id,
        full_name=payload.full_name,
        business_name=payload.business_name,
        county=payload.county,
        phone=payload.phone,
        email=payload.email,
        buyer_type=payload.buyer_type,
        preferred_payment=payload.preferred_payment,
    )
    db.add(buyer_profile)
    db.commit()
    db.refresh(buyer_profile)
    return buyer_profile


def get_buyer_profile(db: Session, buyer_id: int) -> BuyerProfile | None:
    """Get buyer profile by buyer ID"""
    return db.query(BuyerProfile).filter(BuyerProfile.buyer_id == buyer_id).first()


def buyer_profile_exists(db: Session, buyer_id: int) -> bool:
    """Check if buyer profile exists"""
    return db.query(BuyerProfile).filter(BuyerProfile.buyer_id == buyer_id).first() is not None
