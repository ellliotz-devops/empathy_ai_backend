from fastapi import FastAPI
from app.database import connect_db
from app.routers import appointments
from app.routers import patients
from app.routers import messages


app = FastAPI(title="Empathy AI Backend")

@app.on_event("startup")
def startup():
    connect_db()

app.include_router(appointments.router)
app.include_router(patients.router)
app.include_router(messages.router)

@app.get("/")
def root():
    return {"message": "Empathy AI Backend is running!"}
