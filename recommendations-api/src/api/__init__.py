from fastapi import FastAPI

from .routes import router

app = FastAPI()
app.include_router(router)


@app.get("/health")
def healthcheck():
    return 200
