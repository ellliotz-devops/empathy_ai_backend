from fastapi import APIRouter
from app.database import conn
from pydantic import BaseModel

router = APIRouter(prefix="/messages", tags=["Messages"])

class MessageCreate(BaseModel):
    clinic_id: int
    patient_id: int
    content: str
    sender: str  # "patient" or automatically "clinic"


@router.get("/")
def get_all_messages():
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            id,
            clinic_id,
            patient_id,
            sender,
            content,
            created_at
        FROM messages
        ORDER BY created_at DESC;
    """)

    rows = cursor.fetchall()

    return [
        {
            "id": r[0],
            "clinic_id": r[1],
            "patient_id": r[2],
            "sender": r[3],
            "content": r[4],
            "created_at": r[5],
        }
        for r in rows
    ]

@router.get("/patient/{patient_id}")
def get_messages_for_patient(patient_id: int):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            id,
            clinic_id,
            patient_id,
            sender,
            content,
            created_at
        FROM messages
        WHERE patient_id = %s
        ORDER BY created_at ASC;
    """, (patient_id,))

    rows = cursor.fetchall()

    return [
        {
            "id": r[0],
            "clinic_id": r[1],
            "patient_id": r[2],
            "sender": r[3],
            "content": r[4],
            "created_at": r[5],
        }
        for r in rows
    ]
@router.post("/")
def create_message(msg: MessageCreate):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (clinic_id, patient_id, sender, content)
        VALUES (%s, %s, %s, %s)
        RETURNING id, created_at;
    """, (
        msg.clinic_id,
        msg.patient_id,
        msg.sender,
        msg.content
    ))

    result = cursor.fetchone()
    
    if not result:
        return {"error": "Failed to create message"}

    new_id, created_at = result
    conn.commit()

    return {
        "id": new_id,
        "clinic_id": msg.clinic_id,
        "patient_id": msg.patient_id,
        "sender": msg.sender,
        "content": msg.content,
        "created_at": created_at
    }

