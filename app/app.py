from fastapi import FastAPI
import logging
from dotenv import load_dotenv
import sys

# from processors.linkedin import upload

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)-9s %(asctime)s - %(name)s - %(message)s")
LOGGER = logging.getLogger(__name__)


app = FastAPI(debug=True)
# app.include_router(populate.router)

# @app.post("/upload-linkedin/")
# async def upload_linkedin():
#     upload()

