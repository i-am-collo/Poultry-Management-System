from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.crud import notification as notification_crud
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/")
def list_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all notifications for the current user"""
    return notification_crud.get_user_notifications(db, current_user.id)


@router.get("/{notification_id}")
def get_notification(notification_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a specific notification"""
    return notification_crud.get_notification(db, notification_id)


@router.put("/{notification_id}")
def update_notification(notification_id: int, is_read: bool = False, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Mark a notification as read/unread"""
    return notification_crud.update_notification(db, notification_id, {"is_read": is_read})


@router.put("/mark-all-read")
def mark_all_as_read(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Mark all notifications as read for current user"""
    return notification_crud.mark_all_as_read(db, current_user.id)


@router.delete("/{notification_id}")
def delete_notification(notification_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a notification"""
    return notification_crud.delete_notification(db, notification_id)


@router.delete("/")
def delete_all_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete all notifications for current user"""
    return notification_crud.delete_all_notifications(db, current_user.id)