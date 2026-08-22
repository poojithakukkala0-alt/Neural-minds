from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.auth.rbac import require_role
from app.database import db_manager, COLLECTIONS
from app.seed.campus_seed import (
    SEED_VENUES,
    SEED_RESOURCES,
    SEED_LEADERSHIP,
    SEED_BLOCKS
)

router = APIRouter(
    prefix="/admin",
    tags=["Super Admin Master Data Console"],
    dependencies=[Depends(require_role(["SUPER_ADMIN"]))]
)

# In-memory stores for runtime master data modifications when MongoDB is in standby mode
runtime_venues = [dict(v) for v in SEED_VENUES]
runtime_resources = [dict(r) for r in SEED_RESOURCES]
runtime_faculty = [
    {
        "id": f"fac-{idx+1}",
        "name": l["name"],
        "designation": l["role"],
        "department": l["department"],
        "email": f"faculty.{idx+1}@vignan.ac.in",
        "qualifications": l.get("qualifications", "Ph.D."),
        "status": "Active"
    }
    for idx, l in enumerate(SEED_LEADERSHIP)
]
runtime_departments = [
    {"id": "dept-cse", "name": "Computer Science and Engineering", "code": "CSE", "hod": "Dr. Venkatarama Phani Kumar Sistla", "faculty_count": 48},
    {"id": "dept-ece", "name": "Electronics and Communication Engineering", "code": "ECE", "hod": "Dr. N. Usha Rani", "faculty_count": 42},
    {"id": "dept-eee", "name": "Electrical and Electronics Engineering", "code": "EEE", "hod": "Dr. G. Srinivasa Rao", "faculty_count": 30},
    {"id": "dept-mech", "name": "Mechanical Engineering", "code": "MECH", "hod": "Dr. M. Rama Krishna", "faculty_count": 32},
    {"id": "dept-it", "name": "Information Technology", "code": "IT", "hod": "Dr. A. Rama Swamy Reddy", "faculty_count": 28},
    {"id": "dept-chem", "name": "Chemical Engineering", "code": "CHEM", "hod": "Dr. M. Ramesh Naidu", "faculty_count": 18},
    {"id": "dept-bme", "name": "Biomedical Engineering", "code": "BME", "hod": "Dr. G. Sitaramanjaneya Reddy", "faculty_count": 16},
    {"id": "dept-pharm", "name": "Pharmacy", "code": "PHARM", "hod": "Dr. Ch. Jithendra", "faculty_count": 22},
    {"id": "dept-snh", "name": "Science & Humanities", "code": "S&H", "hod": "Dr. N. Srinivasu", "faculty_count": 55},
    {"id": "dept-mba", "name": "Management Studies", "code": "MBA", "hod": "Mr. D. Vijaya Krishna", "faculty_count": 20}
]

audit_logs: List[Dict[str, Any]] = [
    {"id": "log-01", "timestamp": datetime.now().isoformat(), "actor": "Dr. System Administrator", "action": "System Initialization", "details": "Bootstrapped VFSTR master data collections and 5-agent pipeline."},
    {"id": "log-02", "timestamp": datetime.now().isoformat(), "actor": "Dr. System Administrator", "action": "Security Audit", "details": "Enforced 4-tier RBAC rules (SUPER_ADMIN, HOD, EVENT_ORGANIZER, STUDENT)."}
]

def record_audit_log(actor: str, action: str, details: str):
    audit_logs.insert(0, {
        "id": f"log-{len(audit_logs)+1}",
        "timestamp": datetime.now().isoformat(),
        "actor": actor,
        "action": action,
        "details": details
    })

# -------------------------------------------------------------
# 1. VENUES CRUD
# -------------------------------------------------------------

class VenueCreate(BaseModel):
    name: str
    category: str
    block: str
    capacity: int
    ac: bool = True
    av_equipped: bool = True
    suitable_for: List[str] = ["Events", "Seminars"]
    description: str = "Campus venue"

@router.get("/venues")
async def get_all_venues():
    """Retrieve full venue master catalog."""
    return {"venues": runtime_venues, "total": len(runtime_venues)}

