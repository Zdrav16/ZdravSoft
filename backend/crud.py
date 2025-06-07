from sqlalchemy.orm import Session
import models, schemas
from datetime import datetime


def get_products(db: Session):
    return db.query(models.Product).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def create_sale(db: Session, sale: schemas.SaleCreate):
    db_sale = models.Sale(
        total_amount=sale.total_amount,
        date=datetime.utcnow()
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)

    for item in sale.items:
        db_item = models.SaleItem(
            sale_id=db_sale.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
        )
        db.add(db_item)

        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            product.quantity -= item.quantity

    db.commit()
    db.refresh(db_sale)
    return db_sale

def get_sales(db: Session):
    return db.query(models.Sale).all()
