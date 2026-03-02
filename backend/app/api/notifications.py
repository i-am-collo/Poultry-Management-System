from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.crud import notification as notification_crud

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/")
def list_notifications(user_id: int, db: Session = Depends(get_db)):
    return notification_crud.get_user_notifications(db, user_id)


@router.post("/")
def create_notification(user_id: int, title: str, message: str, type: str, db: Session = Depends(get_db)):
    return notification_crud.create_notification(db, user_id, title, message, type)