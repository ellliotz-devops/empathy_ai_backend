from fastapi import APIRouter
from app.database import conn
from pydantic import BaseModel

class AppointmentCreate(BaseModel):
    patient_id: int
    clinic_id: int
    appointment_time: str
    reason: str
    status: str


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

@router.get("/{appointment_id}")
def get_appointment(appointment_id: int):
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
        WHERE a.id = %s
    """, (appointment_id,))

    row = cursor.fetchone()

    if not row:
        return {"error": "Appointment not found"}

    return {
        "appointment_id": row[0],
        "patient_id": row[1],
        "clinic_id": row[2],
        "appointment_time": row[3],
        "reason": row[4],
        "status": row[5],
        "patient_name": row[6],
        "patient_phone": row[7],
        "patient_email": row[8],
    }

@router.post("/")
def create_appointment(appt: AppointmentCreate):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO appointments (patient_id, clinic_id, appointment_time, reason, status)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """, (
        appt.patient_id,
        appt.clinic_id,
        appt.appointment_time,
        appt.reason,
        appt.status
    ))

    result = cursor.fetchone()
    if not result:
        return {"error": "Failed to create appointment"}
    new_id = result[0]
    conn.commit()

    return {
        "id": new_id,
        "patient_id": appt.patient_id,
        "clinic_id": appt.clinic_id,
        "appointment_time": appt.appointment_time,
        "reason": appt.reason,
        "status": appt.status
    }
