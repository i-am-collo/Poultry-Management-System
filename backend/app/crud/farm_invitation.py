from sqlalchemy.orm import Session
from app.models.farm_invitation import FarmInvitation
from app.schemas.farm_invitation import FarmInvitationCreate


def create_farm_invitation(db: Session, supplier_id: int, payload: FarmInvitationCreate) -> FarmInvitation:
    """Create a new farm invitation"""
    invitation = FarmInvitation(
        supplier_id=supplier_id,
        farm_name=payload.farmName,
        farmer_name=payload.farmerName,
        farmer_email=payload.farmerEmail,
        farmer_phone=payload.farmerPhone,
        farm_location=payload.farmLocation,
        farm_type=payload.farmType,
        message=payload.message,
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation


def get_invitations_by_supplier(db: Session, supplier_id: int) -> list[FarmInvitation]:
    """Get all invitations sent by a supplier"""
    return db.query(FarmInvitation).filter(FarmInvitation.supplier_id == supplier_id).all()


def get_invitation_by_id(db: Session, invitation_id: int, supplier_id: int) -> FarmInvitation | None:
    """Get a specific invitation (verify ownership)"""
    return db.query(FarmInvitation).filter(
        FarmInvitation.id == invitation_id,
        FarmInvitation.supplier_id == supplier_id
    ).first()
