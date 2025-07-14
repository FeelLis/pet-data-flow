import uvicorn

from api import app
from config import config
from utils.logger import logger

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
