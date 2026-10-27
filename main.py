from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from features.auth.router import router as auth_router
from features.raw_materials.router import router as raw_materials_router
from features.products.router import router as products_router
from features.production.router import router as production_router
from features.stock.router import router as stock_router
from features.destinations.router import router as destinations_router
from features.scheduled_orders.router import router as scheduled_orders_router
from features.deliveries.router import router as deliveries_router

from features.auth.models import User
from features.raw_materials.models import RawMaterial
from features.products.models import Product, ProductRecipe
from features.production.models import ProductionLog, ProductionLogInput
from features.stock.models import StockMovement
from features.destinations.models import Destination
from features.scheduled_orders.models import ScheduledOrder, ScheduledOrderItem
from features.deliveries.models import Delivery, DeliveryProduct
from features.dashboard.router import router as dashboard_router
from core.database import Base, engine, SessionLocal


def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Gestión de Negocio — API",
    description="API para el sistema de gestión de stock y reparto",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(raw_materials_router, prefix="/raw-materials", tags=["Raw Materials"])
app.include_router(products_router, prefix="/products", tags=["Products"])
app.include_router(production_router, prefix="/production", tags=["Production"])
app.include_router(stock_router, prefix="/stock", tags=["Stock"])
app.include_router(destinations_router, prefix="/destinations", tags=["Destinations"])
app.include_router(scheduled_orders_router, prefix="/scheduled-orders", tags=["Scheduled Orders"])
app.include_router(deliveries_router, prefix="/deliveries", tags=["Deliveries"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Gestión de Negocio API running"}