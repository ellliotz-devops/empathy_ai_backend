from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from app.database import conn


router = APIRouter(prefix="/users", tags=["Users"])

# -------------------------
# Pydantic Models
# -------------------------

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str | None = None
    role: str        # "admin" or "staff"
    clinic_id: int

class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    role: str | None = None
    clinic_id: int | None = None


# -------------------------
# POST /users  (Create User)
# -------------------------

@router.post("/")
def create_user(user: UserCreate):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (full_name, email, phone_number, role, clinic_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """, (
        user.full_name,
        user.email,
        user.phone_number,
        user.role,
        user.clinic_id
    ))

    result = cursor.fetchone()
    if not result:
        return {"error": "Failed to create user"}

    new_id = result[0]
    conn.commit()

    return {"id": new_id, **user.dict()}

# -------------------------
# GET /users  (Create User)
# -------------------------

@router.get("/")
def get_users():
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, full_name, email, phone_number, role, clinic_id, created_at
        FROM users
        ORDER BY id ASC;
    """)
    rows = cursor.fetchall()
    cursor.close()

    return [
        {
            "id": r[0],
            "full_name": r[1],
            "email": r[2],
            "phone_number": r[3],
            "role": r[4],
            "clinic_id": r[5],
            "created_at": r[6],
        }
        for r in rows
    ]

# -------------------------
# GET /users/{user_id}  (Get User)
# -------------------------

@router.get("/{user_id}")
def get_user(user_id: int):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, full_name, email, phone_number, role, clinic_id, created_at
        FROM users
        WHERE id = %s;
    """, (user_id,))

    row = cursor.fetchone()
    cursor.close()

    if not row:
        return {"error": "User not found"}

    return {
        "id": row[0],
        "full_name": row[1],
        "email": row[2],
        "phone_number": row[3],
        "role": row[4],
        "clinic_id": row[5],
        "created_at": row[6],
    }