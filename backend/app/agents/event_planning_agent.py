import re
import time
from typing import Dict, Any, List
from app.services.claude_service import claude_service
from app.schemas.plan import EventDetails

class EventPlanningAgent:
    """
    Agent 1 — Event Planning Agent
    Understands natural language prompt, extracts event type, participant count,
    duration, category, requirements, and documents all assumptions.
    """
    def __init__(self):
        self.name = "Event Planning Agent"
        self.responsibility = "NLP Requirement Understanding & Scope Extraction"

    async def execute(
        self,
        prompt: str,
        venues_catalog: List[Dict[str, Any]],
        resources_catalog: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        start_time = time.time()
        ai_engine_used = "Anthropic Claude API"

        # Try Anthropic Claude first if configured
        claude_result = await claude_service.analyze_event_prompt(prompt, venues_catalog, resources_catalog)

        if claude_result:
            event_details = EventDetails(
                title=claude_result.get("title", "Campus Event"),
                category=claude_result.get("category", "Technical"),
                event_type=claude_result.get("event_type", "Event"),
                expected_participants=int(claude_result.get("expected_participants", 300)),
                duration=claude_result.get("duration", "1 Day"),
                duration_days=int(claude_result.get("duration_days", 1)),
                duration_hours_per_day=int(claude_result.get("duration_hours_per_day", 6)),
                target_audience=claude_result.get("target_audience", "Vignan University Students"),
                host_department=claude_result.get("host_department", "Academic Affairs & SAC"),
                key_objectives=claude_result.get("key_objectives", ["Promote student engagement and campus excellence"]),
                special_requirements=claude_result.get("special_requirements", ["Standard AV Setup"])
            )
            assumptions = claude_result.get("assumptions", [
                "Assumed standard daytime schedule (09:00 AM - 05:00 PM)",
                f"Assumed estimated participant turnout of {event_details.expected_participants}"
            ])
            resource_demands = claude_result.get("resource_demands", {})
            schedule_outline = claude_result.get("schedule_outline", [])
            recommendations = claude_result.get("recommendations", [])
        else:
            # High-precision deterministic NLP parser as fallback
            ai_engine_used = "Deterministic NLP Campus Engine (Standby Mode)"
            extracted = self._parse_deterministic(prompt)
            event_details = extracted["event_details"]
            assumptions = extracted["assumptions"]
            resource_demands = extracted["resource_demands"]
            schedule_outline = extracted["schedule_outline"]
            recommendations = extracted["recommendations"]

        exec_time = round((time.time() - start_time) * 1000, 2)

        return {
            "event_details": event_details,
            "assumptions": assumptions,
            "resource_demands": resource_demands,
            "schedule_outline": schedule_outline,
            "recommendations": recommendations,
            "ai_engine_used": ai_engine_used,
            "trace": {
                "agent_id": "agent-1-planning",
                "agent_name": self.name,
                "responsibility": self.responsibility,
                "status": "completed",
                "execution_time_ms": exec_time,
                "summary": f"Successfully parsed '{event_details.title}' ({event_details.expected_participants} participants, {event_details.duration}).",
                "details": {
                    "event_type": event_details.event_type,
                    "category": event_details.category,
                    "participants": event_details.expected_participants
                }
            }
        }

    def _parse_deterministic(self, prompt: str) -> Dict[str, Any]:
        """Extracts event structure using regex and university taxonomy."""
        prompt_lower = prompt.lower()

        # 1. Extract Participants
        participants = 300  # Default assumption
        p_match = re.search(r'(\d+)\s*(?:students?|participants?|attendees?|delegates?|people|volunteers?)', prompt_lower)
        if p_match:
            participants = int(p_match.group(1))
        else:
            # Look for isolated numbers
            numbers = re.findall(r'\b\d+\b', prompt)
            for num in numbers:
                val = int(num)
                if val >= 20 and val <= 5000:
                    participants = val
                    break

        # 2. Extract Duration
        days = 1
        hours = 6
        duration_label = "1 Day"
        if "2-day" in prompt_lower or "2 days" in prompt_lower or "two day" in prompt_lower:
            days = 2
            duration_label = "2 Days"
        elif "3-day" in prompt_lower or "3 days" in prompt_lower:
            days = 3
            duration_label = "3 Days"
        elif "half day" in prompt_lower or "half-day" in prompt_lower:
            hours = 4
            duration_label = "Half Day (4 Hours)"
        elif "evening" in prompt_lower or "night" in prompt_lower:
            hours = 4
            duration_label = "Evening (4 Hours)"

        # 3. Categorize & Title Event
        if "hackathon" in prompt_lower or "ideathon" in prompt_lower or "code" in prompt_lower:
            category = "Technical"
            event_type = "Hackathon"
            title = f"Vignan {duration_label} Hackathon 2026"
            host_dept = "Department of Computer Science & Engineering (CSE) and IT"
            target_audience = "Engineering Students, Coders & Innovators"
            key_objectives = [
                "Foster rapid prototyping, software innovation, and teamwork",
                "Engage 500+ student developers with industry problem statements",
                "Evaluate and award top AI & full-stack software solutions"
            ]
            special_reqs = ["High-density Wi-Fi nodes", "Power strips per team table", "Overnight lab access"]
            res_demands = {
                "projectors": max(2, participants // 150),
                "microphones": 4,
                "speakers": 2,
                "led_screens": 1,
                "chairs": participants,
                "tables": max(20, participants // 4),
                "laptops": max(5, participants // 50),
                "wifi_access_points": max(4, participants // 40),
                "security_guards": max(4, participants // 80),
                "volunteers": max(10, participants // 25)
            }
        elif "cultural" in prompt_lower or "mahotsav" in prompt_lower or "beat the street" in prompt_lower or "music" in prompt_lower or "dance" in prompt_lower:
            category = "Cultural / Major"
            event_type = "Cultural Fest"
            title = f"Vignan Tarang Cultural Celebrations"
            host_dept = "Student Activity Center (SAC) & Cultural Committee"
            target_audience = "University Students, Faculty & Special Guests"
            key_objectives = [
                "Showcase student artistic and musical talents",
                "Celebrate university cultural diversity and creative arts",
                "Provide a high-energy live stage experience"
            ]
            special_reqs = ["Acoustic stage lighting", "High-power PA audio setup", "Dressing green rooms"]
            res_demands = {
                "projectors": 2,
                "microphones": 8,
                "speakers": 4,
                "led_screens": 3,
                "chairs": participants,
                "tables": 20,
                "cameras": 4,
                "wifi_access_points": 6,
                "security_guards": max(10, participants // 40),
                "volunteers": max(20, participants // 20)
            }
        elif "nss" in prompt_lower or "swachh" in prompt_lower or "social" in prompt_lower or "volunteer" in prompt_lower or "camp" in prompt_lower:
            category = "NSS / Social"
            event_type = "Social & Outreach Drive"
            title = "VFSTR NSS Community Orientation & Service Drive"
            host_dept = "NSS Cell & Community Engagement Wing"
            target_audience = "Registered Student Volunteers & Staff Coordinators"
            key_objectives = [
                "Mobilize volunteers for campus hygiene and rural community outreach",
                "Conduct training on public health awareness and safety protocols",
                "Organize volunteer dispatch squads across campus blocks"
            ]
            special_reqs = ["Field briefing audio", "First aid desk support", "Dispatch logistics"]
            res_demands = {
                "projectors": 2,
                "microphones": 4,
                "speakers": 2,
                "chairs": participants,
                "tables": 15,
                "buses": max(2, participants // 50),
                "security_guards": 4,
                "volunteers": participants
            }
        elif "seminar" in prompt_lower or "symposium" in prompt_lower or "conference" in prompt_lower or "lecture" in prompt_lower or "talk" in prompt_lower:
            category = "Academic / Workshop"
            event_type = "Technical Seminar"
            title = "VFSTR Advanced Academic Symposium & Keynote"
            host_dept = "Faculty of Engineering & Research Deanship"
            target_audience = "Scholars, Faculty & Senior B.Tech Students"
            key_objectives = [
                "Disseminate contemporary research breakthroughs and domain insights",
                "Host distinguished keynote speakers and industry leaders",
                "Facilitate active Q&A, research poster interactions, and networking"
            ]
            special_reqs = ["Dual podium mics", "Central AC", "High-clarity AV projection"]
            res_demands = {
                "projectors": max(2, participants // 200),
                "microphones": 6,
                "speakers": 2,
                "chairs": participants,
                "tables": 10,
                "laptops": 4,
                "wifi_access_points": 4,
                "security_guards": 4,
                "volunteers": max(8, participants // 40)
            }
        else:
            category = "General Campus Event"
            event_type = "University Event"
            title = f"Vignan Campus Event ({participants} Attendees)"
            host_dept = "Academic Affairs & SAC"
            target_audience = "VFSTR Campus Community"
            key_objectives = [
                "Ensure smooth execution of university event operations",
                "Provide seamless seating, AV, and attendee coordination"
            ]
            special_reqs = ["Standard AV projection", "Seating alignment"]
            res_demands = {
                "projectors": 2,
                "microphones": 4,
                "speakers": 2,
                "chairs": participants,
                "tables": max(10, participants // 20),
                "wifi_access_points": 4,
                "security_guards": max(4, participants // 80),
                "volunteers": max(10, participants // 30)
            }

        # Document explicit assumptions
        assumptions = [
            f"Assumed attendee volume of approximately {participants} based on request parameters.",
            f"Assumed duration of {duration_label} with standard academic calendar timings.",
            f"Mapped hosting responsibility to {host_dept}.",
            "Assumed standard campus electrical backup and network bandwidth."
        ]

        recommendations = [
            "Submit event proposal to HOD at least 5 working days prior for clearance.",
            "Coordinate with Central IT 24 hours ahead for dedicated SSID provisioning."
        ]

        event_details = EventDetails(
            title=title,
            category=category,
            event_type=event_type,
            expected_participants=participants,
            duration=duration_label,
            duration_days=days,
            duration_hours_per_day=hours,
            target_audience=target_audience,
            host_department=host_dept,
            key_objectives=key_objectives,
            special_requirements=special_reqs
        )

        return {
            "event_details": event_details,
            "assumptions": assumptions,
            "resource_demands": res_demands,
            "schedule_outline": [],
            "recommendations": recommendations
        }

event_planning_agent = EventPlanningAgent()
