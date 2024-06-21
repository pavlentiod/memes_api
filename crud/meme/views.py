import uuid
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.Storage.aws_s3 import S3
from db.models import db_helper, Meme
from . import crud
from .crud import image_by_filename
from .schemas import MemeCreate, MemeUpdate
from fastapi_pagination import Page, add_pagination, paginate

router = APIRouter()
s3 = S3()


@router.post("/create", name="Добавление мемов")
async def create_meme(
        description: str,
        image: UploadFile = File(...),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    format = image.filename.split(".")[-1]
    image.filename = f"{uuid.uuid4()}.{format}"
    await s3.upload(file=image)
    db_meme = await crud.get_meme_by_description(session=session, description=description)
    if db_meme:
        raise HTTPException(status_code=400, detail="Мем уже существует")

    image_path = f"{image.filename}"  # Adjust the path as necessary

    meme_data = MemeCreate(description=description, image_path=image_path)
    new_meme = await crud.create_meme(session, meme_data)
    return new_meme


@router.get('/read/{meme_id}', name="Чтение существующих мемов")
async def get_meme(meme_id: int, session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    meme: Meme | None = await crud.get_meme(session, meme_id=meme_id)
    if meme:
        image = await s3.download_object(meme.image_path)
        return Response(content=image, media_type="image/jpg", headers={"description":meme.description, "image_path": meme.image_path, "id": str(meme.id)})


    raise HTTPException(status_code=404, detail="Мем не существует")


@router.patch("/update/{meme_id}", name="Обновление существующих мемов")
async def update_meme(
        meme_id: int,
        description: str = None,
        image: UploadFile = File(None),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    meme = await crud.get_meme(session=session, meme_id=meme_id)
    if not meme:
        raise HTTPException(status_code=404, detail="Мем не существует")

    update_data = {}
    if description:
        update_data["description"] = description
    if image:
        format = image.filename.split(".")[-1]
        image.filename = f"{uuid.uuid4()}.{format}"
        await s3.upload(file=image)
        update_data["image_path"] = image.filename

    meme_update = MemeUpdate(**update_data)
    updated_meme = await crud.update_meme(session, meme_id, meme_update)
    return updated_meme


@router.delete("/delete/{meme_id}", status_code=status.HTTP_204_NO_CONTENT, name="Удаление существующих мемов")
async def delete_meme(
        meme_id: int,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
) -> None:
    meme = await crud.get_meme(session=session, meme_id=meme_id)
    if not meme:
        raise HTTPException(status_code=404, detail="Мем не существует")
    await crud.delete_meme(session=session, meme_id=meme_id)

@router.get("/all", name="Все мемы")
async def get_all(session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    return await crud.get_all(session=session)

@router.get('/pages', name="Просмотр мемов с пагинацией")
async def meme_pages(session: AsyncSession = Depends(db_helper.scoped_session_dependency)) -> Page[MemeCreate]:
    memes = await crud.get_all(session=session)
    return paginate(memes)

add_pagination(router)