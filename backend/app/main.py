from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import profile

app = FastAPI(
    title="Merited API",
    description="GitHub profile → recruiter-ready developer evaluation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://merited-chi.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router, prefix="/api/v1", tags=["profile"])


@app.get("/health")
def health():
    return {"status": "ok"}
