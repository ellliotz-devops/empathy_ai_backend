from fastapi import APIRouter
from pydantic import BaseModel
from app.database import conn
from psycopg2 import errors


router = APIRouter(prefix="/clinics", tags=["Clinics"])

# ------------------------
# Pydantic Models
# ------------------------

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


# ------------------------
# GET /clinics
# ------------------------

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


# ------------------------
# GET /clinics/{clinic_id}
# ------------------------

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


# ------------------------
# POST /clinics
# ------------------------

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

# ------------------------
# PUT /clinics/{clinic_id}
# ------------------------

@router.put("/{clinic_id}")
def update_clinic(clinic_id: int, update: ClinicUpdate):
    cursor = conn.cursor()

    # Check if clinic exists
    cursor.execute("SELECT * FROM clinics WHERE id = %s", (clinic_id,))
    existing = cursor.fetchone()

    if not existing:
        return {"error": "Clinic not found"}

    # Build dynamic list of fields to update
    updates = []
    values = []

    for field, value in update.dict().items():
        if value is not None:  
            updates.append(f"{field} = %s")
            values.append(value)

    if not updates:
        return {"message": "No valid fields provided for update"}

    values.append(clinic_id)

    sql = f"UPDATE clinics SET {', '.join(updates)} WHERE id = %s RETURNING id;"
    cursor.execute(sql, values)
    conn.commit()

    return {
        "message": "Clinic updated successfully",
        "clinic_id": clinic_id
    }

# ------------------------
# PATCH /clinics/{clinic_id}
# ------------------------

@router.patch("/{clinic_id}")
def patch_clinic(clinic_id: int, update: ClinicUpdate):
    cursor = conn.cursor()

    # Check if the clinic exists
    cursor.execute("SELECT * FROM clinics WHERE id = %s", (clinic_id,))
    existing = cursor.fetchone()

    if not existing:
        return {"error": "Clinic not found"}

    # Build dynamic update list
    updates = []
    values = []

    for field, value in update.dict().items():
        if value is not None:  # Only update fields that were included and not null
            updates.append(f"{field} = %s")
            values.append(value)

    if not updates:
        return {"message": "No fields provided for update"}

    values.append(clinic_id)

    sql = f"""
        UPDATE clinics
        SET {', '.join(updates)}
        WHERE id = %s
        RETURNING id;
    """

    cursor.execute(sql, values)
    conn.commit()

    return {
        "message": "Clinic partially updated successfully",
        "clinic_id": clinic_id
    }

# ------------------------
# DELETE /clinics/{clinic_id}
# ------------------------

@router.delete("/{clinic_id}")
def delete_clinic(clinic_id: int):
    cursor = conn.cursor()

    # 1. Check if clinic exists
    cursor.execute("SELECT id FROM clinics WHERE id = %s", (clinic_id,))
    existing = cursor.fetchone()

    if not existing:
        cursor.close()
        return {"error": "Clinic not found"}

    # 2. Check users linked to this clinic
    cursor.execute("SELECT COUNT(*) FROM users WHERE clinic_id = %s", (clinic_id,))
    result = cursor.fetchone()
    user_count = result[0] if result else 0

    if user_count > 0:
        cursor.close()
        return {
            "error": "Cannot delete clinic",
            "reason": f"There are {user_count} user(s) assigned to this clinic.",
            "action_required": "Reassign or delete users before deleting this clinic."
        }

    # 3. Check patients linked to the clinic
    cursor.execute("SELECT COUNT(*) FROM patients WHERE clinic_id = %s", (clinic_id,))
    result = cursor.fetchone()
    patient_count = result[0] if result else 0

    if patient_count > 0:
        cursor.close()
        return {
            "error": "Cannot delete clinic",
            "reason": f"There are {patient_count} patient(s) assigned to this clinic.",
            "action_required": "Reassign or delete patients before deleting this clinic."
        }

    # 4. If no dependencies, delete clinic
    cursor.execute("DELETE FROM clinics WHERE id = %s", (clinic_id,))
    conn.commit()
    cursor.close()

    return {
        "message": "Clinic deleted successfully",
        "clinic_id": clinic_id
    }


