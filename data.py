import os
import uuid

from crud.meme.schemas import MemeCreate
from db.Storage import S3
from db.models import db_helper
from crud.meme.crud import create_meme
s3 = S3()


async def add_data():
    images = os.listdir("./memes_data")
    names = []

    # print(names)
    async with db_helper.session_factory() as session:
        for image in images:
            format = image.split(".")[-1]
            filename = f"{uuid.uuid4()}.{format}"
            os.rename(f"./memes_data/{image}", f"./memes_data/{filename}")
            await create_meme(session=session, meme=MemeCreate(description=f"text number {images.index(image)}", image_path=image))

# print(images)
