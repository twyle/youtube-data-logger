from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ...extensions.extensions import load_playlist
from celery.result import AsyncResult


playlist = APIRouter(
    prefix='/playlist',
    tags=['Playlists']
)


@playlist.post('/', status_code=201)
async def add_playlist(video_id: str):
    task = load_playlist.delay(video_id)
    return JSONResponse({"task_id": task.id})
    

@playlist.get('/task_status', status_code=200)
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)

@playlist.get('/', status_code=200)
async def get_playlist(playlist_id: str):
    return {'add_playlist': 'True'}


@playlist.post('/videos', status_code=201)
async def add_playlist_videos(playlist_id: str):
    task = load_playlist.delay(playlist_id)
    return JSONResponse({"task_id": task.id})