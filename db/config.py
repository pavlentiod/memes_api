from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
import os


# load_dotenv()
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent
load_dotenv()

class DbSettings(BaseModel):
    username: str = os.getenv("DATABASE_USER")
    password: str = os.getenv("DATABASE_PASSWORD")
    host: str = os.getenv("DATABASE_HOST")
    name: str = os.getenv("DATABASE_NAME")
    echo: bool = False

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.username}:{self.password}@db:2222/{self.name}"
        # return f"postgresql+asyncpg://{self.username}:{self.password}@localhost:5432/{self.name}"


class Settings(BaseSettings):
    db: DbSettings = DbSettings()


class AWS_Settings(BaseSettings):
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_DEFAULT_REGION: str = os.getenv("AWS_DEFAULT_REGION")
    AWS_BUCKET_NAME: str = os.getenv("AWS_BUCKET_NAME")
#

settings = Settings()
aws_settings = AWS_Settings()
