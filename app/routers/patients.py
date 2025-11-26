from fastapi import APIRouter
from app.database import conn
from pydantic import BaseModel

class PatientCreate(BaseModel):
    full_name: str
    phone: str
    email: str
    date_of_birth: str
    clinic_id: int

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("/")
@router.post("/")
def create_patient(patient: PatientCreate):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO patients (full_name, phone, email, date_of_birth, clinic_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """, (patient.full_name, patient.phone, patient.email, patient.date_of_birth, patient.clinic_id))

    new_id = cursor.fetchone()[0]
    conn.commit()

    return {
        "id": new_id,
        "full_name": patient.full_name,
        "phone": patient.phone,
        "email": patient.email,
        "date_of_birth": patient.date_of_birth,
        "clinic_id": patient.clinic_id
    }

def get_patients():
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            id,
            full_name,
            phone,
            email,
            date_of_birth,
            clinic_id
        FROM patients
        ORDER BY full_name ASC;
    """)
    
    rows = cursor.fetchall()

    return [
        {
            "id": r[0],
            "full_name": r[1],
            "phone": r[2],
            "email": r[3],
            "date_of_birth": r[4],
            "clinic_id": r[5]
        }
        for r in rows
    ]

@router.get("/{patient_id}")
def get_patient(patient_id: int):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, full_name, phone, email, date_of_birth, clinic_id FROM patients WHERE id = %s",
        (patient_id,)
    )
    result = cursor.fetchone()
    cursor.close()

    if not result:
        return {"error": "Patient not found"}

    return {
        "id": result[0],
        "full_name": result[1],
        "phone": result[2],
        "email": result[3],
        "date_of_birth": result[4],
        "clinic_id": result[5]
    }

@router.get("/{patient_id}")
def get_patient(patient_id: int):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            id,
            full_name,
            phone,
            email,
            date_of_birth,
            clinic_id
        FROM patients
        WHERE id = %s
    """, (patient_id,))

    row = cursor.fetchone()

    if not row:
        return {"error": "Patient not found"}

    return {
        "id": row[0],
        "full_name": row[1],
        "phone": row[2],
        "email": row[3],
        "date_of_birth": row[4],
        "clinic_id": row[5]
    }
