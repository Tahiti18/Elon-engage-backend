from fastapi import FastAPI
from app.db import Base, engine
from app.api.routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Elon Engage API", version="0.1.0")
app.include_router(router)
