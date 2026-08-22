// ---------------------------------------------
// ONLY 4 Supported Roles in the System
// ---------------------------------------------
export type UserRole =
  | 'SUPER_ADMIN'
  | 'HOD'
  | 'EVENT_ORGANIZER'
  | 'STUDENT';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  department?: string;
  avatar?: string;
}

export interface Venue {
  id: string;
  name: string;
  category: string;
  block: string;
  capacity: number;
  ac: boolean;
  av_equipped: boolean;
  suitable_for: string[];
  status: 'available' | 'booked' | 'maintenance';
  description: string;
}

export interface ResourceItem {
  id: string;
  name: string;
  category: string;
  total_quantity: number;
  available_quantity: number;
  unit: string;
  editable: boolean;
}

export interface LeadershipMember {
  id: string;
  name: string;
  role: string;
  qualifications?: string;
  department: string;
  user_provided: boolean;
  editable: boolean;
}

export interface FacultyMember {
  id: string;
  name: string;
  designation: string;
  department: string;
  email: string;
  qualifications?: string;
  status: string;
}

export interface DepartmentItem {
  id: string;
  name: string;
  code: string;
  hod: string;
  faculty_count: number;
}

export interface BlockInfo {
  block_id: string;
  name: string;
  total_floors: number;
  known_patterns: string[];
  description: string;
  known_rooms_count: number;
}

export interface HealthResponse {
  status: string;
  project: string;
  version: string;
  campus: {
    name: string;
    location: string;
  };
  database: {
    status: string;
    name: string;
    connected: boolean;
  };
  ai_engine: {
    provider: string;
    model: string;
    api_key_configured: boolean;
  };
  uptime_seconds: number;
}

// ---------------------------------------------
// Campus Event & Operations Types
// ---------------------------------------------

export interface CampusEvent {
  id: string;
  title: string;
  category: string;
  event_type: string;
  venue_id: string;
  venue_name: string;
  date: string;
  dates_label?: string;
  start_time: string;
  end_time: string;
  expected_participants: number;
  organizer: string;
  organizer_email: string;
  host_department: string;
  status: 'Approved' | 'Pending Approval' | 'Under Review' | 'Rejected' | 'Draft';
  approval_tier: string;
  conflict_status: string;
  description: string;
  registered_students_count: number;
  is_published: boolean;
}

export interface VenueTimeSlot {
  slot: string;
  status: 'AVAILABLE' | 'BOOKED' | 'MAINTENANCE' | 'CONFLICT';
  event_title?: string | null;
}

export interface VenueAvailability {
  venue_id: string;
  venue_name: string;
  category: string;
  capacity: number;
  block: string;
  date: string;
  overall_status: 'AVAILABLE' | 'PARTIAL_BOOKED' | 'FULLY_BOOKED';
  time_slots: VenueTimeSlot[];
}

export interface AuditLogItem {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  details: string;
}

// ---------------------------------------------
// AI Event Plan Types
// ---------------------------------------------

export interface EventDetails {
  title: string;
  category: string;
  event_type: string;
  expected_participants: number;
  duration: string;
  duration_days: number;
  duration_hours_per_day: number;
  target_audience: string;
  host_department: string;
  key_objectives: string[];
  special_requirements: string[];
}

export interface VenueRecommendation {
  venue_id: string;
  venue_name: string;
  category: string;
  block: string;
  capacity: number;
  capacity_match: string;
  utilization_percentage: number;
  ac: boolean;
  av_equipped: boolean;
  suitability_score: number;
  suitability_reason: string;
  is_primary: boolean;
}

export interface ResourceAllocation {
  resource_id: string;
  name: string;
  category: string;
  required_quantity: number;
  available_quantity: number;
  allocated_quantity: number;
  unit: string;
  status: 'Optimal' | 'Sufficient' | 'Shortage' | 'Partial';
  notes?: string;
}

export interface ConflictItem {
  conflict_id: string;
  type: string;
  severity: 'High' | 'Medium' | 'Low' | 'Resolved';
  description: string;
  impact: string;
  resolved: boolean;
}

export interface ConflictResolution {
  resolution_id: string;
  target_conflict: string;
  strategy: string;
  action_taken: string;
  status: string;
}

export interface ScheduleItem {
  day: number;
  time_slot: string;
  stage_name: string;
  activity: string;
  venue_allocated: string;
  responsible_team: string;
  notes?: string;
}

export interface AgentTrace {
  agent_id: string;
  agent_name: string;
  responsibility: string;
  status: 'completed' | 'executing' | 'error' | 'waiting';
  execution_time_ms: number;
  summary: string;
  details?: Record<string, any>;
}

export interface EventPlanResponse {
  event: EventDetails;
  assumptions: string[];
  venue_recommendations: VenueRecommendation[];
  selected_venue: VenueRecommendation;
  secondary_venues: VenueRecommendation[];
  resources: ResourceAllocation[];
  conflicts: ConflictItem[];
  resolutions: ConflictResolution[];
  schedule: ScheduleItem[];
  recommendations: string[];
  approval_workflow: Array<{ tier: string; role: string; action: string }>;
  status: string;
  planning_summary: string;
  ai_engine_used: string;
  orchestration_time_ms: number;
  agent_trace: AgentTrace[];
}

export interface PlanRevalidateResponse {
  is_valid: boolean;
  status: string;
  venue_check: {
    venue_name: string;
    capacity: number;
    demanded: number;
    status: string;
    deficit: number;
  };
  resource_check: {
    status: string;
    details: string[];
  };
  conflict_check: {
    conflicts: string[];
    count: number;
  };
  message: string;
}
