from fastapi import APIRouter
from app.database import conn

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.get("/")
def get_appointments():
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            a.id AS appointment_id,
            a.patient_id,
            a.clinic_id,
            a.appointment_time,
            a.reason,
            a.status,
            p.full_name AS patient_name,
            p.phone AS patient_phone,
            p.email AS patient_email
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        ORDER BY a.appointment_time ASC;
    """)
    rows = cursor.fetchall()

    return [
        {
            "appointment_id": r[0],
            "patient_id": r[1],
            "clinic_id": r[2],
            "appointment_time": r[3],
            "reason": r[4],
            "status": r[5],
            "patient_name": r[6],
            "patient_phone": r[7],
            "patient_email": r[8],
        }
        for r in rows
    ]
