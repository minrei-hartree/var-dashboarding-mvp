from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import var, utils

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(var.router)
app.include_router(utils.router)

@app.get("/")
async def root():
    return {"message": "Hello World!"}