from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, TIME

from core.database import Base


class Video(Base):
    __tablename__ = 'videos'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(length=30), nullable=False)
    title: Mapped[str] = mapped_column(String(length=50), nullable=False)
    file_path: Mapped[str] = mapped_column(String(length=200), nullable=False)
    data_upload: Mapped[TIME] = mapped_column(TIME, nullable=False)

    def __str__(self):
        return self.title
