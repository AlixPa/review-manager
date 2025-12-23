from datetime import date, datetime, timedelta

from src.clients.mysql import AMysqlClientReader, AMySqlIdNotFoundError
from src.config.path import path_config
from src.models.database import Reward, User, UUID4Str
from src.modules.date import get_first_day_of_cycle

from .exceptions import UserNotFound


async def get_users_service() -> list[tuple[User, int]]:
    """
    Returns list of users with their total reward since last Tuesday
    """
    reader = AMysqlClientReader()
    users = await reader.select(table=User)

    rewards = await reader.select(
        table=Reward,
        cond_greater_or_eq=dict(created_at=get_first_day_of_cycle()),
    )
    return [(u, sum([r.points for r in rewards if r.user_id == u.id])) for u in users]


async def patch_set_user_service(user_public_id: UUID4Str) -> User:
    reader = AMysqlClientReader()
    users = await reader.select(table=User, cond_equal=dict(public_id=user_public_id))
    if not users:
        raise UserNotFound()
    return users[0]
