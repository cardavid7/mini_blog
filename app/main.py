
from fastapi import FastAPI
from dotenv import load_dotenv
from app.core.db import Base, engine
from app.api.v1.posts.router import router as posts_router
from app.api.v1.auth.router import router as auth_router

load_dotenv()

# up environment
# pip install fastapi[standard]                 # install fastapi and all dependencies
# source .venv/Scripts/activate                 # activate virtual environment
# uvicorn app.main:app --reload                 # run the server with hot reload
# fastapi dev app/main.py                       # run the server with hot reload
# deactivate                                    # deactivate virtual environment


def create_app() -> FastAPI:
    app = FastAPI(
        title="Mini Blog", 
        description="This is a simple blog API", 
        version="1.0.0"
    )
    Base.metadata.create_all(bind=engine)  # development
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(posts_router)
    return app

app = create_app()