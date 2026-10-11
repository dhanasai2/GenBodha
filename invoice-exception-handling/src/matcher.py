"""
Code-Based 3-Way Matcher Engine.
Computes 100% of arithmetic differences deterministically in Python code.
Ensures zero LLM calculation errors.
"""

from typing import Dict, Any

class DeterministicThreeWayMatcher:
    def match(self, invoice_fields: Dict[str, Any], po: Dict[str, Any], gr: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes exact 3-Way Match comparison between Invoice, Purchase Order, and Goods Receipt.
        """
        inv_qty = invoice_fields.get("quantity_billed", 0)
        inv_price = invoice_fields.get("unit_price", 0.0)
        inv_tax = invoice_fields.get("tax_amount", 0.0)
        inv_total = invoice_fields.get("total_amount", 0.0)

        po_price = po.get("unit_price", 0.0)
        po_qty = po.get("quantity", 0)
        po_tax_rate = po.get("tax_rate", 0.08)

        gr_qty = gr.get("quantity_received", 0) if gr else 0
        gr_posted = gr.get("posted", False) if gr else False

        # Compute exact deltas in code
        qty_diff = inv_qty - gr_qty
        price_diff = round(inv_price - po_price, 2)
        price_drift_pct = round((price_diff / po_price) * 100, 2) if po_price > 0 else 0.0

        expected_tax = round((inv_qty * inv_price) * po_tax_rate, 2)
        tax_diff = round(inv_tax - expected_tax, 2)

        expected_total = round((inv_qty * inv_price) + expected_tax, 2)
        total_diff = round(inv_total - expected_total, 2)

        # Flag individual discrepancy signals
        discrepancies = []
        if not gr_posted:
            discrepancies.append("MISSING_GOODS_RECEIPT")
        if qty_diff != 0:
            discrepancies.append(f"QUANTITY_MISMATCH (Billed {inv_qty} vs Received {gr_qty})")
        if abs(price_diff) > 0.01:
            discrepancies.append(f"PRICE_DRIFT (Invoice ${inv_price:.2f} vs PO ${po_price:.2f}, Drift: {price_drift_pct:+.1f}%)")
        if abs(tax_diff) > 0.05:
            discrepancies.append(f"TAX_DISCREPANCY (Billed ${inv_tax:.2f} vs Expected ${expected_tax:.2f})")

        is_perfect_match = len(discrepancies) == 0 and gr_posted

        return {
            "is_perfect_match": is_perfect_match,
            "discrepancies_detected": discrepancies,
            "calculated_deltas": {
                "quantity_billed": inv_qty,
                "quantity_received": gr_qty,
                "quantity_delta": qty_diff,
                "invoice_unit_price": inv_price,
                "po_unit_price": po_price,
                "unit_price_delta": price_diff,
                "unit_price_drift_pct": price_drift_pct,
                "billed_tax": inv_tax,
                "expected_tax": expected_tax,
                "tax_delta": tax_diff,
                "goods_receipt_posted": gr_posted
            }
        }
