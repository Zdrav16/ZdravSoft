from sqlalchemy.orm import Session
import models, schemas
from datetime import datetime

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

        # Намаляване на наличността
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            product.quantity -= item.quantity

    db.commit()
    db.refresh(db_sale)
    return db_sale

def get_sales(db: Session):
    return db.query(models.Sale).all()
