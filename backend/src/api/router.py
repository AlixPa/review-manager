from fastapi import APIRouter

from .auth import auth_router
from .rewards import rewards_router
from .tasks import tasks_router
from .users import users_router

router = APIRouter(prefix="/api")

router.include_router(auth_router)
router.include_router(rewards_router)
router.include_router(tasks_router)
router.include_router(users_router)
