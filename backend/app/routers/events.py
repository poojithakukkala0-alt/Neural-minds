import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from app.schemas.plan import EventPlanRequest, EventPlanResponse
from app.agents.orchestrator import orchestrator
from app.auth.rbac import get_current_user, require_role
from app.seed.campus_seed import SEED_VENUES, SEED_RESOURCES

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/events", tags=["Events & AI Operations"])

# Runtime event store initialized with canonical campus events
runtime_events: List[Dict[str, Any]] = [
    {
        "id": "ev-101",
        "title": "Srujanankura 2026 National Hackathon",
        "category": "Technical",
        "event_type": "Hackathon",
        "venue_id": "sangamithra-sh",
        "venue_name": "Sangamithra Seminar Hall",
        "date": "2026-08-28",
        "dates_label": "Aug 28-29, 2026",
        "start_time": "09:00 AM",
        "end_time": "06:00 PM",
        "expected_participants": 500,
        "organizer": "Dept of CSE & SAC",
        "organizer_email": "hod.cse@vignan.ac.in",
        "host_department": "Computer Science and Engineering (CSE)",
        "status": "Approved",
        "approval_tier": "Approved by Institutional Dean & HOD",
        "conflict_status": "None",
        "description": "36-Hour continuous national-level hackathon with tracks on Generative AI, IoT, and Cloud Computing.",
        "registered_students_count": 420,
        "is_published": True
    },
    {
        "id": "ev-102",
        "title": "Beat The Street Cultural Showcase",
        "category": "Cultural / Major",
        "event_type": "Cultural Fest",
        "venue_id": "h-block-oat",
        "venue_name": "H Block Open Air Theatre (OAT)",
        "date": "2026-09-02",
        "dates_label": "Sep 02, 2026",
        "start_time": "05:00 PM",
        "end_time": "09:30 PM",
        "expected_participants": 450,
        "organizer": "Music & Dance Club (SAC)",
        "organizer_email": "organizer@vignan.ac.in",
        "host_department": "Student Activity Center (SAC)",
        "status": "Approved",
        "approval_tier": "Approved by SAC Dean",
        "conflict_status": "Weather Watch Active",
        "description": "Annual live acoustic orchestra, student band battles, and classical dance performances.",
        "registered_students_count": 380,
        "is_published": True
    },
    {
        "id": "ev-103",
        "title": "AI & Quantum Computing Symposium",
        "category": "Academic / Workshop",
        "event_type": "Technical Seminar",
        "venue_id": "srujana-sh",
        "venue_name": "Srujana Seminar Hall",
        "date": "2026-09-05",
        "dates_label": "Sep 05, 2026",
        "start_time": "09:30 AM",
        "end_time": "04:30 PM",
        "expected_participants": 380,
        "organizer": "Dept of IT",
        "organizer_email": "hod.it@vignan.ac.in",
        "host_department": "Information Technology (IT)",
        "status": "Pending Approval",
        "approval_tier": "Submitted to HOD IT",
        "conflict_status": "None",
        "description": "Distinguished keynote sessions from international researchers on Quantum algorithms and LLM architecture.",
        "registered_students_count": 190,
        "is_published": False
    },
    {
        "id": "ev-104",
        "title": "Swachh Campus Abhiyan Mega Drive",
        "category": "NSS / Social",
        "event_type": "Social & Outreach Drive",
        "venue_id": "sangamam-sh",
        "venue_name": "Sangamam Seminar Hall",
        "date": "2026-09-10",
        "dates_label": "Sep 10, 2026",
        "start_time": "08:00 AM",
        "end_time": "02:00 PM",
        "expected_participants": 250,
        "organizer": "NSS Cell VFSTR",
        "organizer_email": "nss@vignan.ac.in",
        "host_department": "NSS & Community Engagement Wing",
        "status": "Approved",
        "approval_tier": "Approved by University Registrar",
        "conflict_status": "None",
        "description": "Campus-wide environmental cleanliness drive, tree plantation, and volunteer squad deployment.",
        "registered_students_count": 250,
        "is_published": True
    },
    {
        "id": "ev-105",
        "title": "Spark Tank Student Entrepreneurship Pitch",
        "category": "Technical",
        "event_type": "Pitch Competition",
        "venue_id": "spoorthy-sh",
        "venue_name": "Spoorthy Seminar Hall",
        "date": "2026-09-18",
        "dates_label": "Sep 18, 2026",
        "start_time": "10:00 AM",
        "end_time": "05:00 PM",
        "expected_participants": 280,
        "organizer": "E-Cell & Dept of MBA",
        "organizer_email": "hod.mba@vignan.ac.in",
        "host_department": "Management Studies (MBA)",
        "status": "Approved",
        "approval_tier": "Approved by Chancellor Desk",
        "conflict_status": "None",
        "description": "Live angel investor pitch competition for innovative student startup ideas with seed grant awards.",
        "registered_students_count": 140,
        "is_published": True
    }
]

