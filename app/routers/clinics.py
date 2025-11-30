from fastapi import APIRouter
from pydantic import BaseModel
from app.database import conn

router = APIRouter(prefix="/clinics", tags=["Clinics"])

class ClinicCreate(BaseModel):
    name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    timezone: str | None = "UTC"

class ClinicUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    timezone: str | None = None


@router.get("/")
def get_clinics():
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, address, phone, email, timezone, created_at
        FROM clinics
        ORDER BY name ASC;
    """)

    rows = cursor.fetchall()

    return [
        {
            "id": r[0],
            "name": r[1],
            "address": r[2],
            "phone": r[3],
            "email": r[4],
            "timezone": r[5],
            "created_at": r[6],
        }
        for r in rows
    ]


@router.get("/{clinic_id}")
def get_clinic(clinic_id: int):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, address, phone, email, timezone, created_at
        FROM clinics
        WHERE id = %s;
    """, (clinic_id,))

    row = cursor.fetchone()

    if not row:
        return {"error": "Clinic not found"}

    return {
        "id": row[0],
        "name": row[1],
        "address": row[2],
        "phone": row[3],
        "email": row[4],
        "timezone": row[5],
        "created_at": row[6],
    }


@router.post("/")
def create_clinic(clinic: ClinicCreate):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clinics (name, address, phone, email, timezone)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """, (
        clinic.name,
        clinic.address,
        clinic.phone,
        clinic.email,
        clinic.timezone,
    ))

    result = cursor.fetchone()
    if not result:
        raise Exception("Database did not return an ID for the new clinic")

    new_id = result[0]
    conn.commit()

    return {
        "id": new_id,
        **clinic.dict()
    }


@router.put("/{clinic_id}")
def update_clinic(clinic_id: int, update: ClinicUpdate):
    cursor = conn.cursor()

    # Fetch existing clinic
    cursor.execute("SELECT * FROM clinics WHERE id = %s", (clinic_id,))
    existing = cursor.fetchone()

    if not existing:
        return {"error": "Clinic not found"}

    # Build dynamic update fields
    updates = []
    values = []

    for field, value in update.dict().items():
        if value is not None:  # only update fields provided
            updates.append(f"{field} = %s")
            values.append(value)

    if not updates:
        return {"message": "No valid fields provided for update"}

    values.append(clinic_id)

    sql = f"UPDATE clinics SET {', '.join(updates)} WHERE id = %s RETURNING id;"
    cursor.execute(sql, values)

    conn.commit()

    return {"message": "Clinic updated successfully", "clinic_id": clinic_id}
