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
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"message": "working"}



class GetTranscriptRequest(BaseModel):
    url: str

@app.post("/get_transcript")
async def get_transcript(request: GetTranscriptRequest):
    try:
        loader = YoutubeLoader.from_youtube_url(request.url)
        docs = loader.load()
        if not docs:
            raise ValueError("No transcript found for this video")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
        texts = text_splitter.split_text(docs[0].page_content)
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vector_store = FAISS.from_texts(texts, embeddings)
        video_id = request.url.split("v=")[-1].split("&")[0]
        vector_stores[video_id] = vector_store
        return {"video_id": video_id}
    except Exception as e:
        print(f"Error in get_transcript: {e}")
        raise HTTPException(status_code=400, detail=str(e))

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    video_id: str
    question: str
    history: list[ChatMessage] = []

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        vector_store = vector_stores[request.video_id]
        docs = vector_store.similarity_search(request.question, k=4)
        context = "\n\n".join(doc.page_content for doc in docs)

        messages = [
            ("system", "Answer based on this YouTube transcript context. Be concise and helpful.\n\n{context}"),
        ]
        for msg in request.history:
            messages.append((msg.role, msg.content))
        messages.append(("user", "{question}"))

        prompt = ChatPromptTemplate.from_messages(messages)
        llm = ChatOpenAI(model="gpt-4o-mini")
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"context": context, "question": request.question})
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

