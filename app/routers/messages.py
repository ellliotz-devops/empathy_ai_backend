from fastapi import APIRouter
from app.database import conn

router = APIRouter(prefix="/messages", tags=["Messages"])


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
