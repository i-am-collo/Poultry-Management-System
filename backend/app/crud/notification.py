from sqlalchemy.orm import Session
from app.models.notification import Notification


def create_notification(db: Session, user_id: int, title: str, message: str, type: str):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_user_notifications(db: Session, user_id: int):
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()


def get_notification(db: Session, notification_id: int):
    """Get a single notification by ID"""
    return db.query(Notification).filter(Notification.id == notification_id).first()


def mark_notification_as_read(db: Session, notification: Notification):
    notification.is_read = True
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def update_notification(db: Session, notification_id: int, data: dict):
    """Update a notification with the given data"""
    notification = get_notification(db, notification_id)
    if not notification:
        return None
    
    for key, value in data.items():
        if hasattr(notification, key):
            setattr(notification, key, value)
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_as_read(db: Session, user_id: int):
    """Mark all notifications as read for a user"""
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).all()
    
    for notification in notifications:
        notification.is_read = True
    
    db.add_all(notifications)
    db.commit()
    return {"message": f"Marked {len(notifications)} notifications as read"}


def delete_notification(db: Session, notification_id: int):
    """Delete a notification"""
    notification = get_notification(db, notification_id)
    if notification:
        db.delete(notification)
        db.commit()
        return {"message": "Notification deleted"}
    return None


def delete_all_notifications(db: Session, user_id: int):
    """Delete all notifications for a user"""
    notifications = db.query(Notification).filter(Notification.user_id == user_id).all()
    
    for notification in notifications:
        db.delete(notification)
    
    db.commit()
    return {"message": f"Deleted {len(notifications)} notifications"}