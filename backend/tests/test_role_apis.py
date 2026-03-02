import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.api.buyers import create_order, list_orders, search_products
from app.api.farmers import list_flocks, register_flock
from app.api.suppliers import add_product, list_products
from app.db.database import Base
from app.models.user import User
from app.schemas.flock import FlockCreate
from app.schemas.order import OrderCreate
from app.schemas.product import ProductCreate


class RoleApiFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.engine.dispose()

    def setUp(self) -> None:
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.SessionLocal()

    def tearDown(self) -> None:
        self.db.close()

    def _create_user(self, role: str, index: int) -> User:
        user = User(
            name=f"{role.capitalize()} User {index}",
            email=f"{role}{index}@example.com",
            phone=f"+1555000{index:04d}",
            hashed_password="hashed-password-placeholder",
            role=role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def test_farmer_can_create_and_list_flocks(self) -> None:
        farmer = self._create_user("farmer", 1)
        payload = FlockCreate(
            bird_type="broiler",
            breed="Ross 308",
            quantity=300,
            age_weeks=3,
            health_status="healthy",
            daily_feed_kg=28.5,
            notes="Initial flock",
        )

        created = register_flock(payload=payload, db=self.db, current_user=farmer)
        self.assertEqual(created.quantity, 300)
        self.assertEqual(created.farmer_id, farmer.id)

        flocks = list_flocks(db=self.db, current_user=farmer)
        self.assertEqual(len(flocks), 1)
        self.assertEqual(flocks[0].breed, "Ross 308")

    def test_supplier_can_add_and_list_products(self) -> None:
        supplier = self._create_user("supplier", 2)
        payload = ProductCreate(
            name="Starter Feed 50kg",
            category="feed",
            description="High protein starter feed",
            price_per_unit=31.25,
            unit="bag",
            stock_quantity=140,
        )

        created = add_product(payload=payload, db=self.db, current_user=supplier)
        self.assertEqual(created.supplier_id, supplier.id)
        self.assertEqual(created.stock_quantity, 140)

        products = list_products(db=self.db, current_user=supplier)
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].name, "Starter Feed 50kg")

    def test_buyer_can_search_create_and_list_orders(self) -> None:
        supplier = self._create_user("supplier", 3)
        buyer = self._create_user("buyer", 4)

        product = add_product(
            payload=ProductCreate(
                name="Layer Mash Premium",
                category="feed",
                description="Premium layer feed",
                price_per_unit=27.5,
                unit="bag",
                stock_quantity=100,
            ),
            db=self.db,
            current_user=supplier,
        )

        found = search_products(q="Layer", db=self.db, _=buyer)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].id, product.id)

        created_order = create_order(
            payload=OrderCreate(product_id=product.id, quantity=4, note="Urgent"),
            db=self.db,
            current_user=buyer,
        )
        self.assertEqual(created_order.quantity, 4)
        self.assertEqual(created_order.total_price, 110.0)

        orders = list_orders(db=self.db, current_user=buyer)
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].product_name, "Layer Mash Premium")
