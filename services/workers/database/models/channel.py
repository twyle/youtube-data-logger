from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base
from datetime import datetime


class Channel(Base):
    __tablename__ = 'channels'
    
    channel_id: Mapped[str] = mapped_column(primary_key=True)
    channel_title: Mapped[str]
    published_at: Mapped[datetime]
    custom_url: Mapped[str]
    channel_description: Mapped[str]
    channel_thumbnail: Mapped[str]
    views_count: Mapped[int]
    videos_count: Mapped[int]
    subscribers_count: Mapped[int] = 0