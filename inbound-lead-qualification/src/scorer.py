"""
ICP Lead Scorer.
Evaluates enriched lead object against ICP rubric using deterministic scoring rules.
"""

import json
from pathlib import Path
from typing import Dict, Any

class LeadScorer:
    def __init__(self, rubric_path: str = None):
        if rubric_path is None:
            rubric_path = Path(__file__).parent.parent / "config" / "icp_rubric.json"
        with open(rubric_path, "r", encoding="utf-8") as f:
            self.rubric = json.load(f)
        self.weights = self.rubric["scoring_weights"]
        self.thresholds = self.rubric["qualification_thresholds"]

    def score_lead(self, enriched_lead: Dict[str, Any], is_disqualified: bool = False, disqualification_reason: str = "") -> Dict[str, Any]:
        """
        Calculates ICP score breakdown and final qualification decision.
        """
        if is_disqualified:
            return {
                "total_score": 0,
                "tier": "DISQUALIFIED",
                "disqualified": True,
                "disqualification_reason": disqualification_reason,
                "breakdown": {
                    "engineering_headcount": 0,
                    "kubernetes_usage": 0,
                    "geography": 0,
                    "persona_match": 0
                },
                "matched_criteria": []
            }

        form = enriched_lead.get("form_input", {})
        enrichment = enriched_lead.get("enrichment_data", {})

        eng_count = enrichment.get("engineering_headcount", 0)
        tech_stack = enrichment.get("tech_stack", [])
        geo = enrichment.get("geography", "")
        job_title = form.get("job_title", "").lower()
        message = form.get("message", "").lower()

        score_eng = 0
        matched_criteria = []

        # 1. Engineering Headcount Score
        if eng_count >= 200:
            score_eng = self.weights["engineering_team_size"]["200+"]
            matched_criteria.append(f"Ideal engineering team size ({eng_count} engineers >= 200 target)")
        elif eng_count >= 100:
            score_eng = self.weights["engineering_team_size"]["100-199"]
            matched_criteria.append(f"Mid-large engineering team size ({eng_count} engineers)")
        elif eng_count >= 50:
            score_eng = self.weights["engineering_team_size"]["50-99"]
            matched_criteria.append(f"Growth engineering team size ({eng_count} engineers)")
        else:
            score_eng = 0

        # 2. Kubernetes Usage Score (Checked in tech stack or prospect message)
        score_k8s = 0
        has_k8s_tech = any("kubernetes" in tech.lower() or "k8s" in tech.lower() or "eks" in tech.lower() or "gke" in tech.lower() or "aks" in tech.lower() for tech in tech_stack)
        has_k8s_msg = "kubernetes" in message or "k8s" in message or "cluster" in message

        if has_k8s_tech or has_k8s_msg:
            score_k8s = self.weights["kubernetes_usage"]["verified_production"]
            matched_criteria.append("Verified Kubernetes workload in production")

        # 3. Geography Score
        score_geo = 0
        if any(allowed in geo for allowed in ["US", "EU", "North America", "Europe"]):
            score_geo = self.weights["geography"]["US"]
            matched_criteria.append(f"Primary target region ({geo})")

        # 4. Persona Match Score
        score_persona = 0
        high_value_titles = ["vp", "head of", "cto", "director", "platform", "infrastructure", "architect"]
        if any(t in job_title for t in high_value_titles):
            score_persona = self.weights["persona_match"]["VP Engineering / Head of Infrastructure / CTO / Director of Platform"]
            matched_criteria.append(f"Decision maker job title ({form.get('job_title')})")
        elif "devops" in job_title or "senior" in job_title or "lead" in job_title:
            score_persona = self.weights["persona_match"]["Senior DevOps / Staff Engineer"]
            matched_criteria.append(f"Technical influencer job title ({form.get('job_title')})")

        total_score = score_eng + score_k8s + score_geo + score_persona

        if total_score >= self.thresholds["qualified"]:
            tier = "QUALIFIED"
        elif total_score >= self.thresholds["nurture"]:
            tier = "NURTURE"
        else:
            tier = "UNQUALIFIED"

        return {
            "total_score": total_score,
            "tier": tier,
            "disqualified": False,
            "disqualification_reason": "",
            "breakdown": {
                "engineering_headcount": score_eng,
                "kubernetes_usage": score_k8s,
                "geography": score_geo,
                "persona_match": score_persona
            },
            "matched_criteria": matched_criteria
        }

if __name__ == "__main__":
    scorer = LeadScorer()
    sample = {
        "form_input": {"job_title": "VP of Infrastructure", "message": "Automating K8s"},
        "enrichment_data": {"engineering_headcount": 450, "tech_stack": ["Kubernetes"], "geography": "US"}
    }
    result = scorer.score_lead(sample)
    print(json.dumps(result, indent=2))
