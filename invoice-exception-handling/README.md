# 🥈 Project 2: Invoice Exception Handling — 3-Way Match

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Zero LLM Arithmetic](https://img.shields.io/badge/LLM_Arithmetic-Zero-brightgreen.svg)]()
[![Financial Loss Matrix](https://img.shields.io/badge/Financial_Loss-Cost_Matrix-red.svg)]()

> **GenBodha.ai Industry Use-Case Challenge Solution**
> Department of Information Technology, JNTU-GV College of Engineering

---

## 🎯 Executive Overview

AP teams at mid-to-large enterprises receive ~900 monthly invoice exceptions from ERP systems. A naive AI classifier trained to maximize F1 score makes the wrong trade-off: it treats a missed duplicate ($94,000 loss) as equally bad as an unnecessary human review escalation ($15 cost). **InvoiceGuard AI makes this trade-off visible** by calculating total dollar loss using an asymmetric financial cost matrix.

### Core Principles
1. **Zero LLM Arithmetic**: Quantity differences, price drifts, tax discrepancies, and totals are computed 100% in Python. A future language model could receive pre-calculated deltas for taxonomy classification and email drafting.
2. **Asymmetric Error Costs**: Results are evaluated using financial loss ($), not only F1. Missing a duplicate costs $94,000; escalating a clean invoice to humans costs $15.
3. **First-Class Abstention**: `UNSURE_NEEDS_HUMAN_CHECK` is a real, first-class output — used when PDF OCR confidence is below threshold or signals are genuinely ambiguous.
4. **Subscription Trap Protection**: Recurring monthly subscriptions (same vendor, same amount, 30-day cycle) are explicitly distinguished from true duplicate payments.

---

## 🏗️ Architecture: 6-Stage Deterministic Pipeline

```
 Invoice PDF / JSON
       │
       ▼
┌──────────────────────┐
│ 1. Invoice Field Extractor│  ← Structured payload parse + confidence score
│    (pdf_extractor.py) │
└──────────┬───────────┘
           │ extracted_fields + confidence
           ▼
┌──────────────────────┐
│ 2. 3-Way Matcher     │  ← 100% code arithmetic. Zero LLM math.
│    (matcher.py)       │    Computes qty_delta, price_drift_pct, tax_delta
└──────────┬───────────┘
           │ match_result (discrepancies + calculated_deltas)
           ▼
┌──────────────────────┐
│ 3. Duplicate Detector│  ← Fuzzy match on invoice#, supplier, amount
│    (dup_detector.py)  │    Subscription trap: same vendor, ~30-day gap
└──────────┬───────────┘
           │ dup_result
           ▼
┌──────────────────────┐
│ 4. Exception Classifier│ ← Rules-based taxonomy with UNSURE state
│    (classifier.py)    │
└──────────┬───────────┘
           │ classification_category + confidence
           ▼
┌──────────────────────┐
│ 5. Cost Reporter     │  ← Calculates loss on $, not F1
│    (cost_optimizer.py)│    Missed Duplicate: $94,000
│                       │    Unnecessary Escalation: $15
└──────────┬───────────┘
           │ cost_report
           ▼
┌──────────────────────┐
│ 6. Resolution Engine │  ← ERP status code + supplier email draft
│    (resolution_engine)│
└──────────────────────┘
```

---

## 📊 Exception Taxonomy

| Category | ERP Action | Typical Financial Risk |
|:---------|:-----------|:----------------------|
| `CLEARED_AUTO_MATCH` | AUTO_RELEASE_PAYMENT | None |
| `QUANTITY_MISMATCH` | PARTIAL_PAYMENT_SHORT_SHIPMENT | Invoice overcharge |
| `PRICE_DRIFT` | REQUEST_CREDIT_MEMO | PO rate violation |
| `TAX_DISCREPANCY` | ON_HOLD_TAX_REVIEW | Tax overpayment |
| `MISSING_GOODS_RECEIPT` | HOLD_PENDING_WAREHOUSE_GR | Payment before delivery |
| `TRUE_DUPLICATE_RISK` | **REJECT_INVOICE_DUPLICATE** | **$94,000 avg loss** |
| `VALID_SUBSCRIPTION_RECURRING` | AUTO_RELEASE_PAYMENT | None (valid) |
| `UNSURE_NEEDS_HUMAN_CHECK` | ESCALATE_TO_SENIOR_AP_ANALYST | $15 analyst cost |

---

## 🚀 Setup & Run

### 1. Generate Synthetic Dataset (900 Invoices)

The current extractor receives structured synthetic invoice payloads and simulates OCR confidence; it does not parse binary PDF files.
```bash
python data/generate_synthetic_data.py
```

### 2. Run Evaluation Benchmark
```bash
python eval/run_eval.py
```

### 3. Launch Interactive Dashboard
Open `app/index.html` directly in any modern browser. Features:
- **Exception Queue** with category filters and pagination
- **3-Way Match Inspector**: side-by-side Invoice vs PO vs GR comparison
- **Live Delta Analysis**: computed deltas displayed with color-coded alerts
- **Duplicate Risk Detection**: with subscription trap classification
- **Financial Cost Matrix Simulator**: live sliders to adjust error costs and recalculate total financial exposure

---

## 💰 Financial Cost Matrix: Why F1 Is Wrong

**Standard F1 Optimizer** treats all errors as equal:
- FP (unnecessary review) = 1 unit of "bad"
- FN (missed duplicate) = 1 unit of "bad"

**Reality**: Missed duplicate = **$94,000**. Unnecessary escalation = **$15**. A model that sends every invoice to human review ($15 × 900 = $13,500) is far cheaper than one that misses even one duplicate ($94,000).

The current cost report calculates:
```
Total Loss = (# missed duplicates × $94,000) + (# unnecessary escalations × $15) + (# wrong resolutions × $50)
```

---

## 🔬 PDF Extraction Accuracy Benchmark

| Metric | Result |
|:-------|:-------|
| Total Invoices Parsed | 900 |
| High-Confidence Extractions (≥70%) | 788 (87.56%) |
| Low-Confidence OCR Noise | 112 (12.44%) |
| Auto-routed to `UNSURE_NEEDS_HUMAN_CHECK` | 112 (100% of noisy PDFs) |
