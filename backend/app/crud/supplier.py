from sqlalchemy.orm import Session
import json
from app.models.supplier import SupplierProfile
from app.schemas.product import SupplierRegisterRequest


def create_supplier_profile(
    db: Session, supplier_id: int, payload: SupplierRegisterRequest
) -> SupplierProfile:
    """Create a supplier profile"""
    supplier_profile = SupplierProfile(
        supplier_id=supplier_id,
        business_name=payload.business_name,
        contact_person=payload.contact_person,
        county=payload.county,
        phone=payload.phone,
        email=payload.email,
        kra_pin=payload.kra_pin,
        categories=json.dumps(payload.categories),
        payment_mpesa_till=payload.payment_mpesa_till,
    )
    db.add(supplier_profile)
    db.commit()
    db.refresh(supplier_profile)
    return supplier_profile


def get_supplier_profile(db: Session, supplier_id: int) -> SupplierProfile | None:
    """Get supplier profile by supplier ID"""
    return db.query(SupplierProfile).filter(SupplierProfile.supplier_id == supplier_id).first()


def supplier_profile_exists(db: Session, supplier_id: int) -> bool:
    """Check if supplier profile exists"""
    return db.query(SupplierProfile).filter(SupplierProfile.supplier_id == supplier_id).first() is not None
