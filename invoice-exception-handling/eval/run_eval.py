"""
Invoice Exception Handling — 3-Way Match Evaluation Suite.
Compares financial cost reporting with standard classification metrics.
Tests: Noisy PDF accuracy, subscription trap, duplicate detection, and total dollar loss.
"""

import sys
import json
import time
from pathlib import Path

src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

from src.pdf_extractor import PDFInvoiceExtractor
from src.matcher import DeterministicThreeWayMatcher
from src.duplicate_detector import DuplicateDetector
from src.classifier import InvoiceExceptionClassifier
from src.cost_optimizer import FinancialCostOptimizer
from src.resolution_engine import ResolutionEngine


def run_evaluation():
    print("=" * 66)
    print(" [GOLD] INVOICE EXCEPTION HANDLING 3-WAY MATCH BENCHMARK SUITE")
    print("=" * 66)

    # Load datasets
    data_dir = src_dir / "data"
    with open(data_dir / "invoices.json", encoding="utf-8") as f:
        invoices = json.load(f)
    with open(data_dir / "purchase_orders.json", encoding="utf-8") as f:
        pos = json.load(f)
    with open(data_dir / "goods_receipts.json", encoding="utf-8") as f:
        grs = json.load(f)

    extractor = PDFInvoiceExtractor()
    matcher = DeterministicThreeWayMatcher()
    dup_detector = DuplicateDetector()
    classifier = InvoiceExceptionClassifier()
    resolver = ResolutionEngine()
    cost_opt = FinancialCostOptimizer()

    predictions = []
    category_counts = {}
    abstentions = 0
    start_time = time.time()

    # Processing all invoices
    for idx, invoice in enumerate(invoices):
        # Step 1: PDF Extraction
        extraction = extractor.extract_fields(invoice)
        fields = extraction["extracted_fields"]

        # Step 2: Lookup PO and GR
        po_id = invoice.get("po_id")
        po = pos.get(po_id, {})
        gr = grs.get(po_id, {})

        # Step 3: Deterministic 3-Way Match
        match_result = matcher.match(fields, po, gr)

        # Step 4: Duplicate Detection (check against previous 50 invoices)
        historical_window = invoices[max(0, idx - 50):idx]
        dup_result = dup_detector.check_duplicate_risk(invoice, historical_window)

        # Step 5: Classify Exception
        classification = classifier.classify(match_result, dup_result, extraction)

        # Step 6: Generate Resolution
        resolution = resolver.generate_resolution(invoice, classification, match_result.get("calculated_deltas", {}))

        if classification.get("is_abstention"):
            abstentions += 1

        cat = classification["classification_category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

        predictions.append({
            "invoice_id": invoice["invoice_id"],
            "ground_truth_defect": invoice["ground_truth_defect"],
            "classification_category": cat,
            "proposed_action": resolution["proposed_action"],
            "erp_status": resolution["erp_status"]
        })

    total_time = time.time() - start_time

    # Compute Financial Cost Matrix
    cost_report = cost_opt.calculate_total_financial_loss(predictions)

    # Compute simple accuracy (for baseline comparison)
    correct = sum(1 for p in predictions if _defect_matches_category(p["ground_truth_defect"], p["classification_category"]))
    accuracy_pct = round(correct / len(predictions) * 100, 2)

    # Compute F1 for duplicates (most critical class)
    true_dups = [p for p in predictions if p["ground_truth_defect"] == "TRUE_DUPLICATE"]
    tp = sum(1 for p in true_dups if p["classification_category"] == "TRUE_DUPLICATE_RISK")
    fp = sum(1 for p in predictions if p["ground_truth_defect"] != "TRUE_DUPLICATE" and p["classification_category"] == "TRUE_DUPLICATE_RISK")
    fn = sum(1 for p in true_dups if p["classification_category"] != "TRUE_DUPLICATE_RISK")
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    # PDF Extraction accuracy
    extraction_report = extractor.measure_extraction_accuracy(invoices)

    print(f"\nProcessed {len(invoices)} invoice exceptions in {total_time:.3f}s")
    print(f"  Avg latency: {(total_time / len(invoices)) * 1000:.2f}ms per invoice\n")

    print("-" * 66)
    print(" CLASSIFICATION DISTRIBUTION")
    print("-" * 66)
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        pct = count / len(invoices) * 100
        print(f"  {cat:<40} : {count:4d} ({pct:5.1f}%)")

    print("-" * 66)
    print(" FINANCIAL COST MATRIX ANALYSIS")
    print("-" * 66)
    bd = cost_report["cost_breakdown"]
    print(f"  Missed Duplicates (@ $94,000 each) : {bd['missed_duplicates_count']:3d}  => ${bd['missed_duplicates_loss_dollars']:>12,.2f}")
    print(f"  Unnecessary Escalations (@ $15)    : {bd['unnecessary_escalations_count']:3d}  => ${bd['unnecessary_escalation_loss_dollars']:>12,.2f}")
    print(f"  Wrong Resolutions (@ $50)          : {bd['wrong_resolutions_count']:3d}  => ${bd['wrong_resolution_loss_dollars']:>12,.2f}")
    print(f"  Correct Auto-Actions               : {bd['correct_auto_actions_count']:3d}")
    print(f"  {'TOTAL FINANCIAL LOSS':<38} => ${cost_report['total_financial_loss_dollars']:>12,.2f}")

    print("-" * 66)
    print(" DUPLICATE DETECTION METRICS (Most Critical Class)")
    print("-" * 66)
    print(f"  Precision  : {precision:.4f}")
    print(f"  Recall     : {recall:.4f}")
    print(f"  F1 Score   : {f1:.4f}")

    print("-" * 66)
    print(" ABSTENTION & SAFETY")
    print("-" * 66)
    print(f"  UNSURE_NEEDS_HUMAN_CHECK routed : {abstentions}")
    print(f"  Simple Classification Accuracy  : {accuracy_pct}%")

    print("-" * 66)
    print(" PDF EXTRACTION ACCURACY BENCHMARK")
    print("-" * 66)
    print(f"  Clean Extractions (>=70%): {extraction_report['clean_extractions']}")
    print(f"  Noisy OCR Extractions    : {extraction_report['noisy_extractions']}")
    print(f"  Overall Extraction Acc.  : {extraction_report['overall_extraction_accuracy_pct']}%")
    print("=" * 66)

    # Save detailed results
    results = {
        "total_invoices": len(invoices),
        "total_time_seconds": round(total_time, 4),
        "avg_latency_ms_per_invoice": round((total_time / len(invoices)) * 1000, 4),
        "accuracy_pct": accuracy_pct,
        "duplicate_precision": round(precision, 4),
        "duplicate_recall": round(recall, 4),
        "duplicate_f1": round(f1, 4),
        "abstentions_count": abstentions,
        "cost_report": cost_report,
        "extraction_accuracy": extraction_report,
        "category_distribution": category_counts
    }

    out_file = src_dir / "eval" / "benchmark_results.json"
    out_file.parent.mkdir(exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return results


def _defect_matches_category(ground_truth: str, predicted: str) -> bool:
    mapping = {
        "PERFECT_MATCH": "CLEARED_AUTO_MATCH",
        "TRUE_DUPLICATE": "TRUE_DUPLICATE_RISK",
        "QUANTITY_MISMATCH": "QUANTITY_MISMATCH",
        "PRICE_DRIFT": "PRICE_DRIFT",
        "TAX_DISCREPANCY": "TAX_DISCREPANCY",
        "MISSING_GOODS_RECEIPT": "MISSING_GOODS_RECEIPT",
        "SUBSCRIPTION_TRAP": "VALID_SUBSCRIPTION_RECURRING",
        "EXTRACTION_NOISE_UNSURE": "UNSURE_NEEDS_HUMAN_CHECK"
    }
    return mapping.get(ground_truth) == predicted


if __name__ == "__main__":
    run_evaluation()
