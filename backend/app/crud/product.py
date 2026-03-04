from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def create_product(db: Session, supplier_id: int, payload: ProductCreate) -> Product:
    product = Product(
        supplier_id=supplier_id,
        name=payload.name,
        category=payload.category,
        description=payload.description,
        product_image=payload.product_image,
        unit_price=payload.unit_price,
        unit_of_measure=payload.unit_of_measure,
        stock_quantity=payload.stock_quantity,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_products_by_supplier(db: Session, supplier_id: int) -> list[Product]:
    return (
        db.query(Product)
        .filter(Product.supplier_id == supplier_id)
        .order_by(Product.created_at.desc())
        .all()
    )


def get_product_by_id_for_supplier(db: Session, product_id: int, supplier_id: int) -> Product | None:
    return (
        db.query(Product)
        .filter(Product.id == product_id, Product.supplier_id == supplier_id)
        .first()
    )


def get_product_by_id(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()


def update_product(db: Session, product: Product, payload: ProductUpdate) -> Product:
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(product, field, value)

    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()


def search_active_products(db: Session, query: str | None) -> list[Product]:
    products_query = db.query(Product).filter(Product.is_active.is_(True), Product.stock_quantity > 0)

    if query:
        search_text = f"%{query.strip()}%"
        products_query = products_query.filter(
            or_(
                Product.name.ilike(search_text),
                Product.category.ilike(search_text),
                Product.description.ilike(search_text),
            )
        )

    return products_query.order_by(Product.created_at.desc()).all()
