
import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.internal.utils.exceptions import GenerateSSHKeyPairException
from .routers import ssh

logging.basicConfig(
    filename="uvicorn.log",
    filemode="a",
    format="%(asctime)s:%(levelname)s:%(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
)

logging.info("Starting a fresh uvicorn!")

app = FastAPI(debug=True)

app.include_router(ssh.router)

@app.exception_handler(GenerateSSHKeyPairException)
async def generate_ssh_key_pair_failed_exception_handler(
    request: Request,
    exc: GenerateSSHKeyPairException):
    
    logging.error(f"Machine Info: {request.client}") 
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": f"GenerateSSHKeyPairException: {exc.name}"
        }
    )