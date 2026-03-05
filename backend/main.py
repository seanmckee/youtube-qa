from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

vector_stores = {}

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
    try:
        loader = YoutubeLoader.from_youtube_url(request.url)
        docs = loader.load()[0].page_content
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
        texts = text_splitter.split_text(docs)
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vector_store = FAISS.from_texts(texts, embeddings)
        video_id = request.url.split("v=")[1]
        vector_stores[video_id] = vector_store      
        return {"video_id": video_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class ChatRequest(BaseModel):
    video_id: str
    question: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        vector_store = vector_stores[request.video_id]
        docs = vector_store.similarity_search(request.question, k=4)
        context = "\n\n".join(doc.page_content for doc in docs)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Answer based on this transcript context:\n\n{context}"),
            ("user", "{question}"),
        ])
        llm = ChatOpenAI(model="gpt-4o-mini")
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"context": context, "question": request.question})
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

