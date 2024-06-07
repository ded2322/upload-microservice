import uuid
import shutil
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import UploadFile
from starlette.responses import JSONResponse
from aiobotocore.session import get_session
from botocore.exceptions import ClientError

from core.config import env
from core.logs.logs import logger_error, logger_response


class Utils:
    VALID_EXTENSIONS = ["mp4", "avi", "wmv"]

    @classmethod
    def check_file(cls, file: UploadFile) -> JSONResponse | None:
        """
        Проверка файла, что он является видео, и размер файла не больше 1 гб
        """
        valid_extension = file.filename.split('.')[-1] in cls.VALID_EXTENSIONS
        # 1 гигабайт, в байтах
        max_size_video = 1_073_741_824

        if file.size > max_size_video:
            logger_error.error(f"Try to load too big file: {file.size}")
            return JSONResponse(status_code=400, content={"error": "File size exceeds 1GB limit"})

        if not valid_extension:
            logger_error.error("Invalid file extension")
            return JSONResponse(status_code=400,
                                content={
                                    "error": f"Invalid file extension. Allowed extensions are: {', '.join(cls.VALID_EXTENSIONS)}"})

        return None

    @classmethod
    def save_video_file(cls, username: str, video: UploadFile) -> Exception | str:
        """
        Сохраняет файл на сервере
        """
        try:
            video_path = f"/core/static/videos/{username}_{uuid.uuid4()}.{video.filename.split('.')[-1]}"

            with open(video_path, "wb+") as file_object:
                shutil.copyfileobj(video.file, file_object)

            return video_path
        except Exception as e:
            logger_error.error(f"Error in save_video_file {str(e)}")

    @classmethod
    def generate_data(cls, video_path: str) -> dict[str, str]:

        current_time = datetime.now().time()
        formatted_time = current_time.strftime("%H:%M:%S")
        time_object = datetime.strptime(formatted_time, "%H:%M:%S").time()

        backed_path = f"https://s3.timeweb.cloud/{env('BUCKET_NAME')}/{video_path.split('/')[-1]}"

        return {"time_object": time_object, "backed_path": backed_path}


class S3:
    def __init__(self):
        self.config = {
            "aws_access_key_id": env("ACCESS_KEY"),
            "aws_secret_access_key": env("SECRET_KEY"),
            "endpoint_url": env("ENDPOINT_URL"),
        }
        self.bucket_name = env("BUCKET_NAME")
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(
            self,
            file_path: str,
    ):
        object_name = file_path.split("/")[-1]  # /users/artem/cat.jpg
        try:
            async with self.get_client() as client:
                with open(file_path, "rb") as file:
                    await client.put_object(
                        Bucket=self.bucket_name,
                        Key=object_name,
                        Body=file,
                    )
                logger_response.info(f"File {object_name} uploaded to {self.bucket_name}")
        except ClientError as e:
            logger_error.error(f"Error uploading file: {e}")

    async def delete_file(self, file_path: str):
        try:
            object_name = file_path.split("/")[-1]
            async with self.get_client() as client:
                await client.delete_object(Bucket=self.bucket_name, Key=object_name)
                logger_response.info(f"File {object_name} deleted from {self.bucket_name}")
        except ClientError as e:
            logger_error.error(f"Error deleting file: {e}")
