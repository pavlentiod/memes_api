from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from crud import router
from data import add_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    await add_data()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router=router)


@app.get("/")
async def hello_index():

    return {
        "Docs": f"http://127.0.0.1:8002/docs",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8003)
