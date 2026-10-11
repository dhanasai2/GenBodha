"""
Lead Enrichment Module.
Maintains a strict wall between Form Input (prospect-provided) and Enrichment Data (retrieved facts).
"""

import json
from pathlib import Path
from typing import Dict, Any

class LeadEnricher:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "enrichment_db.json"
        with open(db_path, "r", encoding="utf-8") as f:
            self.enrichment_db = json.load(f)

    def enrich(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriches a lead form submission with company intelligence.
        Explicitly separates form_input from enrichment_data.
        """
        form_input = lead.get("form_input", {})
        domain = form_input.get("company_domain", "").lower()

        retrieved_data = self.enrichment_db.get(domain, None)

        if retrieved_data:
            enrichment_payload = {
                "found": True,
                "company_name": retrieved_data.get("company_name", domain),
                "industry": retrieved_data.get("industry", "Unknown"),
                "total_employees": retrieved_data.get("total_employees", 0),
                "engineering_headcount": retrieved_data.get("engineering_headcount", 0),
                "tech_stack": retrieved_data.get("tech_stack", []),
                "geography": retrieved_data.get("geography", "Unknown"),
                "headquarters": retrieved_data.get("headquarters", "Unknown"),
                "company_type": retrieved_data.get("company_type", "Unknown"),
                "snippets": retrieved_data.get("verified_snippets", [])
            }
        else:
            enrichment_payload = {
                "found": False,
                "company_name": domain.capitalize() if domain else "Unknown",
                "industry": "Unknown",
                "total_employees": 0,
                "engineering_headcount": 0,
                "tech_stack": [],
                "geography": "Unknown",
                "headquarters": "Unknown",
                "company_type": "Unknown",
                "snippets": []
            }

        return {
            "lead_id": lead.get("lead_id"),
            "timestamp": lead.get("timestamp"),
            "form_input": form_input,
            "enrichment_data": enrichment_payload,
            "provenance": {
                "form_fields": list(form_input.keys()),
                "enrichment_fields": list(enrichment_payload.keys()) if enrichment_payload["found"] else [],
                "enrichment_status": "SUCCESS" if enrichment_payload["found"] else "NOT_FOUND"
            }
        }

if __name__ == "__main__":
    enricher = LeadEnricher()
    test_lead = {
        "lead_id": "TEST-1",
        "form_input": {"name": "Test", "work_email": "sjenkins@cloudscale.io", "company_domain": "cloudscale.io"}
    }
    result = enricher.enrich(test_lead)
    print(json.dumps(result, indent=2))
