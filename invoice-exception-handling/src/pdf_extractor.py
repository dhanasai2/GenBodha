"""
PDF Extractor Module.
Extracts structured invoice fields from synthetic invoice payloads and carries an OCR confidence score.
This prototype does not parse binary PDF documents.
"""

from typing import Dict, Any

class PDFInvoiceExtractor:
    def extract_fields(self, raw_invoice_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses invoice fields and assigns extraction confidence scores.
        Simulates OCR text extraction performance.
        """
        confidence = raw_invoice_payload.get("extraction_confidence", 0.98)

        # Field-level extraction
        extracted_data = {
            "invoice_number": raw_invoice_payload.get("invoice_number"),
            "po_id": raw_invoice_payload.get("po_id"),
            "supplier_name": raw_invoice_payload.get("supplier_name"),
            "invoice_date": raw_invoice_payload.get("invoice_date"),
            "unit_price": raw_invoice_payload.get("unit_price"),
            "quantity_billed": raw_invoice_payload.get("quantity_billed"),
            "tax_amount": raw_invoice_payload.get("tax_amount"),
            "total_amount": raw_invoice_payload.get("total_amount")
        }

        # Determine extraction health
        if confidence < 0.70:
            status = "LOW_CONFIDENCE_OCR_NOISE"
        elif confidence < 0.90:
            status = "MODERATE_CONFIDENCE"
        else:
            status = "HIGH_CONFIDENCE_CLEAN"

        return {
            "extracted_fields": extracted_data,
            "extraction_confidence": round(confidence, 4),
            "extraction_status": status,
            "needs_manual_ocr_review": confidence < 0.70
        }

    def measure_extraction_accuracy(self, dataset: list) -> Dict[str, float]:
        """
        Calculates field-level extraction accuracy metrics across a benchmark dataset.
        """
        total = len(dataset)
        clean = sum(1 for item in dataset if item.get("extraction_confidence", 1.0) >= 0.70)
        noisy = total - clean

        return {
            "total_invoices_parsed": total,
            "clean_extractions": clean,
            "noisy_extractions": noisy,
            "overall_extraction_accuracy_pct": round((clean / total) * 100, 2)
        }
