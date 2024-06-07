from fastapi import APIRouter, BackgroundTasks, UploadFile, Form, File
from starlette.responses import JSONResponse

from core.dao.video_dao import VideoDao
from core.utils.video_utils import Utils, S3
from core.logs.logs import logger_response

router = APIRouter(
    prefix="/upload-service",
    tags=["routers"],
)


@router.post("/", status_code=201,summary="Upload a video-file" )
async def upload_video_file(background_tasks: BackgroundTasks,
                            title: str = Form(...), username: str = Form(...),
                            file: UploadFile = File(...)):
    """
    Позволяет загружать видео.
    Доступные расширения: mp4, avi, wmv
    Максимальный размер файла: 1 гигабайт
    """
    logger_response.info("Upload video-file")

    error_response = Utils.check_file(file)
    if error_response:
        return error_response

    video_path = Utils.save_video_file(username=username, video=file)
    s3 = S3()
    background_tasks.add_task(s3.upload_file, video_path)

    data_db = Utils.generate_data(video_path)

    await VideoDao.insert_data(username=username, title=title,
                               file_path=data_db["backed_path"],
                               data_upload=data_db["time_object"])

    return JSONResponse(status_code=200, content={"message": "Video send to server"})


@router.post("/delete-video", status_code=200, summary="Delete a video-file")
async def delete_video(background_tasks: BackgroundTasks, title: str = Form(...)):
    """
    Удаляет видео-файл из базы данных и s3 хранилища
    Происходит поиск по названию видео
    """
    video = await VideoDao.found_one_or_none(title=title)
    if not video:
        return JSONResponse(status_code=404, content={"message": "Video not found"})

    await VideoDao.delete_data(id=video.id)
    s3 = S3()
    background_tasks.add_task(s3.delete_file, video.file_path)

    return JSONResponse(status_code=200, content={"message": "Video deleted"})
