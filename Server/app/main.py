from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, flashcards
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fiszki-Edu API",
    description="Backend systemu do generowania fiszek wspomaganego przez AI Gemini",
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(flashcards.router)

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Witaj w Fiszki-Edu API!",
        "docs": "/docs",
        "version": "1.2.0"
    }