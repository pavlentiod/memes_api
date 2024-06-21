from pathlib import Path
from typing import Annotated

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.Storage import s3
from db.models import Meme
from crud.meme.schemas import MemeCreate, MemeUpdate


async def get_meme(session: AsyncSession, meme_id: int) -> Meme | None:
    meme = await session.get(Meme, meme_id)
    return meme


async def get_meme_by_description(session: AsyncSession, description: str) -> Meme | None:
    meme: Meme = await session.scalar(select(Meme).where(Meme.description == description))
    return meme


async def create_meme(session: AsyncSession, meme: MemeCreate) -> Meme:
    in_db: Meme = await session.scalar(select(Meme).where(Meme.description == meme.description))
    if in_db:
        return in_db
    new_meme = Meme(description=meme.description, image_path=meme.image_path)
    session.add(new_meme)
    await session.commit()
    await session.refresh(new_meme)
    return new_meme


async def update_meme(session: AsyncSession, meme_id: int, update: MemeUpdate) -> Meme | None:
    meme: Meme = await session.get(Meme, meme_id)
    if not meme:
        return None
    for name, value in update.dict(exclude_unset=True).items():
        setattr(meme, name, value)
    await session.commit()
    await session.refresh(meme)
    return meme


async def delete_meme(session: AsyncSession, meme_id: int) -> None:
    meme: Meme = await session.get(Meme, meme_id)
    if meme:
        await session.delete(meme)
        await session.commit()

async def image_by_filename(filename: Annotated[str, Path]):
    path = filename
    image = await s3.download_object(path)
    return image

async def get_all(session: AsyncSession) -> list[Meme]:
    stmt = select(Meme).order_by(Meme.id)
    result = await session.execute(stmt)
    memes = result.scalars().all()
    return list(memes)
