from fastapi import FastAPI
from .routers.register_routers import register_routers

def create_app():
    app = FastAPI()
    register_routers(app)
    
    @app.get('/')
    async def get():
        return {'message': 'hello world!'}
    
    return app