from fastapi import APIRouter, Depends
from src.logger import get_logger
from src.models.database import User
from src.modules.authentification import get_current_user
from src.modules.normalize_url import normalize_github_url

from .models import GetRewardsResponseItem
from .service import get_rewards_service

router = APIRouter(prefix="/rewards")
logger = get_logger()


@router.get("", response_model=list[GetRewardsResponseItem])
async def get_rewards(
    cycle_offset: int, user: User = Depends(get_current_user)
) -> list[GetRewardsResponseItem]:
    logger.info(f"GET patch_task, {cycle_offset=}")

    rewards = await get_rewards_service(user, cycle_offset)

    return [
        GetRewardsResponseItem(
            pr_link=r.pr_link,
            pr_number=gu.pull_request_number if gu else None,
            repo=gu.repo if gu else None,
            points=r.points,
            was_quick_review=r.was_quick_review,
            rewarded_at=r.created_at,
            creator_public_id=r.creator_public_id,
            creator_user_name=r.creator_user_name,
            review_priority=r.review_priority,
            lines_of_code=r.lines_of_code,
        )
        for r, gu in [(r, normalize_github_url(r.pr_link)) for r in rewards]
    ]
