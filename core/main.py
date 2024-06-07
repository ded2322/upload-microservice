from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from core.routers.router import router

app = FastAPI(
    title="Upload Service",
    description="Service for uploading video-files",
    version="1.0",
)
app.mount("/static", StaticFiles(directory="/core/static"), "static")

app.include_router(router)
