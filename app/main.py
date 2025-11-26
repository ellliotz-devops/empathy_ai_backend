from fastapi import FastAPI
from .database import connect_db
from .routers import appointments

app = FastAPI(title="Empathy AI Backend")

@app.on_event("startup")
def startup():
    connect_db()

app.include_router(appointments.router)

@app.get("/")
def root():
    return {"message": "Empathy AI Backend is running!"}
