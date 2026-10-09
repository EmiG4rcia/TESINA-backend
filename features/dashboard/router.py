from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_admin
from features.products.models import Product
from features.raw_materials.models import RawMaterial
from features.deliveries.models import Delivery
from features.scheduled_orders.models import ScheduledOrder

router = APIRouter()


@router.get("")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    today = date.today()

    # Low stock products
    products = db.query(Product).filter(
        Product.is_active == True,
        Product.deleted_at == None,
        Product.alert_enabled == True,
    ).all()
    low_stock_products = [
        {
            "id": p.id,
            "name": p.name,
            "unit": p.unit,
            "stock_quantity": float(p.stock_quantity or 0),
            "stock_min_alert": float(p.stock_min_alert or 0),
        }
        for p in products
        if p.stock_quantity is not None
        and p.stock_min_alert is not None
        and float(p.stock_min_alert) > 0
        and float(p.stock_quantity) <= float(p.stock_min_alert)
    ]

    # Low stock raw materials
    raw_materials = db.query(RawMaterial).filter(
        RawMaterial.is_active == True,
        RawMaterial.deleted_at == None,
        RawMaterial.alert_enabled == True,
    ).all()
    low_stock_raw = [
        {
            "id": r.id,
            "name": r.name,
            "unit": r.unit,
            "stock_quantity": float(r.stock_quantity or 0),
            "stock_min_alert": float(r.stock_min_alert or 0),
        }
        for r in raw_materials
        if r.stock_quantity is not None
        and r.stock_min_alert is not None
        and float(r.stock_min_alert) > 0
        and float(r.stock_quantity) <= float(r.stock_min_alert)
    ]

    # Today's deliveries
    deliveries_today = db.query(Delivery).filter(
        Delivery.delivery_date == today,
        Delivery.deleted_at == None,
    ).all()

    pending_deliveries = [d for d in deliveries_today if d.status == "pending"]
    completed_deliveries = [d for d in deliveries_today if d.status == "completed"]

    # Upcoming scheduled orders (next 7 days)
    from datetime import timedelta
    upcoming = db.query(ScheduledOrder).filter(
        ScheduledOrder.scheduled_date >= today,
        ScheduledOrder.scheduled_date <= today + timedelta(days=7),
        ScheduledOrder.status == "pending",
        ScheduledOrder.deleted_at == None,
    ).count()

    return {
        "date": today,
        "deliveries": {
            "total_today": len(deliveries_today),
            "pending": len(pending_deliveries),
            "completed": len(completed_deliveries),
        },
        "stock_alerts": {
            "low_stock_products": low_stock_products,
            "low_stock_raw_materials": low_stock_raw,
            "total_alerts": len(low_stock_products) + len(low_stock_raw),
        },
        "upcoming_scheduled_orders": upcoming,
    }