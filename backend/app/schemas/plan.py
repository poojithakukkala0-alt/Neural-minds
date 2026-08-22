from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class EventPlanRequest(BaseModel):
    prompt: str = Field(..., min_length=3, description="User's natural language event requirement")
    preferred_venue: Optional[str] = None
    expected_attendees: Optional[int] = None
    date_hint: Optional[str] = None

class EventDetails(BaseModel):
    title: str
    category: str
    event_type: str
    expected_participants: int
    duration: str
    duration_days: int
    duration_hours_per_day: int
    target_audience: str
    host_department: str
    key_objectives: List[str]
    special_requirements: List[str]

class VenueRecommendation(BaseModel):
    venue_id: str
    venue_name: str
    category: str
    block: str
    capacity: int
    capacity_match: str  # 'Perfect', 'Sufficient', 'Overflow Risk', 'Exceeds Demand'
    utilization_percentage: float
    ac: bool
    av_equipped: bool
    suitability_score: int  # 0 - 100
    suitability_reason: str
    is_primary: bool = False

class ResourceAllocation(BaseModel):
    resource_id: str
    name: str
    category: str
    required_quantity: int
    available_quantity: int
    allocated_quantity: int
    unit: str
    status: str  # 'Sufficient', 'Partial', 'Shortage', 'Optimal'
    notes: Optional[str] = None

class ConflictItem(BaseModel):
    conflict_id: str
    type: str  # 'Capacity', 'Venue Overlap', 'Resource Shortage', 'Logistical', 'Weather'
    severity: str  # 'High', 'Medium', 'Low', 'Resolved'
    description: str
    impact: str
    resolved: bool = False

class ConflictResolution(BaseModel):
    resolution_id: str
    target_conflict: str
    strategy: str
    action_taken: str
    status: str  # 'Applied', 'Alternative Selected', 'Mitigated'

class ScheduleItem(BaseModel):
    day: int
    time_slot: str
    stage_name: str
    activity: str
    venue_allocated: str
    responsible_team: str
    notes: Optional[str] = None

class AgentTrace(BaseModel):
    agent_id: str
    agent_name: str
    responsibility: str
    status: str  # 'completed', 'executing', 'error'
    execution_time_ms: float
    summary: str
    details: Optional[Dict[str, Any]] = None

class EventPlanResponse(BaseModel):
    event: EventDetails
    assumptions: List[str]
    venue_recommendations: List[VenueRecommendation]
    selected_venue: VenueRecommendation
    secondary_venues: List[VenueRecommendation] = []
    resources: List[ResourceAllocation]
    conflicts: List[ConflictItem]
    resolutions: List[ConflictResolution]
    schedule: List[ScheduleItem]
    recommendations: List[str]
    approval_workflow: List[Dict[str, str]]
    status: str  # 'Optimal - Feasible', 'Feasible with Replanning', 'Requires Review'
    planning_summary: str
    ai_engine_used: str
    orchestration_time_ms: float
    agent_trace: List[AgentTrace]
