from backend.app.core.db import AsyncSessionLocal
from backend.app.models.user import UserTable
from sqlmodel import update
from backend.app.crud.base import BaseCURD


class UserCRUD(BaseCURD[UserTable]):

    @staticmethod
    async def reset_users_score() -> None:
        """
        重置用户积分为30分
        """
        async with AsyncSessionLocal() as session:
            sql = update(UserTable).values(score=30)
            session.execute(sql)
            session.commit()


crud_user = UserCRUD(UserTable)