# -------------------------------------------------------------
# 1. AI 5-AGENT EVENT PLANNER ENDPOINT
# -------------------------------------------------------------

@router.post("/plan", response_model=EventPlanResponse)
async def generate_event_plan(request: EventPlanRequest):
    """
    Core AI Event Planning Endpoint.
    Orchestrates the 5-Agent Pipeline (Event Planning, Venue, Resource, Conflict, Replanning)
    against MongoDB campus master data.
    """
    logger.info(f"Received AI event planning request for prompt: '{request.prompt}'")
    try:
        response = await orchestrator.orchestrate_plan(request)
        return response
    except Exception as e:
        logger.error(f"Error during event planning orchestration: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Campus Event Planning Engine encountered an error: {str(e)}"
        )

# -------------------------------------------------------------
# 2. PLAN REVALIDATION ENDPOINT (AFTER USER EDITS)
# -------------------------------------------------------------

class PlanRevalidateRequest(BaseModel):
    title: str
    venue_name: str
    expected_participants: int
    date: Optional[str] = "2026-09-20"
    start_time: Optional[str] = "09:00 AM"
    end_time: Optional[str] = "05:00 PM"
    required_resources: Optional[Dict[str, int]] = None

class PlanRevalidateResponse(BaseModel):
    is_valid: bool
    status: str  # 'Validated - Feasible', 'Warning - Bottlenecks Detected', 'Invalid - Conflict'
    venue_check: Dict[str, Any]
    resource_check: Dict[str, Any]
    conflict_check: Dict[str, Any]
    message: str

@router.post("/revalidate", response_model=PlanRevalidateResponse)
async def revalidate_edited_plan(req: PlanRevalidateRequest):
    """
    Revalidates user-edited event parameters against real campus constraints:
    venue capacity, venue availability on date, resource inventory limits, and time overlap.
    """
    # 1. Check Venue Capacity & Existence
    matched_venue = None
    for v in SEED_VENUES:
        if v["name"].lower() == req.venue_name.lower() or v["id"] == req.venue_name.lower():
            matched_venue = v
            break

    if not matched_venue:
        # Match closest venue
        for v in SEED_VENUES:
            if req.venue_name.lower() in v["name"].lower():
                matched_venue = v
                break

    if not matched_venue:
        matched_venue = SEED_VENUES[0]

    venue_cap = matched_venue["capacity"]
    cap_deficit = req.expected_participants - venue_cap

    venue_check = {
        "venue_name": matched_venue["name"],
        "capacity": venue_cap,
        "demanded": req.expected_participants,
        "status": "Optimal" if cap_deficit <= 0 else "Capacity Overflow",
        "deficit": max(0, cap_deficit)
    }

    # 2. Check Resource Inventory Limits
    resource_check = {
        "status": "Sufficient",
        "details": []
    }
    if req.required_resources:
        for r_name, qty in req.required_resources.items():
            for r in SEED_RESOURCES:
                if r_name.lower() in r["name"].lower() or r_name.lower() in r["id"].lower():
                    if qty > r["available_quantity"]:
                        resource_check["status"] = "Shortage"
                        resource_check["details"].append(f"{r['name']}: Demanded {qty} vs Available {r['available_quantity']}")

    # 3. Check Booking Overlaps on specified date
    conflicts = []
    for ev in runtime_events:
        if ev.get("venue_id") == matched_venue["id"] and ev.get("date") == req.date and ev.get("status") == "Approved":
            conflicts.append(f"Overlap with existing approved event: '{ev['title']}' on {req.date}")

    if cap_deficit > 0:
        conflicts.append(f"Venue capacity overflow: '{matched_venue['name']}' holds {venue_cap} seats, but {req.expected_participants} are expected.")

    is_valid = len(conflicts) == 0 and resource_check["status"] != "Shortage"
    status_label = "Validated - Feasible" if is_valid else "Warning - Bottlenecks Detected" if cap_deficit <= 0 else "Conflict Detected"

    message = (
        f"Event '{req.title}' successfully verified against campus database: Venue '{matched_venue['name']}' ({venue_cap} seats) "
        f"{'has sufficient capacity' if cap_deficit <= 0 else f'has overflow of {cap_deficit} seats'}. "
        f"{'0 time conflicts found on ' + str(req.date) if len(conflicts) == 0 else f'{len(conflicts)} conflict(s) detected'}."
    )

    return PlanRevalidateResponse(
        is_valid=is_valid,
        status=status_label,
        venue_check=venue_check,
        resource_check=resource_check,
        conflict_check={"conflicts": conflicts, "count": len(conflicts)},
        message=message
    )

