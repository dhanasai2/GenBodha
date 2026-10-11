"""
Fuzzy Duplicate Detector & Subscription Trap Filter.
Detects duplicate payment risk using fuzzy matching on invoice #, supplier name, amount, and date window.
Prevents false-positive flags on valid monthly subscriptions.
"""

import re
from typing import Dict, Any, List
from datetime import datetime


def _normalize_inv_num(inv_num: str) -> str:
    """Strip trailing/leading whitespace and normalize to lowercase alphanumeric only."""
    return re.sub(r"[^a-z0-9]", "", inv_num.strip().lower())


class DuplicateDetector:
    def __init__(self):
        self.subscription_vendors = [
            "cloudhosting infrastructure llc",
            "aws cloud services",
            "microsoft azure saas",
            "datadog monitoring",
            "slack technologies"
        ]

    def check_duplicate_risk(self, target_invoice: Dict[str, Any], historical_invoices: List[Dict[str, Any]]) -> Dict[str, Any]:
        target_raw_num = target_invoice.get("invoice_number", "")
        target_num_norm = _normalize_inv_num(target_raw_num)
        target_supplier = target_invoice.get("supplier_name", "").strip().lower()
        target_amount = target_invoice.get("total_amount", 0.0)
        target_date_str = target_invoice.get("invoice_date", "2026-09-01")
        target_po = target_invoice.get("po_id", "")

        for prev in historical_invoices:
            if prev.get("invoice_id") == target_invoice.get("invoice_id"):
                continue

            prev_raw_num = prev.get("invoice_number", "")
            prev_num_norm = _normalize_inv_num(prev_raw_num)
            prev_supplier = prev.get("supplier_name", "").strip().lower()
            prev_amount = prev.get("total_amount", 0.0)
            prev_date_str = prev.get("invoice_date", "2026-09-01")
            prev_po = prev.get("po_id", "")

            # 1. Exact normalized invoice number match (catches INV-001 == INV 001 == inv001)
            if target_num_norm and target_num_norm == prev_num_norm and target_num_norm != "":
                return {
                    "is_duplicate_risk": True,
                    "duplicate_type": "EXACT_INVOICE_NUMBER_MATCH",
                    "duplicate_confidence": 1.0,
                    "matched_invoice_id": prev.get("invoice_id"),
                    "explanation": (
                        f"Exact duplicate invoice number '{target_raw_num}' previously submitted "
                        f"(Invoice ID: {prev.get('invoice_id')}) on {prev_date_str} for ${prev_amount:.2f}."
                    )
                }

            # 2. Same PO + same supplier + same amount (likely re-submission)
            if (target_po and target_po == prev_po
                    and (target_supplier in prev_supplier or prev_supplier in target_supplier)
                    and abs(target_amount - prev_amount) < 0.50):
                # 2a. Subscription trap check first
                if any(sub in target_supplier for sub in self.subscription_vendors):
                    try:
                        d1 = datetime.strptime(target_date_str, "%Y-%m-%d")
                        d2 = datetime.strptime(prev_date_str, "%Y-%m-%d")
                        days_diff = abs((d1 - d2).days)
                        if 25 <= days_diff <= 35:
                            return {
                                "is_duplicate_risk": False,
                                "duplicate_type": "VALID_SUBSCRIPTION_RECURRING",
                                "duplicate_confidence": 0.05,
                                "matched_invoice_id": prev.get("invoice_id"),
                                "explanation": (
                                    f"Subscription billing detected for {target_invoice.get('supplier_name')} "
                                    f"(${target_amount:.2f}). Monthly recurring ({days_diff}-day gap)."
                                )
                            }
                        continue
                    except ValueError:
                        pass

                return {
                    "is_duplicate_risk": True,
                    "duplicate_type": "SAME_PO_SUPPLIER_AMOUNT_RESUBMISSION",
                    "duplicate_confidence": 0.92,
                    "matched_invoice_id": prev.get("invoice_id"),
                    "explanation": (
                        f"Possible re-submission: Same PO ({target_po}), same supplier "
                        f"'{target_invoice.get('supplier_name')}', same amount ${target_amount:.2f} "
                        f"previously billed on {prev_date_str}."
                    )
                }

            # 3. Fuzzy: same supplier + same amount (no PO match required)
            if (target_supplier in prev_supplier or prev_supplier in target_supplier) and abs(target_amount - prev_amount) < 0.01:
                if any(sub in target_supplier for sub in self.subscription_vendors):
                    try:
                        d1 = datetime.strptime(target_date_str, "%Y-%m-%d")
                        d2 = datetime.strptime(prev_date_str, "%Y-%m-%d")
                        days_diff = abs((d1 - d2).days)
                        if 25 <= days_diff <= 35:
                            return {
                                "is_duplicate_risk": False,
                                "duplicate_type": "VALID_SUBSCRIPTION_RECURRING",
                                "duplicate_confidence": 0.05,
                                "matched_invoice_id": prev.get("invoice_id"),
                                "explanation": (
                                    f"Subscription match detected for {target_invoice.get('supplier_name')} "
                                    f"(${target_amount:.2f}). Recurring monthly billing ({days_diff} days gap)."
                                )
                            }
                        continue
                    except ValueError:
                        pass

                return {
                    "is_duplicate_risk": True,
                    "duplicate_type": "FUZZY_SUPPLIER_AMOUNT_MATCH",
                    "duplicate_confidence": 0.88,
                    "matched_invoice_id": prev.get("invoice_id"),
                    "explanation": (
                        f"Potential duplicate: Same supplier '{target_invoice.get('supplier_name')}' "
                        f"and exact amount ${target_amount:.2f} billed on {prev_date_str}."
                    )
                }

        return {
            "is_duplicate_risk": False,
            "duplicate_type": "NO_DUPLICATE_FOUND",
            "duplicate_confidence": 0.0,
            "matched_invoice_id": None,
            "explanation": "No duplicate pattern detected in historical payment records."
        }
