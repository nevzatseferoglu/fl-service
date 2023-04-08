import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.internal.exceptions import (CopySSHKeyToRemoteException,
                                     GenerateSSHKeyPairException)

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
    request: Request, exc: GenerateSSHKeyPairException
) -> JSONResponse:
    logging.error(f"Machine Info: {request.client}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f"GenerateSSHKeyPairException: {exc.detail}"},
    )


@app.exception_handler(CopySSHKeyToRemoteException)
async def copy_ssh_key_to_remote_exception_handler(
    request: Request, exc: CopySSHKeyToRemoteException
) -> JSONResponse:
    logging.error(f"Machine Info: {request.client}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f"CopySSHKeyToRemoteException: {exc.detail}"},
    )
