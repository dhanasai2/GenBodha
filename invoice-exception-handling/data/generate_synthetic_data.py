"""
Synthetic Dataset Generator for Invoice Exception Handling (3-Way Match).
Generates 900 invoice exceptions with ground-truth defect labels:
1. QUANTITY_MISMATCH
2. PRICE_DRIFT
3. MISSING_GOODS_RECEIPT
4. TAX_DISCREPANCY
5. TRUE_DUPLICATE
6. SUBSCRIPTION_TRAP (Looks like duplicate but is valid recurring subscription)
7. EXTRACTION_NOISE_UNSURE (Low confidence PDF extraction)
8. PERFECT_MATCH (Auto-cleared control)
"""

import json
import random
from datetime import date as calendar_date, timedelta
from pathlib import Path

SUPPLIERS = [
  {"id": "SUP-101", "name": "Acme Hardware Components Inc"},
  {"id": "SUP-102", "name": "Global Semiconductor Corp"},
  {"id": "SUP-103", "name": "Precision Fasteners Ltd"},
  {"id": "SUP-104", "name": "Vortex Electronics Corp"},
  {"id": "SUP-105", "name": "CloudHosting Infrastructure LLC"} # Subscription vendor
]

DEFECT_TYPES = [
    "QUANTITY_MISMATCH",
    "PRICE_DRIFT",
    "MISSING_GOODS_RECEIPT",
    "TAX_DISCREPANCY",
    "TRUE_DUPLICATE",
    "SUBSCRIPTION_TRAP",
    "EXTRACTION_NOISE_UNSURE",
    "PERFECT_MATCH"
]

def generate_dataset(num_records=900):
    random.seed(20260929)
    pos = {}
    grs = {}
    invoices = []
    subscription_count = 0

    # 1. Base POs and GRs
    for i in range(1, 401):
        po_id = f"PO-2026-{i:04d}"
        supplier = random.choice(SUPPLIERS)
        unit_price = round(random.uniform(25.0, 500.0), 2)
        qty = random.randint(10, 500)
        total_amount = round(unit_price * qty, 2)

        pos[po_id] = {
            "po_id": po_id,
            "supplier_id": supplier["id"],
            "supplier_name": supplier["name"],
            "unit_price": unit_price,
            "quantity": qty,
            "total_amount": total_amount,
            "tax_rate": 0.08,
            "created_date": "2026-08-15"
        }

        # 70% of GRs match PO exactly
        gr_qty = qty if random.random() > 0.3 else random.randint(qty - 50, qty + 50)
        grs[po_id] = {
            "gr_id": f"GR-2026-{i:04d}",
            "po_id": po_id,
            "quantity_received": max(0, gr_qty),
            "received_date": "2026-08-20",
            "posted": True
        }

    # 2. Invoices with ground truth defects
    for i in range(1, num_records + 1):
        po_id = f"PO-2026-{((i - 1) % 400) + 1:04d}"
        po = pos[po_id]
        gr = grs[po_id]

        inv_num = f"INV-990{i:04d}"
        defect = DEFECT_TYPES[i % len(DEFECT_TYPES)]

        inv_qty = po["quantity"]
        inv_price = po["unit_price"]
        inv_tax = round(po["total_amount"] * 0.08, 2)
        gr_posted = True
        extraction_confidence = 0.98
        supplier_name = po["supplier_name"]
        date = f"2026-09-{(i % 28) + 1:02d}"

        # Inject ground truth defect
        if defect == "QUANTITY_MISMATCH":
            inv_qty = po["quantity"] + 20
        elif defect == "PRICE_DRIFT":
            inv_price = round(po["unit_price"] * 1.12, 2)
        elif defect == "MISSING_GOODS_RECEIPT":
            gr_posted = False
        elif defect == "TAX_DISCREPANCY":
            inv_tax = round(po["total_amount"] * 0.15, 2) # Wrong 15% tax
        elif defect == "TRUE_DUPLICATE":
            # Exact duplicate of previous invoice
            reference_index = len(invoices) - 1
            inv_num = invoices[reference_index]["invoice_number"]
        elif defect == "SUBSCRIPTION_TRAP":
            # CloudHosting subscription - same vendor, same amount, different month
            subscription_count += 1
            supplier_name = "CloudHosting Infrastructure LLC"
            inv_price = 4999.00
            inv_qty = 1
            inv_tax = round(inv_price * 0.08, 2)
            date = (calendar_date(2026, 8, 1) + timedelta(days=30 * (subscription_count - 1))).isoformat()
        elif defect == "EXTRACTION_NOISE_UNSURE":
            extraction_confidence = random.uniform(0.40, 0.65) # Low PDF OCR confidence

        inv_total = round((inv_qty * inv_price) + inv_tax, 2)

        invoices.append({
            "invoice_id": f"INV-OBJ-{i:04d}",
            "invoice_number": inv_num,
            "po_id": po_id,
            "supplier_name": supplier_name,
            "invoice_date": date,
            "unit_price": inv_price,
            "quantity_billed": inv_qty,
            "tax_amount": inv_tax,
            "total_amount": inv_total,
            "gr_posted": gr_posted,
            "extraction_confidence": round(extraction_confidence, 2),
            "ground_truth_defect": defect
        })

    data_dir = Path(__file__).parent
    with open(data_dir / "purchase_orders.json", "w", encoding="utf-8") as f:
        json.dump(pos, f, indent=2)

    with open(data_dir / "goods_receipts.json", "w", encoding="utf-8") as f:
        json.dump(grs, f, indent=2)

    with open(data_dir / "invoices.json", "w", encoding="utf-8") as f:
        json.dump(invoices, f, indent=2)

    print(f"[OK] Generated synthetic dataset: {len(invoices)} invoices, {len(pos)} POs, {len(grs)} GRs.")

if __name__ == "__main__":
    generate_dataset()
