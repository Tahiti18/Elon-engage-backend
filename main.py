# main.py  — FastAPI app with CORS enabled
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import Base, engine
from app.api.routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Elon Engage API", version="0.1.0")

# CORS — open for testing; lock down origins later if you want
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
