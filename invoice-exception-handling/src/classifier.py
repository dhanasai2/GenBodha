"""
Invoice Exception Classifier.
Classifies exceptions into taxonomy categories and supports the first-class failure state:
'UNSURE_NEEDS_HUMAN_CHECK'.
"""

from typing import Dict, Any

class InvoiceExceptionClassifier:
    def classify(self, match_result: Dict[str, Any], dup_result: Dict[str, Any], extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classifies invoice exception type based on deterministic signals.
        """
        # 1. First-Class Failure / Abstention Check (Low PDF extraction confidence)
        if extraction_result.get("needs_manual_ocr_review", False):
            return {
                "classification_category": "UNSURE_NEEDS_HUMAN_CHECK",
                "confidence": extraction_result.get("extraction_confidence", 0.5),
                "is_abstention": True,
                "reason": "PDF extraction confidence fell below safety threshold (<70%). Unreadable characters in total amount or PO field.",
                "human_check_checklist": [
                    "Manually inspect raw invoice PDF scan",
                    "Verify total dollar amount against line items",
                    "Confirm PO number visibility"
                ]
            }

        # 2. Duplicate Payment Risk Check (High financial risk)
        if dup_result.get("is_duplicate_risk", False):
            return {
                "classification_category": "TRUE_DUPLICATE_RISK",
                "confidence": dup_result.get("duplicate_confidence", 0.95),
                "is_abstention": False,
                "reason": dup_result.get("explanation"),
                "human_check_checklist": [
                    "Verify whether previous payment was remitted",
                    "Check bank ledger for duplicate transaction ID",
                    "Contact vendor AP before releasing payment"
                ]
            }

        # 3. Subscription Trap Check
        if dup_result.get("duplicate_type") == "VALID_SUBSCRIPTION_RECURRING":
            return {
                "classification_category": "VALID_SUBSCRIPTION_RECURRING",
                "confidence": 0.95,
                "is_abstention": False,
                "reason": dup_result.get("explanation"),
                "human_check_checklist": []
            }

        # 4. Check Match Discrepancies
        discrepancies = match_result.get("discrepancies_detected", [])
        if match_result.get("is_perfect_match", False):
            return {
                "classification_category": "CLEARED_AUTO_MATCH",
                "confidence": 0.99,
                "is_abstention": False,
                "reason": "Invoice, Purchase Order, and Goods Receipt match perfectly.",
                "human_check_checklist": []
            }

        # Classify primary discrepancy cause
        deltas = match_result.get("calculated_deltas", {})
        if "MISSING_GOODS_RECEIPT" in discrepancies or not deltas.get("goods_receipt_posted", True):
            return {
                "classification_category": "MISSING_GOODS_RECEIPT",
                "confidence": 0.95,
                "is_abstention": False,
                "reason": "Goods Receipt (GR) has not been posted in ERP system yet.",
                "human_check_checklist": ["Ping warehouse manager to confirm physical delivery receipt"]
            }

        if deltas.get("quantity_delta", 0) != 0:
            return {
                "classification_category": "QUANTITY_MISMATCH",
                "confidence": 0.95,
                "is_abstention": False,
                "reason": f"Quantity billed ({deltas.get('quantity_billed')}) exceeds quantity received ({deltas.get('quantity_received')}).",
                "human_check_checklist": ["Check warehouse short-shipment log", "Request partial billing adjustment"]
            }

        if abs(deltas.get("unit_price_delta", 0)) > 0.01:
            return {
                "classification_category": "PRICE_DRIFT",
                "confidence": 0.95,
                "is_abstention": False,
                "reason": f"Invoice unit price (${deltas.get('invoice_unit_price'):.2f}) drifted by {deltas.get('unit_price_drift_pct'):+.1f}% from PO rate (${deltas.get('po_unit_price'):.2f}).",
                "human_check_checklist": ["Verify contract pricing tier", "Contact vendor for credit memo"]
            }

        if abs(deltas.get("tax_delta", 0)) > 0.05:
            return {
                "classification_category": "TAX_DISCREPANCY",
                "confidence": 0.90,
                "is_abstention": False,
                "reason": f"Tax billed (${deltas.get('billed_tax'):.2f}) differs from expected tax (${deltas.get('expected_tax'):.2f}).",
                "human_check_checklist": ["Verify local vs state tax rate application"]
            }

        # Default fallback to UNSURE if unclassified
        return {
            "classification_category": "UNSURE_NEEDS_HUMAN_CHECK",
            "confidence": 0.50,
            "is_abstention": True,
            "reason": "Complex multi-variable anomaly detected. Automated confidence below threshold.",
            "human_check_checklist": ["Conduct manual 3-way audit"]
        }
