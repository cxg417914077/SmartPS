from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.images import router as images_router


__all__ = [
    "auth_router",
    "images_router",
]
