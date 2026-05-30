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
    allow_origins=[
        "http://localhost:3000",
        "https://merited-phi.vercel.app",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router, prefix="/api/v1", tags=["profile"])

@app.get("/health")
def health():
    return {"status": "ok"}