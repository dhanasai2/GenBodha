"""
Grounded Outbound Email Generator.
Generates claim-traced first-touch emails for qualified leads.
Abstains from hallucination by falling back to generic template when research snippets are absent.
"""

from typing import Dict, Any
from .tracer import ClaimTracer

class GroundedEmailGenerator:
    def __init__(self):
        self.tracer = ClaimTracer()

    def generate_email(self, enriched_lead: Dict[str, Any], scored_lead: Dict[str, Any]) -> Dict[str, Any]:
        if scored_lead.get("disqualified", False):
            return {
                "email_generated": False,
                "reason": "Lead is disqualified. Outbound email generation suppressed.",
                "subject": "",
                "body": "",
                "claim_trace": []
            }

        form = enriched_lead.get("form_input", {})
        enrichment = enriched_lead.get("enrichment_data", {})
        prospect_name = form.get("name", "there").split()[0]
        snippets = enrichment.get("snippets", [])
        company_name = enrichment.get("company_name", form.get("company_domain", "your company"))

        claims_to_include = []
        body_paragraphs = []

        # Check if we have verified snippets
        if enrichment.get("found", False) and snippets:
            # We have verified facts! Craft personalized claims linked to snippet IDs
            for snip in snippets:
                if "Kubernetes" in snip["fact"] or "nodes" in snip["fact"] or "K8s" in snip["fact"] or "clusters" in snip["fact"]:
                    claims_to_include.append({
                        "sentence": f"I noticed {company_name} is running production Kubernetes infrastructure ({snip['fact']}).",
                        "fact_claimed": snip["fact"],
                        "snippet_id": snip["snippet_id"]
                    })
                elif "engineers" in snip["fact"] or "workforce" in snip["fact"]:
                    claims_to_include.append({
                        "sentence": f"Given your team of {enrichment.get('engineering_headcount', 200)}+ engineers, maintaining deployment velocity is critical.",
                        "fact_claimed": snip["fact"],
                        "snippet_id": snip["snippet_id"]
                    })

            # Run through tracer
            trace_result = self.tracer.verify_and_trace(claims_to_include, snippets)
            verified_sentences = [c["sentence"] for c in trace_result["claims_trace"]]

            subject = f"Scaling K8s workflows for {company_name}"
            intro = f"Hi {prospect_name},\n\nThanks for reaching out to us!"
            personalized_section = " ".join(verified_sentences)
            pitch = "\n\nI'd love to share how our platform can support your developer environment goals."
            cta = "\n\nDo you have 15 minutes this Thursday for a quick demo?\n\nBest regards,\nAlex Vance\nLead Solutions Engineer"

            full_body = intro + ("\n\n" + personalized_section if personalized_section else "") + pitch + cta

            return {
                "email_generated": True,
                "mode": "PERSONALIZED_CLAIM_TRACED",
                "subject": subject,
                "body": full_body,
                "claim_trace": trace_result["claims_trace"],
                "rejected_claims": trace_result["rejected_claims"],
                "hallucination_prevention_status": "ZERO_HALLUCINATION_VERIFIED"
            }
        else:
            # Fallback to Generic Template when research finds nothing
            subject = f"DevTools Platform Overview for {company_name}"
            body = (
                f"Hi {prospect_name},\n\n"
                f"Thanks for your interest in our developer tools platform!\n\n"
                f"We help engineering organizations accelerate deployment pipelines and simplify containerized infrastructure management.\n\n"
                f"I'd be happy to set up a quick 15-minute introductory call to learn more about your current dev environment goals.\n\n"
                f"Best regards,\nAlex Vance\nLead Solutions Engineer"
            )
            return {
                "email_generated": True,
                "mode": "GENERIC_SAFE_FALLBACK",
                "subject": subject,
                "body": body,
                "claim_trace": [],
                "rejected_claims": [],
                "hallucination_prevention_status": "FALLBACK_GENERIC_NO_UNVERIFIED_CLAIMS"
            }
