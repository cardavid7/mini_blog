
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from app.core.db import Base, engine
from app.api.v1.posts.router import router as posts_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.uploads.router import router as upload_router
from app.api.v1.tags.router import router as tags_router
from app.api.v1.categories.router import router as categories_router

load_dotenv()

MEDIA_DIR = "app/media"

# up environment
# pip install fastapi[standard]                 # install fastapi and all dependencies
# source .venv/Scripts/activate                 # activate virtual environment
# uvicorn app.main:app --reload                 # run the server with hot reload
# fastapi dev app/main.py                       # run the server with hot reload
# deactivate                                    # deactivate virtual environment

# run seed scripts
# python3 -m app.seeds all
# python3 -m app.seeds users
# python3 -m app.seeds categories
# python3 -m app.seeds tags

def create_app() -> FastAPI:
    app = FastAPI(
        title="Mini Blog", 
        description="This is a simple blog API", 
        version="1.0.0"
    )
    Base.metadata.create_all(bind=engine)  # development
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(posts_router)
    app.include_router(tags_router)
    app.include_router(upload_router)
    app.include_router(categories_router)
    
    os.makedirs(MEDIA_DIR, exist_ok=True)
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

    return app

app = create_app()