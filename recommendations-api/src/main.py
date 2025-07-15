from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api import router
from utils.rabbitmq.publisher import publisher


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with publisher:
        yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
