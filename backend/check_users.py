from app.db.database import SessionLocal
from app.models.user import User

db = SessionLocal()
users = db.query(User).all()

print("\nUsers in database:")
for u in users:
    print(f"  - {u.email}: {getattr(u, 'role', 'no_role')} (ID: {u.id})")

print(f"\nTotal: {len(users)} users")

if len(users) == 0:
    print("\n⚠️  No users found. Creating test user...")
    from app.core.security import hash_password
    
    test_user = User(
        name="Test Farmer",
        email="farmer@test.com",
        phone="254712345678",
        hashed_password=hash_password("password123"),
        role="farmer"
    )
    db.add(test_user)
    db.commit()
    print(f"✅ Created test user: farmer@test.com")
