from fastapi import FastAPI
from .channel.channel import channel
from .video.video import video
from .playlist.playlist import playlist

def register_routers(app: FastAPI) -> None:
    app.include_router(channel)
    app.include_router(video)
    app.include_router(playlist)