
from fastapi import FastAPI
from dotenv import load_dotenv
from app.core.db import Base, engine
from app.api.v1.posts.router import router as posts_router

load_dotenv()

# up environment
# pip install fastapi uvicorn
# source venv/Scripts/activate
# uvicorn main:app --reload
# deactivate

def create_app() -> FastAPI:
    app = FastAPI(
        title="Mini Blog", 
        description="This is a simple blog API", 
        version="1.0.0"
    )
    Base.metadata.create_all(bind=engine)  # development
    app.include_router(posts_router)
    return app

app = create_app()