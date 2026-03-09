# YouTube Q&A

Chat with any YouTube video. Paste a URL, load the transcript, and ask questions about the content.

## Tech Stack

- **Frontend**: Next.js, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI, LangChain, FAISS, OpenAI

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file with your OpenAI key:

```
OPENAI_API_KEY=your_key_here
```

Run the server:

```bash
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

## How It Works

1. Paste a YouTube URL and click **Load** to fetch and embed the transcript
2. Ask questions in the chat — the app retrieves relevant transcript chunks and sends them along with chat history to the LLM for context-aware answers