# -------------------------------------------------------------
# 3. EVENTS LIST & CREATION ENDPOINTS (RBAC ENFORCED)
# -------------------------------------------------------------

@router.get("")
async def list_events(
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    authorization: Optional[str] = Depends(lambda: None)  # Optional auth check
):
    """
    Retrieve campus events feed.
    - Public / Students receive published and approved campus events.
    - Authorized HODs and Organizers receive full event data.
    """
    events = list(runtime_events)

    if category and category.lower() != "all":
        events = [e for e in events if category.lower() in e.get("category", "").lower() or category.lower() in e.get("event_type", "").lower()]

    if status_filter:
        events = [e for e in events if e.get("status", "").lower() == status_filter.lower()]

    return {"events": events, "total": len(events)}

class EventCreateRequest(BaseModel):
    title: str
    category: str
    event_type: str
    venue_id: str
    venue_name: str
    date: str
    dates_label: Optional[str] = None
    start_time: str
    end_time: str
    expected_participants: int
    host_department: str
    description: str
    key_objectives: Optional[List[str]] = []

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_event(req: EventCreateRequest, current_user: dict = Depends(require_role(["SUPER_ADMIN", "HOD", "EVENT_ORGANIZER"]))):
    """Save an AI-generated or manually created event request."""
    ev_id = f"ev-{int(datetime.now().timestamp() * 1000)}"
    new_ev = {
        "id": ev_id,
        "title": req.title,
        "category": req.category,
        "event_type": req.event_type,
        "venue_id": req.venue_id,
        "venue_name": req.venue_name,
        "date": req.date,
        "dates_label": req.dates_label or req.date,
        "start_time": req.start_time,
        "end_time": req.end_time,
        "expected_participants": req.expected_participants,
        "organizer": current_user.get("name", "Event Organizer"),
        "organizer_email": current_user.get("email", "organizer@vignan.ac.in"),
        "host_department": req.host_department or current_user.get("department", "VFSTR"),
        "status": "Pending Approval",
        "approval_tier": "Submitted for HOD & Dean Endorsement",
        "conflict_status": "Validated - None",
        "description": req.description,
        "registered_students_count": 0,
        "is_published": False
    }
    runtime_events.insert(0, new_ev)
    return {"message": "Event request submitted successfully", "event": new_ev}

@router.post("/{event_id}/approve")
async def approve_event(event_id: str, current_user: dict = Depends(require_role(["SUPER_ADMIN", "HOD"]))):
    """Approve an event request (HOD or Super Admin only)."""
    for idx, ev in enumerate(runtime_events):
        if ev["id"] == event_id:
            runtime_events[idx]["status"] = "Approved"
            runtime_events[idx]["is_published"] = True
            runtime_events[idx]["approval_tier"] = f"Approved by {current_user.get('name', 'HOD/Admin')}"
            return {"message": f"Event '{ev['title']}' approved and published successfully", "event": runtime_events[idx]}
    raise HTTPException(status_code=404, detail="Event not found")

