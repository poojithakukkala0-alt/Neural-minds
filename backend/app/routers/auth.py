from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from app.auth.security import create_access_token, verify_password, get_password_hash
from app.auth.rbac import get_current_user, get_user_by_email, DEFAULT_USERS, ALLOWED_ROLES
from app.database import db_manager, COLLECTIONS

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])

class LoginRequest(BaseModel):
    email: str
    password: str
    role: Optional[str] = None  # Optional client hint

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str
    department: Optional[str] = "VFSTR Vadlamudi"

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    """Authenticate user with email/password and issue JWT bearer token."""
    user = await get_user_by_email(req.email)
    if not user:
        # Check if role matches a demo seed user
        for u in DEFAULT_USERS:
            if req.role and u["role"] == req.role:
                user = u
                break

    if not user or not verify_password(req.password, user.get("password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials."
        )

    token_data = {
        "sub": user["email"],
        "id": user.get("id", f"usr-{user['email']}"),
        "name": user["name"],
        "role": user["role"],
        "department": user.get("department", "VFSTR Vadlamudi")
    }
    token = create_access_token(token_data)

    safe_user = {
        "id": token_data["id"],
        "name": token_data["name"],
        "email": token_data["sub"],
        "role": token_data["role"],
        "department": token_data["department"]
    }

    return AuthResponse(access_token=token, user=safe_user)

@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest):
    """Register a new student or event organizer. Super Admin registration is strictly prohibited."""
    if req.role not in ["STUDENT", "EVENT_ORGANIZER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public registration is only permitted for 'STUDENT' and 'EVENT_ORGANIZER' roles. Super Admin and HOD accounts must be created by institutional administration."
        )

    existing = await get_user_by_email(req.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    new_user = {
        "id": f"usr-{int(req.email.__hash__() & 0xFFFFFFF)}",
        "name": req.name,
        "email": req.email.lower().strip(),
        "password": get_password_hash(req.password),
        "role": req.role,
        "department": req.department or "VFSTR Vadlamudi",
        "is_active": True
    }

    if db_manager.is_connected and db_manager.db is not None:
        try:
            coll = db_manager.db[COLLECTIONS["users"]]
            await coll.insert_one(new_user)
        except Exception:
            pass

    token_data = {
        "sub": new_user["email"],
        "id": new_user["id"],
        "name": new_user["name"],
        "role": new_user["role"],
        "department": new_user["department"]
    }
    token = create_access_token(token_data)

    safe_user = {
        "id": new_user["id"],
        "name": new_user["name"],
        "email": new_user["email"],
        "role": new_user["role"],
        "department": new_user["department"]
    }

    return AuthResponse(access_token=token, user=safe_user)

@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Retrieve authenticated user's profile and active permissions."""
    return {
        "user": {
            "id": current_user.get("id"),
            "name": current_user.get("name"),
            "email": current_user.get("email"),
            "role": current_user.get("role"),
            "department": current_user.get("department")
        },
        "permissions": {
            "can_modify_master_data": current_user.get("role") == "SUPER_ADMIN",
            "can_plan_events": current_user.get("role") in ["SUPER_ADMIN", "HOD", "EVENT_ORGANIZER"],
            "can_approve_events": current_user.get("role") in ["SUPER_ADMIN", "HOD"],
            "is_student_view": current_user.get("role") == "STUDENT"
        }
    }

@router.get("/roles")
async def list_available_roles():
    """List the 4 supported login roles with descriptions."""
    return {
        "roles": [
            {"role": "SUPER_ADMIN", "title": "Super Admin", "description": "Full Master Data Console & Campus Operations Oversight"},
            {"role": "HOD", "title": "Head of Department", "description": "Department Event Operations, Faculty Coordination & Approvals"},
            {"role": "EVENT_ORGANIZER", "title": "Event Organizer", "description": "AI Event Planning, Blueprint Editing & Event Management"},
            {"role": "STUDENT", "title": "Student Participant", "description": "Campus Events Feed, Registration & Program Schedules"}
        ]
    }
