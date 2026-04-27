import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_pipeline import LegalRAG
import uvicorn

app = FastAPI(title="LegalEase BD API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*", # প্রোডাকশনের জন্য এটি সব ডোমেইন থেকে রিকোয়েস্ট এক্সেপ্ট করবে
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag: LegalRAG | None = None


@app.on_event("startup")
def startup_event():
    global rag
    try:
        rag = LegalRAG()
        print("✅ LegalRAG ready")
    except Exception as e:
        print(f"❌ LegalRAG init failed: {e}")
        traceback.print_exc()


# ─── Models ───────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str

class Source(BaseModel):
    source: str
    section: str

class AnswerDetail(BaseModel):
    legalExplanation: str
    userRights: str
    nextSteps: list[str]
    formalVersion: str

class ChatResponse(BaseModel):
    question: str
    answer: AnswerDetail
    sources: list[Source]
    confidence: float
    warning: str


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "LegalEase BD is running ✅"}


@app.get("/health")
def health():
    return {
        "status":     "ok" if rag is not None else "error",
        "rag_loaded": rag is not None,
        "llm":        "mistral",
        "embeddings": "nomic-embed-text",
        "db":         "chromadb",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if rag is None:
        raise HTTPException(503, "RAG not initialised. Check server logs.")
    try:
        return rag.query(req.message)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))


@app.post("/ingest")
def ingest_documents():
    if rag is None:
        raise HTTPException(503, "RAG not initialised. Check server logs.")
    try:
        count = rag.ingest_documents()
        return {"message": f"Ingested {count} chunks successfully"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)