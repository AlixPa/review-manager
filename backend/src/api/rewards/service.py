from src.clients.mysql import AMysqlClientReader
from src.models.database import Reward, User
from src.modules.date import get_first_day_of_cycle


async def get_rewards_service(user: User, cycle_offset: int) -> list[Reward]:
    reader = AMysqlClientReader()

    return await reader.select(
        table=Reward,
        cond_equal=dict(user_id=user.id),
        cond_greater_or_eq=dict(created_at=get_first_day_of_cycle(cycle_offset)),
        cond_less=dict(created_at=get_first_day_of_cycle(cycle_offset - 1)),
    )
