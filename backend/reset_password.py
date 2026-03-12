from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

db = SessionLocal()

# Find farmer user
farmer = db.query(User).filter(User.email == "iamcollolimo@gmail.com").first()

if farmer:
    print(f"Found farmer: {farmer.email}")
    print(f"Resetting password to 'password123'...")
    
    # Update password
    farmer.hashed_password = hash_password("password123")
    db.commit()
    
    print(f"✅ Password updated successfully")
else:
    print("❌ Farmer not found")