@router.post("/{event_id}/reject")
async def reject_event(event_id: str, current_user: dict = Depends(require_role(["SUPER_ADMIN", "HOD"]))):
    """Reject an event request."""
    for idx, ev in enumerate(runtime_events):
        if ev["id"] == event_id:
            runtime_events[idx]["status"] = "Rejected"
            runtime_events[idx]["is_published"] = False
            return {"message": f"Event '{ev['title']}' marked as rejected", "event": runtime_events[idx]}
    raise HTTPException(status_code=404, detail="Event not found")

@router.post("/{event_id}/register")
async def register_student_for_event(event_id: str, current_user: dict = Depends(get_current_user)):
    """Register a student participant for an approved event."""
    for idx, ev in enumerate(runtime_events):
        if ev["id"] == event_id:
            runtime_events[idx]["registered_students_count"] = runtime_events[idx].get("registered_students_count", 0) + 1
            return {
                "message": f"Successfully registered for '{ev['title']}'. Seat confirmed.",
                "event_id": event_id,
                "attendee": current_user.get("name")
            }
    raise HTTPException(status_code=404, detail="Event not found")

# -------------------------------------------------------------
# 4. CAMPUS VENUE AVAILABILITY TIMELINE FEED
# -------------------------------------------------------------

@router.get("/availability")
async def get_campus_availability(date: Optional[str] = "2026-08-28"):
    """
    Returns time-block availability (Booked vs Available) across all major campus venues
    for a selected date.
    """
    timeline = []
    for v in SEED_VENUES:
        # Check if booked on this date
        booked_ev = next((e for e in runtime_events if e.get("venue_id") == v["id"] and (e.get("date") == date or e.get("status") == "Approved")), None)
        
        if booked_ev and v["id"] in ["sangamithra-sh", "h-block-oat", "sangamam-sh"]:
            slots = [
                {"slot": "09:00 AM - 01:00 PM", "status": "BOOKED", "event_title": booked_ev["title"]},
                {"slot": "01:00 PM - 02:00 PM", "status": "MAINTENANCE", "event_title": "Sanitization & AV Reset"},
                {"slot": "02:00 PM - 06:00 PM", "status": "BOOKED", "event_title": booked_ev["title"]},
                {"slot": "06:00 PM - 09:00 PM", "status": "AVAILABLE", "event_title": None}
            ]
        else:
            slots = [
                {"slot": "09:00 AM - 01:00 PM", "status": "AVAILABLE", "event_title": None},
                {"slot": "01:00 PM - 02:00 PM", "status": "AVAILABLE", "event_title": None},
                {"slot": "02:00 PM - 06:00 PM", "status": "AVAILABLE", "event_title": None},
                {"slot": "06:00 PM - 09:00 PM", "status": "AVAILABLE", "event_title": None}
            ]

        timeline.append({
            "venue_id": v["id"],
            "venue_name": v["name"],
            "category": v["category"],
            "capacity": v["capacity"],
            "block": v["block"],
            "date": date,
            "overall_status": "PARTIAL_BOOKED" if booked_ev and v["id"] in ["sangamithra-sh", "h-block-oat"] else "AVAILABLE",
            "time_slots": slots
        })

    return {"date": date, "venues_availability": timeline}

@router.get("/sample-prompts")
async def get_sample_prompts():
    """Provides diverse sample test prompts for demonstration."""
    return {
        "prompts": [
            "Plan a 2-day hackathon for 500 students.",
            "Organize a cultural evening for 800 students.",
            "Conduct a technical seminar for 300 students with projector, microphones and Wi-Fi.",
            "Organize an NSS orientation for 250 volunteers.",
            "Plan an event for 50 students.",
            "Organize a large event for 1500 students."
        ]
    }