@router.post("/venues", status_code=status.HTTP_201_CREATED)
async def create_venue(venue: VenueCreate, current_user: dict = Depends(require_role(["SUPER_ADMIN"]))):
    """Add a new campus venue to master data."""
    v_id = f"venue-{int(datetime.now().timestamp() * 1000)}"
    new_v = {
        "id": v_id,
        "name": venue.name,
        "category": venue.category,
        "block": venue.block,
        "capacity": venue.capacity,
        "ac": venue.ac,
        "av_equipped": venue.av_equipped,
        "suitable_for": venue.suitable_for,
        "status": "available",
        "description": venue.description
    }
    runtime_venues.append(new_v)
    record_audit_log(current_user.get("name", "Super Admin"), "Create Venue", f"Created venue '{venue.name}' (Cap: {venue.capacity})")
    return {"message": "Venue successfully created", "venue": new_v}

@router.put("/venues/{venue_id}")
async def update_venue(venue_id: str, venue: VenueCreate, current_user: dict = Depends(require_role(["SUPER_ADMIN"]))):
    """Update an existing campus venue."""
    for idx, v in enumerate(runtime_venues):
        if v["id"] == venue_id:
            runtime_venues[idx].update({
                "name": venue.name,
                "category": venue.category,
                "block": venue.block,
                "capacity": venue.capacity,
                "ac": venue.ac,
                "av_equipped": venue.av_equipped,
                "suitable_for": venue.suitable_for,
                "description": venue.description
            })
            record_audit_log(current_user.get("name", "Super Admin"), "Update Venue", f"Updated venue '{venue.name}'")
            return {"message": "Venue updated successfully", "venue": runtime_venues[idx]}
    raise HTTPException(status_code=404, detail="Venue not found")

@router.delete("/venues/{venue_id}")
async def delete_venue(venue_id: str, current_user: dict = Depends(require_role(["SUPER_ADMIN"]))):
    """Delete a campus venue from master data."""
    global runtime_venues
    for v in runtime_venues:
        if v["id"] == venue_id:
            runtime_venues = [item for item in runtime_venues if item["id"] != venue_id]
            record_audit_log(current_user.get("name", "Super Admin"), "Delete Venue", f"Deleted venue '{v['name']}'")
            return {"message": f"Venue '{v['name']}' deleted successfully"}
    raise HTTPException(status_code=404, detail="Venue not found")

# -------------------------------------------------------------
# 2. RESOURCES CRUD
# -------------------------------------------------------------

class ResourceCreate(BaseModel):
    name: str
    category: str
    total_quantity: int
    available_quantity: int
    unit: str = "units"

@router.get("/resources")
async def get_all_resources():
    """Retrieve full resource master catalog."""
    return {"resources": runtime_resources, "total": len(runtime_resources)}

@router.post("/resources", status_code=status.HTTP_201_CREATED)
async def create_resource(res: ResourceCreate, current_user: dict = Depends(require_role(["SUPER_ADMIN"]))):
    """Add a new resource stream to campus inventory."""
    r_id = f"res-{int(datetime.now().timestamp() * 1000)}"
    new_r = {
        "id": r_id,
        "name": res.name,
        "category": res.category,
        "total_quantity": res.total_quantity,
        "available_quantity": res.available_quantity,
        "unit": res.unit,
        "editable": True
    }
    runtime_resources.append(new_r)
    record_audit_log(current_user.get("name", "Super Admin"), "Create Resource", f"Created resource '{res.name}' ({res.total_quantity} {res.unit})")
    return {"message": "Resource created successfully", "resource": new_r}

@router.put("/resources/{res_id}")
async def update_resource(res_id: str, res: ResourceCreate, current_user: dict = Depends(require_role(["SUPER_ADMIN"]))):
    """Update inventory quantity and details for a campus resource."""
    for idx, r in enumerate(runtime_resources):
        if r["id"] == res_id:
            runtime_resources[idx].update({
                "name": res.name,
                "category": res.category,
                "total_quantity": res.total_quantity,
                "available_quantity": res.available_quantity,
                "unit": res.unit
            })
            record_audit_log(current_user.get("name", "Super Admin"), "Update Resource", f"Updated resource '{res.name}'")
            return {"message": "Resource updated successfully", "resource": runtime_resources[idx]}
    raise HTTPException(status_code=404, detail="Resource not found")

