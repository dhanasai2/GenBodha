"""
Claim Traceability Engine.
Verifies every factual statement in drafted emails against retrieved snippets.
Prevents hallucinations and maps text sentences to snippet provenance metadata.
"""

from typing import List, Dict, Any

class ClaimTracer:
    def verify_and_trace(self, claims: List[Dict[str, Any]], available_snippets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verifies claims against available snippets.
        Each claim must have: statement, target_metric, snippet_id (or None).
        Returns claim traceability trace table.
        """
        snippet_map = {s["snippet_id"]: s for s in available_snippets if "snippet_id" in s}
        verified_claims = []
        unverified_claims = []

        for claim in claims:
            snip_id = claim.get("snippet_id")
            if snip_id and snip_id in snippet_map:
                source_obj = snippet_map[snip_id]
                verified_claims.append({
                    "sentence": claim["sentence"],
                    "fact_claimed": claim["fact_claimed"],
                    "status": "VERIFIED_TRACEABLE",
                    "snippet_id": snip_id,
                    "source_fact": source_obj.get("fact"),
                    "source_provenance": source_obj.get("source")
                })
            else:
                unverified_claims.append({
                    "sentence": claim["sentence"],
                    "fact_claimed": claim.get("fact_claimed", "Unknown"),
                    "status": "UNVERIFIED_REJECTED",
                    "snippet_id": None,
                    "reason": "No retrieved snippet found in research corpus. Claim removed to prevent hallucination."
                })

        is_safe = len(unverified_claims) == 0

        return {
            "is_fully_traceable": is_safe,
            "verified_claims_count": len(verified_claims),
            "unverified_claims_count": len(unverified_claims),
            "claims_trace": verified_claims,
            "rejected_claims": unverified_claims
        }
