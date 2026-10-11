"""
Resolution Proposer & Supplier Email Drafter.
Generates proposed ERP actions and drafts supplier emails based on exception category.
"""

from typing import Dict, Any

class ResolutionEngine:
    def generate_resolution(self, invoice: Dict[str, Any], classification: Dict[str, Any], match_deltas: Dict[str, Any]) -> Dict[str, Any]:
        cat = classification.get("classification_category")
        supplier_name = invoice.get("supplier_name", "Supplier")
        inv_num = invoice.get("invoice_number", "INV-000")

        if cat == "TRUE_DUPLICATE_RISK":
            proposed_action = "REJECT_INVOICE_DUPLICATE"
            erp_status = "CANCELLED_DUPLICATE_FLAG"
            email_draft = (
                f"Dear AP Team at {supplier_name},\n\n"
                f"We received invoice #{inv_num} for ${invoice.get('total_amount'):.2f}. "
                f"Our automated Accounts Payable audit detected that this invoice is a duplicate of a previously processed payment. "
                f"Please review your records. This duplicate invoice submission has been cancelled in our system.\n\n"
                f"Regards,\nAccounts Payable Operations"
            )
        elif cat == "PRICE_DRIFT":
            proposed_action = "REQUEST_CREDIT_MEMO"
            erp_status = "ON_HOLD_PRICE_DISCREPANCY"
            email_draft = (
                f"Dear {supplier_name} Billing Department,\n\n"
                f"We are processing invoice #{inv_num}. The unit price billed (${match_deltas.get('invoice_unit_price'):.2f}) "
                f"exceeds our agreed Purchase Order rate (${match_deltas.get('po_unit_price'):.2f}) by {match_deltas.get('unit_price_drift_pct'):+.1f}%.\n\n"
                f"Please issue a Credit Memo for the difference or re-issue the invoice at the agreed PO price so we may release payment.\n\n"
                f"Regards,\nAccounts Payable Team"
            )
        elif cat == "QUANTITY_MISMATCH":
            proposed_action = "PARTIAL_PAYMENT_SHORT_SHIPMENT"
            erp_status = "PARTIAL_PAYMENT_APPROVED"
            email_draft = (
                f"Dear {supplier_name} Billing Team,\n\n"
                f"Regarding invoice #{inv_num}: Our receiving dock logged a receipt of {match_deltas.get('quantity_received')} units, "
                f"whereas the invoice bills for {match_deltas.get('quantity_billed')} units.\n\n"
                f"We are processing payment for the received quantity of {match_deltas.get('quantity_received')} units. "
                f"Please verify shipment records for the balance.\n\n"
                f"Regards,\nAccounts Payable Team"
            )
        elif cat == "MISSING_GOODS_RECEIPT":
            proposed_action = "HOLD_PENDING_WAREHOUSE_GR"
            erp_status = "PENDING_GR_POSTING"
            email_draft = (
                f"Internal Note: Invoice #{inv_num} held pending receiving dock posting of Goods Receipt. Vendor notification deferred."
            )
        elif cat == "TAX_DISCREPANCY":
            proposed_action = "ON_HOLD_TAX_REVIEW"
            erp_status = "ON_HOLD_TAX_DISCREPANCY"
            email_draft = (
                f"Dear {supplier_name},\n\n"
                f"Invoice #{inv_num} contains a tax discrepancy. The billed tax is ${match_deltas.get('billed_tax'):.2f}, "
                f"while the expected tax is ${match_deltas.get('expected_tax'):.2f}. Please submit a corrected invoice.\n\n"
                f"Regards,\nAccounts Payable Team"
            )
        elif cat == "UNSURE_NEEDS_HUMAN_CHECK":
            proposed_action = "ESCALATE_TO_SENIOR_AP_ANALYST"
            erp_status = "MANUAL_AUDIT_QUEUE"
            email_draft = (
                f"Internal Audit Note: Invoice #{inv_num} routed to Senior AP Analyst queue due to {classification.get('reason')}."
            )
        else:
            proposed_action = "AUTO_RELEASE_PAYMENT"
            erp_status = "APPROVED_FOR_PAYMENT"
            email_draft = ""

        return {
            "proposed_action": proposed_action,
            "erp_status": erp_status,
            "supplier_email_draft": email_draft,
            "checklist": classification.get("human_check_checklist", [])
        }
