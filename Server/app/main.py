from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth

app = FastAPI(title="Fiszki-Edu API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Podpinamy routery
app.include_router(auth.router)

@app.get("/")
def home():
    return {"message": "Serwer Fiszki-Edu działa!"}