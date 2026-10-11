"""
Priority Lead Router & Latency Auditor.
Routes leads based on score tier and tracks wall-clock latency against the 30-minute SLA budget.
"""

import time
from typing import Dict, Any

class LeadRouter:
    def route(self, scored_lead: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        elapsed_sec = time.perf_counter() - start_time
        tier = scored_lead.get("tier", "UNQUALIFIED")
        disqualified = scored_lead.get("disqualified", False)

        if disqualified:
            action = "AUTO_REJECT_SILENT"
            queue = "DISQUALIFIED_LOG"
            sla_status = "PASSED_FAST_FAIL"
        elif tier == "QUALIFIED":
            action = "ASSIGN_SDR_IMMEDIATE_TOUCH"
            queue = "HIGH_PRIORITY_SDR_QUEUE"
            sla_status = "PASSED_SLA" if elapsed_sec <= 1800 else "BREACHED_SLA"
        elif tier == "NURTURE":
            action = "ENROLL_MARKETING_DRIP"
            queue = "NURTURE_QUEUE"
            sla_status = "PASSED_SLA"
        else:
            action = "NO_ACTION_LOW_FIT"
            queue = "LOW_FIT_ARCHIVE"
            sla_status = "PASSED_SLA"

        return {
            "routed_queue": queue,
            "recommended_action": action,
            "sla_performance": {
                "wall_clock_seconds": round(elapsed_sec, 4),
                "budget_seconds": 1800,  # 30-minute budget
                "budget_utilized_pct": round((elapsed_sec / 1800) * 100, 6),
                "sla_status": sla_status
            }
        }
