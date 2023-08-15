from sqlalchemy.orm import Session
from .models.channel import Channel
from sqlalchemy.exc import IntegrityError

def add_channel(session: Session, channel: Channel):
    with session() as db:
        try:
            db.add(channel)
            db.commit()
            db.refresh(channel)
        except IntegrityError:
            return None
        else:
            return channel