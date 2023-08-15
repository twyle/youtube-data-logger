from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ...extensions.extensions import load_channel
from celery.result import AsyncResult


channel = APIRouter(
    prefix='/channel',
    tags=['Channels']
)


@channel.post('/', status_code=201)
async def add_channel(video_id: str):
    task = load_channel.delay(video_id)
    return JSONResponse({"task_id": task.id})
    

@channel.get('/task_status', status_code=200)
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)

@channel.get('/', status_code=200)
async def get_channel(channel_id: str):
    return {'channel': 'True'}