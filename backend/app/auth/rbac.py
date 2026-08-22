from typing import List, Optional
from fastapi import Depends, HTTPException, status, Header
from app.auth.security import decode_access_token
from app.database import db_manager, COLLECTIONS

# ONLY 4 Supported Campus Roles
ALLOWED_ROLES = ["SUPER_ADMIN", "HOD", "EVENT_ORGANIZER", "STUDENT"]

# Canonical Seed Users
DEFAULT_USERS = [
    {
        "id": "usr-superadmin",
        "name": "Dr. System Administrator",
        "email": "superadmin@vignan.ac.in",
        "password": "vignan_admin_2026",
        "role": "SUPER_ADMIN",
        "department": "University Administration",
        "is_active": True
    },
    {
        "id": "usr-hod-cse",
        "name": "Dr. Venkatarama Phani Kumar",
        "email": "hod.cse@vignan.ac.in",
        "password": "vignan_hod_2026",
        "role": "HOD",
        "department": "Computer Science and Engineering (CSE)",
        "is_active": True
    },
    {
        "id": "usr-organizer",
        "name": "Campus Event Lead (SAC)",
        "email": "organizer@vignan.ac.in",
        "password": "vignan_event_2026",
        "role": "EVENT_ORGANIZER",
        "department": "Student Activity Center (SAC)",
        "is_active": True
    },
    {
        "id": "usr-student",
        "name": "Sai Krishna (Student)",
        "email": "student@vignan.ac.in",
        "password": "vignan_student_2026",
        "role": "STUDENT",
        "department": "CSE - 3rd Year",
        "is_active": True
    }
]

async def get_user_by_email(email: str) -> Optional[dict]:
    """Retrieve user from MongoDB or fallback seed users."""
    if db_manager.is_connected and db_manager.db is not None:
        try:
            coll = db_manager.db[COLLECTIONS["users"]]
            user = await coll.find_one({"email": email.lower().strip()}, {"_id": 0})
            if user:
                return user
        except Exception:
            pass

    for u in DEFAULT_USERS:
        if u["email"].lower() == email.lower().strip():
            return u
    return None

async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> dict:
    """Extracts and validates current authenticated user from Bearer token."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing. Please log in.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Bearer token required.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired or invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    email = payload["sub"]
    user = await get_user_by_email(email)
    if not user:
        # Construct ephemeral user from token claims if database record missing
        return {
            "id": payload.get("id", f"usr-{email}"),
            "name": payload.get("name", email.split("@")[0]),
            "email": email,
            "role": payload.get("role", "STUDENT"),
            "department": payload.get("department", "VFSTR Vadlamudi")
        }

    return user

def require_role(allowed_roles: List[str]):
    """
    Role Authorization Dependency Factory.
    Enforces strict RBAC on the backend and raises 403 Forbidden for unauthorized requests.
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Forbidden: Role '{user_role}' is not authorized to access this resource. Required one of: {allowed_roles}"
            )
        return current_user
    return role_checker
