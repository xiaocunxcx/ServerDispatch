from fastapi import APIRouter

from internal.agent.routes import router as agent_router
from internal.audit.routes import router as audit_router
from internal.auth.admin_routes import router as admin_auth_router
from internal.auth.routes import router as auth_router
from internal.inventory.admin_routes import router as admin_inventory_router
from internal.inventory.routes import router as inventory_router
from internal.metrics.admin_routes import router as admin_metrics_router
from internal.metrics.routes import router as metrics_router
from internal.reservation.admin_routes import router as admin_reservation_router
from internal.reservation.routes import router as reservation_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(admin_auth_router)
api_router.include_router(inventory_router)
api_router.include_router(admin_inventory_router)
api_router.include_router(metrics_router)
api_router.include_router(admin_metrics_router)
api_router.include_router(reservation_router)
api_router.include_router(admin_reservation_router)
api_router.include_router(audit_router)
api_router.include_router(agent_router)
