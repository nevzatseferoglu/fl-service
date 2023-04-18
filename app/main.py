import logging

from fastapi import FastAPI

from .routers import database, ssh

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
app.include_router(database.router)
