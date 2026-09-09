"""Synthetic ReadinessAssessment fixtures for zero-quota UI validation.

These fixtures are intentionally non-live. They use example.com URLs and are only
served through the environment-gated UI preview endpoint.
"""

from app.models import ReadinessAssessment


_PREVIEW_FIXTURES = {
    "no-go": ReadinessAssessment.model_validate({
        "status": "NO-GO",
        "readiness_score": 36,
        "summary": (
            "The shoot should not proceed on the current schedule. Required traffic-control approval "
            "cannot be completed within the remaining lead time, and the planned drone operation lacks "
            "confirmed authorization for the proposed night-flight profile. Several operational controls "
            "also remain unresolved and must be closed before a revised call time is approved."
        ),
        "mission_specs": {
            "location": "Downtown Los Angeles, CA",
            "date": "Tomorrow, 6:00 PM call time",
            "remaining_time_hours": 18,
            "activities": [
                "exterior night filming",
                "50 extras",
                "temporary lane control",
                "drone footage",
                "portable generator power"
            ]
        },
        "blockers": [
            {
                "title": "Traffic-control approval cannot meet required notice period",
                "reason": (
                    "The planned curb and lane occupation requires a traffic-control review with a minimum "
                    "72-hour submission window. Approximately 18 hours remain before call time, so the approval "
                    "cannot be obtained within the stated lead time for the current schedule."
                ),
                "category": "road_control",
                "required_lead_time_hours": 72,
                "remaining_time_hours": 18,
                "sources": [
                    "https://example.com/film-office/production-permits/traffic-control-and-lane-occupation/temporary-lane-closure-review-requirements"
                ]
            },
            {
                "title": "Night drone authorization is not confirmed",
                "reason": (
                    "The flight plan includes operation after civil twilight over a controlled production area. "
                    "The assessment has no confirmed authorization or documented operating basis for the planned "
                    "night-flight profile, so aerial filming cannot be cleared as proposed."
                ),
                "category": "drone_uas",
                "required_lead_time_hours": 24,
                "remaining_time_hours": 18,
                "sources": [
                    "https://example.com/aviation/uas/operational-rules/night-operations-and-controlled-production-sites"
                ]
            }
        ],
        "risks": [
            {
                "title": "Generator noise may exceed the planned night-work envelope",
                "severity": "HIGH",
                "category": "generator_noise",
                "description": (
                    "Portable generator use is planned through the night period near mixed residential frontage. "
                    "Without a confirmed low-noise placement plan, the production could trigger complaints or a "
                    "location shutdown even if the primary filming permit is otherwise valid."
                ),
                "mitigation": (
                    "Relocate the generator behind acoustic barriers, verify the permitted operating window with "
                    "the location authority, and keep a lower-noise backup power option available."
                ),
                "sources": [
                    "https://example.com/city-code/environmental-noise/nighttime-construction-and-temporary-event-equipment"
                ]
            },
            {
                "title": "Pedestrian interface is under-controlled for the expected crowd size",
                "severity": "MEDIUM",
                "category": "crowd_control",
                "description": (
                    "Approximately 50 extras, crew movement and equipment staging are concentrated beside an active "
                    "public footpath. The current scope does not show a dedicated pedestrian marshal or segregated "
                    "holding route."
                ),
                "mitigation": (
                    "Add trained pedestrian marshals, define a protected crossing and holding area, and brief all "
                    "departments on public-interface controls before first unit call."
                ),
                "sources": [
                    "https://example.com/film-office/safety-guidance/public-right-of-way-and-pedestrian-management-for-location-filming"
                ]
            },
            {
                "title": "Night load-out creates fatigue and visibility exposure",
                "severity": "MEDIUM",
                "category": "crew_safety",
                "description": (
                    "The current plan places equipment strike and vehicle movement late at night after a long production "
                    "day, increasing fatigue risk and reducing visibility around the loading zone."
                ),
                "mitigation": (
                    "Assign a dedicated load-out supervisor, provide task lighting, separate vehicles from pedestrian "
                    "paths, and confirm crew-hours compliance before the final schedule is issued."
                ),
                "sources": [
                    "https://example.com/production-safety/night-work/fatigue-lighting-and-vehicle-movement-controls"
                ]
            }
        ],
        "conditions": [
            {
                "condition": "Revise the shoot schedule or remove the traffic-control requirement",
                "action_required": (
                    "Move the affected scenes to a date that satisfies the authority's submission window, or redesign "
                    "the blocking so all filming remains within an already authorized private footprint."
                ),
                "sources": [
                    "https://example.com/film-office/production-permits/traffic-control-and-lane-occupation/temporary-lane-closure-review-requirements"
                ]
            },
            {
                "condition": "Document a compliant drone operating basis before aerial filming",
                "action_required": (
                    "Confirm the pilot, aircraft, night-operation requirements, production-area controls and any local "
                    "site permissions in writing before the drone unit is released to shoot."
                ),
                "sources": [
                    "https://example.com/aviation/uas/operational-rules/night-operations-and-controlled-production-sites"
                ]
            }
        ],
        "recommended_actions": [
            "Escalate the traffic-control lead-time failure to production management and reschedule the affected exterior scenes.",
            "Obtain written confirmation of the drone operating basis and remove aerial shots from the call sheet until confirmed.",
            "Issue a revised site plan showing pedestrian marshals, public-interface barriers and a protected equipment route.",
            "Confirm the permitted generator operating window and publish the final acoustic-control plan to locations and electrical teams.",
            "Re-run the readiness assessment after the schedule, traffic-control scope and drone documentation have been updated."
        ],
        "findings": [
            {
                "category": "road_control",
                "requirement": "traffic_control_review",
                "description": "Temporary lane occupation requires advance traffic-control review.",
                "mandatory": True,
                "approval_status": "not_confirmed",
                "required_lead_time_hours": 72,
                "remaining_time_hours": 18,
                "source_urls": [
                    "https://example.com/film-office/production-permits/traffic-control-and-lane-occupation/temporary-lane-closure-review-requirements"
                ],
                "details": "Synthetic preview fact used to stress-test lead-time presentation."
            },
            {
                "category": "drone_uas",
                "requirement": "night_operation_authorization",
                "description": "The planned drone profile requires a documented compliant night-operation basis.",
                "mandatory": True,
                "approval_status": "not_confirmed",
                "required_lead_time_hours": 24,
                "remaining_time_hours": 18,
                "source_urls": [
                    "https://example.com/aviation/uas/operational-rules/night-operations-and-controlled-production-sites"
                ],
                "details": "Synthetic preview fact used to stress-test blocker and evidence density."
            }
        ],
        "evidence": [
            {
                "title": "Temporary Lane Closure and Traffic-Control Review Requirements for Location Filming",
                "url": "https://example.com/film-office/production-permits/traffic-control-and-lane-occupation/temporary-lane-closure-review-requirements",
                "excerpts": [
                    "Applications affecting an active travel lane should be submitted no later than 72 hours before the requested control period.",
                    "Incomplete traffic-control diagrams may be returned for revision before review begins."
                ],
                "query": "Downtown Los Angeles filming temporary lane closure permit lead time traffic control review",
                "search_id": "preview-search-001"
            },
            {
                "title": "Uncrewed Aircraft Systems: Night Operations and Controlled Production Sites",
                "url": "https://example.com/aviation/uas/operational-rules/night-operations-and-controlled-production-sites",
                "excerpts": [
                    "Night operations require the remote pilot to satisfy the applicable operating requirements and maintain required anti-collision lighting.",
                    "Operations over or near people must remain within the operating limitations that apply to the aircraft and flight profile."
                ],
                "query": "commercial film drone night operation requirements controlled production site",
                "search_id": "preview-search-002"
            },
            {
                "title": "Nighttime Environmental Noise Guidance for Temporary Event and Production Equipment",
                "url": "https://example.com/city-code/environmental-noise/nighttime-construction-and-temporary-event-equipment",
                "excerpts": [
                    "Temporary powered equipment should be located and screened to minimize avoidable nighttime disturbance.",
                    "Additional restrictions may apply where equipment operates adjacent to residential uses."
                ],
                "query": "night film shoot portable generator noise restrictions residential frontage",
                "search_id": "preview-search-003"
            },
            {
                "title": "Public Right-of-Way Filming Safety: Pedestrian Management, Staging and Access Routes",
                "url": "https://example.com/film-office/safety-guidance/public-right-of-way-and-pedestrian-management-for-location-filming",
                "excerpts": [
                    "Productions should preserve a safe public path unless an approved closure or alternate route is in place.",
                    "Crowd, cable and equipment movements should be actively managed where they intersect with public access."
                ],
                "query": "film production public sidewalk pedestrian management extras equipment staging safety",
                "search_id": "preview-search-004"
            }
        ]
    }),
    "conditional": ReadinessAssessment.model_validate({
        "status": "CONDITIONAL GO",
        "readiness_score": 72,
        "summary": (
            "No hard blocker is currently established, but the shoot should proceed only after the remaining permit "
            "confirmation, generator controls and pedestrian-management measures are closed. The available lead times "
            "appear workable if the production team acts immediately and documents each approval before call time."
        ),
        "mission_specs": {
            "location": "Arts District, Los Angeles, CA",
            "date": "Three days from now, 5:00 PM call time",
            "remaining_time_hours": 68,
            "activities": ["exterior filming", "small drone unit", "30 extras", "portable generator"]
        },
        "blockers": [],
        "risks": [
            {
                "title": "Permit review window is tight",
                "severity": "MEDIUM",
                "category": "permit_timing",
                "description": "The remaining schedule is feasible but leaves little recovery time if the filing is returned for correction.",
                "mitigation": "Submit the complete package immediately and assign one owner to respond to authority comments the same day.",
                "sources": ["https://example.com/film-office/permits/location-filming-application-timelines"]
            },
            {
                "title": "Public-interface plan still needs final marshal assignments",
                "severity": "LOW",
                "category": "crowd_control",
                "description": "The route plan is suitable, but named pedestrian marshals have not yet been assigned to the call sheet.",
                "mitigation": "Assign marshals by position and include the route briefing in the safety meeting.",
                "sources": ["https://example.com/film-office/safety/public-interface-plan"]
            }
        ],
        "conditions": [
            {
                "condition": "Receive written location-filming permit confirmation",
                "action_required": "Submit the final site plan immediately and retain the authority approval with the production documents.",
                "sources": ["https://example.com/film-office/permits/location-filming-application-timelines"]
            },
            {
                "condition": "Close the generator noise-control plan",
                "action_required": "Confirm equipment placement, acoustic screening and the permitted operating window before technical call.",
                "sources": ["https://example.com/city-code/noise/temporary-production-equipment"]
            },
            {
                "condition": "Assign pedestrian marshals and briefing responsibilities",
                "action_required": "Add named marshals to the call sheet and brief the public-interface route before cameras roll.",
                "sources": ["https://example.com/film-office/safety/public-interface-plan"]
            }
        ],
        "recommended_actions": [
            "Submit the complete permit package now and track authority feedback through one production owner.",
            "Finalize generator placement and acoustic screening before the technical scout is closed.",
            "Assign named pedestrian marshals and add the public-interface route to the safety briefing.",
            "Recheck readiness after written permit confirmation is received."
        ],
        "findings": [
            {
                "category": "location_permit",
                "requirement": "filming_permit",
                "description": "A location-filming permit remains mandatory and is not yet confirmed.",
                "mandatory": True,
                "approval_status": "not_confirmed",
                "required_lead_time_hours": 48,
                "remaining_time_hours": 68,
                "source_urls": ["https://example.com/film-office/permits/location-filming-application-timelines"],
                "details": "Synthetic preview condition with feasible but tight lead time."
            }
        ],
        "evidence": [
            {
                "title": "Location Filming Application Timelines and Required Submission Package",
                "url": "https://example.com/film-office/permits/location-filming-application-timelines",
                "excerpts": [
                    "Standard location applications should be complete before review begins.",
                    "Applications involving public-space impacts may require additional review time."
                ],
                "query": "location filming permit application lead time public space production",
                "search_id": "preview-search-101"
            },
            {
                "title": "Temporary Production Equipment Noise Controls",
                "url": "https://example.com/city-code/noise/temporary-production-equipment",
                "excerpts": [
                    "Equipment placement and screening should reduce avoidable impact on adjacent occupancies."
                ],
                "query": "temporary film generator noise control city guidance",
                "search_id": "preview-search-102"
            },
            {
                "title": "Public-Interface Plan for Film and Commercial Production",
                "url": "https://example.com/film-office/safety/public-interface-plan",
                "excerpts": [
                    "Productions should assign responsible personnel where crew or equipment interact with public routes."
                ],
                "query": "film production pedestrian marshal public route safety plan",
                "search_id": "preview-search-103"
            }
        ]
    }),
    "go": ReadinessAssessment.model_validate({
        "status": "GO",
        "readiness_score": 94,
        "summary": (
            "The planned shoot is ready to proceed based on the supplied scope. Required permissions are documented, "
            "the location footprint remains within the approved area, and the remaining operational risk is low and "
            "covered by standard crew controls."
        ),
        "mission_specs": {
            "location": "Private studio backlot, Los Angeles, CA",
            "date": "Next week, 8:00 AM call time",
            "remaining_time_hours": 144,
            "activities": ["controlled exterior set", "30 crew", "no road control", "no drone"]
        },
        "blockers": [],
        "risks": [
            {
                "title": "Routine vehicle movement during load-in",
                "severity": "LOW",
                "category": "site_logistics",
                "description": "Crew vehicles and equipment trucks share the backlot service road during load-in.",
                "mitigation": "Use the approved one-way vehicle plan and keep a spotter at the loading turn.",
                "sources": ["https://example.com/studio-operations/backlot/vehicle-and-loading-plan"]
            }
        ],
        "conditions": [],
        "recommended_actions": [
            "Confirm the approved one-way vehicle plan during the morning safety briefing.",
            "Keep the permit and location agreement available to the location manager throughout the shoot."
        ],
        "findings": [
            {
                "category": "private_property",
                "requirement": "property_use_agreement",
                "description": "The location agreement is documented for the planned production footprint.",
                "mandatory": True,
                "approval_status": "approved",
                "required_lead_time_hours": None,
                "remaining_time_hours": 144,
                "source_urls": ["https://example.com/studio-operations/backlot/location-use-agreement"],
                "details": "Synthetic approved finding for compact GO-state rendering."
            }
        ],
        "evidence": [
            {
                "title": "Backlot Location Use Agreement and Approved Production Footprint",
                "url": "https://example.com/studio-operations/backlot/location-use-agreement",
                "excerpts": ["The approved production footprint includes the identified exterior set and service access route."],
                "query": "private studio backlot approved production footprint location agreement",
                "search_id": "preview-search-201"
            },
            {
                "title": "Backlot Vehicle and Loading Plan",
                "url": "https://example.com/studio-operations/backlot/vehicle-and-loading-plan",
                "excerpts": ["Load-in uses a one-way service-road pattern with a spotter at the loading turn."],
                "query": "studio backlot vehicle loading one way service road safety",
                "search_id": "preview-search-202"
            }
        ]
    })
}


def get_preview_assessment(scenario: str) -> ReadinessAssessment | None:
    """Return a synthetic preview assessment by scenario name."""
    return _PREVIEW_FIXTURES.get(scenario)
