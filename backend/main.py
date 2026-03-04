from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.document_loaders import YoutubeLoader

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

class GetTranscriptRequest(BaseModel):
    url: str

@app.post("/get_transcript")
async def get_transcript(request: GetTranscriptRequest):
    loader = YoutubeLoader.from_youtube_url(request.url)
    docs = loader.load()
    transcript = "\n".join([doc.page_content for doc in docs])
    return {"transcript": transcript}