"""
Deterministic Lead Disqualification Engine.
Disqualifies competitors, freemail domains, and non-target company types before scoring.
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple

class LeadDisqualifier:
    def __init__(self, rubric_path: str = None):
        if rubric_path is None:
            rubric_path = Path(__file__).parent.parent / "config" / "icp_rubric.json"
        with open(rubric_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)["target_icp"]

    def evaluate(self, form_input: Dict[str, Any], enrichment_data: Dict[str, Any] = None) -> Tuple[bool, str, str]:
        """
        Evaluates a lead against disqualification criteria.
        Returns: (is_disqualified, reason, rule_name)
        """
        email = form_input.get("work_email", "").lower()
        domain = form_input.get("company_domain", "").lower()
        if not domain and "@" in email:
            domain = email.split("@")[1]

        # 1. Freemail Check
        for freemail_domain in self.config["disqualified_email_domains"]:
            if domain == freemail_domain or email.endswith("@" + freemail_domain):
                return True, f"Freemail provider detected ({freemail_domain}). B2B corporate domain required.", "DISQUALIFY_FREEMAIL"

        # 2. Competitor Check
        for comp_domain in self.config["competitor_domains"]:
            if domain == comp_domain:
                return True, f"Competitor domain identified ({comp_domain}). Lead flagged for security recon audit.", "DISQUALIFY_COMPETITOR"

        # 3. Enrichment Data Checks (if available)
        if enrichment_data:
            company_type = enrichment_data.get("company_type", "")
            if company_type in self.config["disqualified_company_types"]:
                return True, f"Company type '{company_type}' does not match product target ICP (Agencies/Consultancies excluded).", "DISQUALIFY_COMPANY_TYPE"

            geo = enrichment_data.get("geography", "")
            allowed_geos = self.config["allowed_geographies"]
            if geo and geo != "Unknown" and not any(allowed in geo for allowed in allowed_geos):
                return True, f"Geography '{geo}' is outside target sales territories ({', '.join(allowed_geos)}).", "DISQUALIFY_GEOGRAPHY"

        return False, "", "PASSED_PREFILTER"

if __name__ == "__main__":
    disqualifier = LeadDisqualifier()
    test_lead = {"work_email": "test@gmail.com", "company_domain": "gmail.com"}
    is_disq, reason, rule = disqualifier.evaluate(test_lead)
    print(f"Disqualified: {is_disq} | Rule: {rule} | Reason: {reason}")
