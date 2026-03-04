from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "working"}

class AddRequest(BaseModel):
    a: int
    b: int

@app.post("/add")
async def add(request: AddRequest):
    return {"result": request.a + request.b}