@router.delete("/resources/{res_id}")
async def delete_resource(res_id: str, current_user: dict = Depends(require_role(["SUPER_ADMIN"]))):
    """Delete a resource stream from inventory."""
    global runtime_resources
    for r in runtime_resources:
        if r["id"] == res_id:
            runtime_resources = [item for item in runtime_resources if item["id"] != res_id]
            record_audit_log(current_user.get("name", "Super Admin"), "Delete Resource", f"Deleted resource '{r['name']}'")
            return {"message": f"Resource '{r['name']}' deleted successfully"}
    raise HTTPException(status_code=404, detail="Resource not found")

# -------------------------------------------------------------
# 3. FACULTY CRUD
# -------------------------------------------------------------

class FacultyCreate(BaseModel):
    name: str
    designation: str
    department: str
    email: str
    qualifications: str = "Ph.D."
    status: str = "Active"

@router.get("/faculty")
async def get_all_faculty():
    """Retrieve campus faculty directory."""
    return {"faculty": runtime_faculty, "total": len(runtime_faculty)}

@router.post("/faculty", status_code=status.HTTP_201_CREATED)
async def create_faculty(fac: FacultyCreate, current_user: dict = Depends(require_role(["SUPER_ADMIN"]))):
    """Add a faculty coordinator to the university directory."""
    f_id = f"fac-{int(datetime.now().timestamp() * 1000)}"
    new_f = {
        "id": f_id,
        "name": fac.name,
        "designation": fac.designation,
        "department": fac.department,
        "email": fac.email,
        "qualifications": fac.qualifications,
        "status": fac.status
    }
    runtime_faculty.append(new_f)
    record_audit_log(current_user.get("name", "Super Admin"), "Create Faculty", f"Added faculty member '{fac.name}' ({fac.department})")
    return {"message": "Faculty added successfully", "faculty": new_f}

@router.put("/faculty/{fac_id}")
async def update_faculty(fac_id: str, fac: FacultyCreate, current_user: dict = Depends(require_role(["SUPER_ADMIN"]))):
    """Update faculty details."""
    for idx, f in enumerate(runtime_faculty):
        if f["id"] == fac_id:
            runtime_faculty[idx].update({
                "name": fac.name,
                "designation": fac.designation,
                "department": fac.department,
                "email": fac.email,
                "qualifications": fac.qualifications,
                "status": fac.status
            })
            record_audit_log(current_user.get("name", "Super Admin"), "Update Faculty", f"Updated faculty '{fac.name}'")
            return {"message": "Faculty updated successfully", "faculty": runtime_faculty[idx]}
    raise HTTPException(status_code=404, detail="Faculty member not found")

@router.delete("/faculty/{fac_id}")
async def delete_faculty(fac_id: str, current_user: dict = Depends(require_role(["SUPER_ADMIN"]))):
    """Remove faculty member from directory."""
    global runtime_faculty
    for f in runtime_faculty:
        if f["id"] == fac_id:
            runtime_faculty = [item for item in runtime_faculty if item["id"] != fac_id]
            record_audit_log(current_user.get("name", "Super Admin"), "Delete Faculty", f"Removed faculty member '{f['name']}'")
            return {"message": f"Faculty '{f['name']}' removed successfully"}
    raise HTTPException(status_code=404, detail="Faculty member not found")

# -------------------------------------------------------------
# 4. DEPARTMENTS CRUD
# -------------------------------------------------------------

class DepartmentCreate(BaseModel):
    name: str
    code: str
    hod: str
    faculty_count: int = 25

@router.get("/departments")
async def get_all_departments():
    """Retrieve university departments."""
    return {"departments": runtime_departments, "total": len(runtime_departments)}

@router.post("/departments", status_code=status.HTTP_201_CREATED)
async def create_department(dept: DepartmentCreate, current_user: dict = Depends(require_role(["SUPER_ADMIN"]))):
    """Add a new university academic department."""
    d_id = f"dept-{dept.code.lower()}"
    new_d = {
        "id": d_id,
        "name": dept.name,
        "code": dept.code,
        "hod": dept.hod,
        "faculty_count": dept.faculty_count
    }
    runtime_departments.append(new_d)
    record_audit_log(current_user.get("name", "Super Admin"), "Create Department", f"Created department '{dept.name}' ({dept.code})")
    return {"message": "Department created successfully", "department": new_d}

# -------------------------------------------------------------
# 5. AUDIT LOGS & SYSTEM STATS
# -------------------------------------------------------------

@router.get("/audit-logs")
async def get_audit_logs():
    """Retrieve security audit logs and administrative trace."""
    return {"audit_logs": audit_logs, "total": len(audit_logs)}
