import time
from typing import List, Dict, Any
from app.schemas.plan import (
    EventDetails,
    VenueRecommendation,
    ResourceAllocation,
    ConflictItem,
    ScheduleItem
)

class ConflictScheduleAgent:
    """
    Agent 4 — Schedule / Conflict Agent
    Performs multi-dimensional conflict detection (Capacity, Overlaps, Resource Limits, Logistics)
    and constructs a feasible day-by-day operational schedule.
    """
    def __init__(self):
        self.name = "Conflict / Schedule Agent"
        self.responsibility = "Multi-Factor Conflict Detection & Chronological Agenda Synthesis"

    async def execute(
        self,
        event_details: EventDetails,
        selected_venue: VenueRecommendation,
        resource_allocations: List[ResourceAllocation],
        shortages: List[str],
        schedule_outline: List[Dict[str, Any]],
        existing_bookings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        start_time = time.time()
        conflicts: List[ConflictItem] = []

        # 1. Capacity Conflict Check
        if selected_venue.capacity < event_details.expected_participants:
            deficit = event_details.expected_participants - selected_venue.capacity
            conflicts.append(
                ConflictItem(
                    conflict_id="conf-cap-01",
                    type="Capacity Overflow",
                    severity="High",
                    description=f"Selected venue '{selected_venue.venue_name}' capacity ({selected_venue.capacity}) is smaller than requested attendee volume ({event_details.expected_participants}).",
                    impact=f"Potential overflow of {deficit} students.",
                    resolved=False
                )
            )

        # 2. Existing Booking Conflict Check
        for booking in existing_bookings:
            if booking.get("venue_id") == selected_venue.venue_id:
                conflicts.append(
                    ConflictItem(
                        conflict_id=f"conf-bk-{booking.get('event_id', '01')}",
                        type="Venue Overlap",
                        severity="High",
                        description=f"Venue '{selected_venue.venue_name}' has an existing booking record: '{booking.get('title')}'.",
                        impact="Schedule collision on primary campus venue.",
                        resolved=False
                    )
                )

        # 3. Resource Shortage Conflicts
        for shortage_text in shortages:
            conflicts.append(
                ConflictItem(
                    conflict_id=f"conf-res-{len(conflicts)+1}",
                    type="Resource Shortage",
                    severity="Medium",
                    description=shortage_text,
                    impact="Equipment deficit requires inventory scaling or backup substitution.",
                    resolved=False
                )
            )

        # 4. Operational / Time Constraints
        if event_details.duration_days > 1 and "hackathon" in event_details.event_type.lower():
            conflicts.append(
                ConflictItem(
                    conflict_id="conf-ops-01",
                    type="Logistical",
                    severity="Low",
                    description="Continuous multi-day / overnight hackathon demands 24x7 security, backup generators, and canteen coordination.",
                    impact="Shift schedules required for security & facility teams.",
                    resolved=True  # Pre-handled in operational plan
                )
            )

        if "oat" in selected_venue.venue_id.lower():
            conflicts.append(
                ConflictItem(
                    conflict_id="conf-env-01",
                    type="Weather / Environmental",
                    severity="Low",
                    description="Open Air Theatre is subject to outdoor weather conditions and requires stage lighting after sunset.",
                    impact="Contingency indoor backup recommended.",
                    resolved=True
                )
            )

        # 5. Build Dynamic Schedule
        schedule: List[ScheduleItem] = self._build_dynamic_schedule(
            event_details, selected_venue, schedule_outline
        )

        exec_time = round((time.time() - start_time) * 1000, 2)

        return {
            "conflicts": conflicts,
            "schedule": schedule,
            "trace": {
                "agent_id": "agent-4-conflict",
                "agent_name": self.name,
                "responsibility": self.responsibility,
                "status": "completed",
                "execution_time_ms": exec_time,
                "summary": f"Detected {len(conflicts)} conflict(s) ({len([c for c in conflicts if not c.resolved])} active) and generated {len(schedule)} schedule milestone(s).",
                "details": {
                    "total_conflicts": len(conflicts),
                    "schedule_stages_count": len(schedule)
                }
            }
        }

    def _build_dynamic_schedule(
        self,
        event_details: EventDetails,
        venue: VenueRecommendation,
        outline: List[Dict[str, Any]]
    ) -> List[ScheduleItem]:
        """Synthesizes structured timeline tailored to event type and days."""
        items: List[ScheduleItem] = []
        days = event_details.duration_days
        event_type = event_details.event_type.lower()
        dept = event_details.host_department

        if outline and len(outline) > 0:
            for item in outline:
                items.append(
                    ScheduleItem(
                        day=item.get("day", 1),
                        time_slot=item.get("time_slot", "09:00 AM - 11:00 AM"),
                        stage_name=item.get("stage_name", "Event Session"),
                        activity=item.get("activity", "Scheduled session activity"),
                        venue_allocated=venue.venue_name,
                        responsible_team=item.get("responsible_team", dept),
                        notes=item.get("notes", "Confirmed slot")
                    )
                )
            return items

        # Tailored schedule generation based on taxonomy
        if "hackathon" in event_type or "ideathon" in event_type:
            if days >= 2:
                items.append(ScheduleItem(
                    day=1,
                    time_slot="08:30 AM - 10:00 AM",
                    stage_name="Delegate Check-In & Team Kit Distribution",
                    activity="Registration verification, Wi-Fi credential issuance, and table seating allocation.",
                    venue_allocated=f"{venue.venue_name} - Reception Foyer",
                    responsible_team="SAC Volunteers & IT Desk"
                ))
                items.append(ScheduleItem(
                    day=1,
                    time_slot="10:00 AM - 11:30 AM",
                    stage_name="Grand Inauguration & Problem Statements Release",
                    activity="Welcome address by HOD / Dignitaries, rules briefing, and release of hack tracks.",
                    venue_allocated=venue.venue_name,
                    responsible_team=dept
                ))
                items.append(ScheduleItem(
                    day=1,
                    time_slot="11:30 AM - 07:00 PM",
                    stage_name="Phase 1: Architecture & Prototyping Sprint",
                    activity="Continuous coding sprint, technical mentorship check-in round 1, and architecture validation.",
                    venue_allocated=f"{venue.venue_name} & Lab Wings",
                    responsible_team="Technical Committee & Mentors"
                ))
                items.append(ScheduleItem(
                    day=1,
                    time_slot="07:00 PM - OVERNIGHT",
                    stage_name="Phase 2: Overnight Deep Build & Mid-Evaluation",
                    activity="Midnight evaluation checkpoint, refreshment rounds, and continuous hackathon development.",
                    venue_allocated=venue.venue_name,
                    responsible_team="Night Shift Coordinators & Security"
                ))
                items.append(ScheduleItem(
                    day=2,
                    time_slot="08:00 AM - 01:00 PM",
                    stage_name="Phase 3: Integration, Polish & Code Freeze",
                    activity="Final software testing, repository submissions, PPT upload, and hard code freeze.",
                    venue_allocated=venue.venue_name,
                    responsible_team="Jury Support Team"
                ))
                items.append(ScheduleItem(
                    day=2,
                    time_slot="02:00 PM - 05:30 PM",
                    stage_name="Grand Jury Pitching & Award Ceremony",
                    activity="Top 10 finalist stage demos, jury scoring, prize distribution, and valedictory ceremony.",
                    venue_allocated=venue.venue_name,
                    responsible_team="SAC Leadership & Department HOD"
                ))
            else:
                items.append(ScheduleItem(
                    day=1,
                    time_slot="09:00 AM - 10:30 AM",
                    stage_name="Inauguration & Track Briefing",
                    activity="Hackathon commencement, team kit distribution, and track briefing.",
                    venue_allocated=venue.venue_name,
                    responsible_team=dept
                ))
                items.append(ScheduleItem(
                    day=1,
                    time_slot="10:30 AM - 04:00 PM",
                    stage_name="Rapid Development Hack Sprint",
                    activity="Sprint coding, live mentor rounds, and prototype development.",
                    venue_allocated=venue.venue_name,
                    responsible_team="Technical Coordinators"
                ))
                items.append(ScheduleItem(
                    day=1,
                    time_slot="04:30 PM - 06:00 PM",
                    stage_name="Jury Evaluation & Prize Distribution",
                    activity="Live project demos, evaluation, certificate and cash prize distribution.",
                    venue_allocated=venue.venue_name,
                    responsible_team="Organizing Committee"
                ))

        elif "cultural" in event_type or "fest" in event_type:
            items.append(ScheduleItem(
                day=1,
                time_slot="04:00 PM - 05:30 PM",
                stage_name="Sound Check & Stage Logistics Setup",
                activity="Audio level balancing, mic sound checks, green room allocation, and lighting presets.",
                venue_allocated=venue.venue_name,
                responsible_team="Facilities & AV Sound Team"
            ))
            items.append(ScheduleItem(
                day=1,
                time_slot="05:30 PM - 07:00 PM",
                stage_name="Classical & Traditional Arts Showcase",
                activity="Inaugural lamp lighting, classical dance performances, and instrumental orchestra.",
                venue_allocated=venue.venue_name,
                responsible_team="Cultural Club Leads"
            ))
            items.append(ScheduleItem(
                day=1,
                time_slot="07:00 PM - 09:30 PM",
                stage_name="Live Band & Celebrity Performance",
                activity="Student rock band performance, thematic dance acts, and guest artist stage show.",
                venue_allocated=venue.venue_name,
                responsible_team="SAC & Campus Security"
            ))

        elif "nss" in event_type or "social" in event_type:
            items.append(ScheduleItem(
                day=1,
                time_slot="08:00 AM - 09:30 AM",
                stage_name="Volunteer Assembly & Briefing",
                activity="Roll call, squad kit distribution (gloves, badges, first aid), and mission briefing.",
                venue_allocated=venue.venue_name,
                responsible_team="NSS Coordinators"
            ))
            items.append(ScheduleItem(
                day=1,
                time_slot="09:30 AM - 01:00 PM",
                stage_name="Field Activity & Community Outreach",
                activity="Execution of cleanliness drive, tree plantation, and rural awareness campaign.",
                venue_allocated="Campus Grounds & Surrounding Zones",
                responsible_team="Field Supervisors & Security"
            ))
            items.append(ScheduleItem(
                day=1,
                time_slot="02:00 PM - 03:30 PM",
                stage_name="Debriefing & Appreciation Session",
                activity="Activity reflection, photo session, and distribution of participation certificates.",
                venue_allocated=venue.venue_name,
                responsible_team="NSS Cell Leadership"
            ))

        elif "seminar" in event_type or "academic" in event_type or "conference" in event_type:
            items.append(ScheduleItem(
                day=1,
                time_slot="09:30 AM - 10:30 AM",
                stage_name="Keynote Address & Research Presentation",
                activity="Opening ceremony, keynote address by guest speaker, and research overview.",
                venue_allocated=venue.venue_name,
                responsible_team=dept
            ))
            items.append(ScheduleItem(
                day=1,
                time_slot="11:00 AM - 01:00 PM",
                stage_name="Technical Session 1: Papers & Innovations",
                activity="Domain paper presentations, live Q&A, and peer academic reviews.",
                venue_allocated=venue.venue_name,
                responsible_team="Faculty Coordinators"
            ))
            items.append(ScheduleItem(
                day=1,
                time_slot="02:00 PM - 04:00 PM",
                stage_name="Panel Discussion & Interactive Colloquium",
                activity="Industry-academia panel discussion, emerging tech exchange, and student interaction.",
                venue_allocated=venue.venue_name,
                responsible_team="Session Chairs"
            ))
            items.append(ScheduleItem(
                day=1,
                time_slot="04:00 PM - 05:00 PM",
                stage_name="Valedictory & Networking High Tea",
                activity="Certificate distribution, formal vote of thanks, and networking high tea.",
                venue_allocated=venue.venue_name,
                responsible_team="Hospitality & SAC"
            ))

        else:
            items.append(ScheduleItem(
                day=1,
                time_slot="09:30 AM - 11:00 AM",
                stage_name="Inaugural Session",
                activity="Opening address and event overview.",
                venue_allocated=venue.venue_name,
                responsible_team=dept
            ))
            items.append(ScheduleItem(
                day=1,
                time_slot="11:30 AM - 03:30 PM",
                stage_name="Main Event Execution",
                activity="Scheduled program activities and interactive sessions.",
                venue_allocated=venue.venue_name,
                responsible_team=dept
            ))
            items.append(ScheduleItem(
                day=1,
                time_slot="03:30 PM - 04:30 PM",
                stage_name="Closing & Acknowledgments",
                activity="Concluding session and acknowledgments.",
                venue_allocated=venue.venue_name,
                responsible_team=dept
            ))

        return items

conflict_schedule_agent = ConflictScheduleAgent()
