from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Meme(Base):
    description: Mapped[str] = mapped_column(String(300), unique=False)
    image_path: Mapped[str] = mapped_column(String(200), unique=False)


