from fastapi import APIRouter, UploadFile

from app.routers.docker.docker import router

# Have in mind that this means that the whole contents will be stored in memory.
# This will work well for small files.

# take ip address
# source files which will be deployed
# entrypointCmd of the image
# data source directory as an absolute path (which will be deployed)
# platform information (pytorch, terserflow)

router = APIRouter(
    prefix="/docker",
    tags=["docker"],
)


@router.post("/upload-source-files/")
async def create_upload_file(
    files: list[UploadFile],
    # files: Annotated[list[UploadFile], list[File(description="A file read as UploadFile")]],
):
    return [file.filename for file in files]
