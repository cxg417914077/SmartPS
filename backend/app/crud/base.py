from typing import TypeVar, Generic, Optional, Type, Sequence
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel, select


ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseCURD(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        # 在实例化时，将具体的模型类存为实例属性 self.model
        self.model = model

    async def get(self, session: AsyncSession, _id: int) -> Optional[ModelType]:
        return await session.get(self.model, _id)

    async def get_by(self, session: AsyncSession, **kwargs) -> Optional[ModelType]:
        stmt = select(self.model)
        # 动态构建 where 条件
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_multi_by(self, session: AsyncSession, **kwargs) -> Sequence[ModelType]:
        stmt = select(self.model)
        # 动态构建 where 条件
        for key, value in kwargs.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update(self, session: AsyncSession, _id: int, **kwargs) -> Optional[ModelType]:
        obj = await self.get(session, _id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            await session.commit()
            await session.refresh(obj)
            return obj
        else:
            return None

    async def delete(self, session: AsyncSession, _id: int) -> None:
        obj = await self.get(session, _id)
        if obj:
            await session.delete(obj)
            await session.commit()
        return obj

    async def create(self, session: AsyncSession, **kwargs) -> Optional[ModelType]:
        obj = self.model(**kwargs)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj
