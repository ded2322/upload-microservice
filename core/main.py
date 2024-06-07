from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from core.routers.router import router

app = FastAPI(
    title="Upload Service",
    description="Service for uploading video-files",
    version="1.0",
)
app.mount("/static", StaticFiles(directory="/core/static"), "static")

app.include_router(router)

origins = ["localhost"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)