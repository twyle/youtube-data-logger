from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ...extensions.extensions import load_video
from celery.result import AsyncResult


video = APIRouter(
    prefix='/video',
    tags=['Videos']
)

@video.post('/', status_code=201)
async def add_video(video_id: str):
    task = load_video.delay(video_id)
    return JSONResponse({"task_id": task.id})
    

@video.get('/', status_code=200)
async def get_video(task_id: str):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)