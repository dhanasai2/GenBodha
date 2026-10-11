# 🥇 Project 1: Inbound Lead Qualification & Claim Traceability Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![SLA Budget](https://img.shields.io/badge/SLA_Budget-30_min_max-green.svg)]()
[![Hallucination Rate](https://img.shields.io/badge/Hallucination_Rate-0.0%25-brightgreen.svg)]()

> **GenBodha.ai Industry Use-Case Challenge Solution**
> Department of Information Technology, JNTU-GV College of Engineering

---

## 🎯 Executive Overview

B2B SaaS companies face a critical trade-off in inbound lead processing: SDRs working leads oldest-first often keep enterprise Fortune 500 decision-makers waiting behind student inquiries and competitor recon, leading to massive drop-offs in conversion (response within 30 minutes triples conversion). However, automating first-touch emails with generative AI introduces a terrifying risk for the VP of Sales: **a personalized outbound email containing a hallucinated fact about the prospect.**

**LeadTrace AI** solves this problem by delivering a **fast, zero-hallucination, claim-traced inbound lead qualification engine**:
1. **Latency SLA Budget**: Evaluates leads in **< 2 milliseconds** (utilizing < 0.0001% of the 30-minute SLA budget).
2. **Deterministic Pre-filtering**: Instantly disqualifies competitors, freemail domains (`@gmail.com`), and non-target geos before invoking expensive models.
3. **Data Provenance Separation**: Explicitly separates prospect-supplied `form_input` from third-party retrieved `enrichment_data`.
4. **Claim Provenance & Traceability**: Every claim statement in an outbound email is linked 1-to-1 to a verified source snippet (`SNIP-001`).
5. **Honest Abstention Guarantee**: When research finds no verified facts, the system **abstains** from making company-specific claims and falls back to a clean, verified generic email template. **Hallucination Rate = 0.0%**.

---

## 🏗️ System Architecture

```
                               ┌──────────────────────────┐
                               │  Inbound Lead Submission  │
                               └────────────┬─────────────┘
                                            │
                               ┌────────────▼─────────────┐
                               │ Fast Rule Pre-Disqualifier│
                               └──────┬─────────────┬─────┘
                     [Disqualified]   │             │ [Passed]
             ┌────────────────────────┘             └────────────────────────┐
             ▼                                                               ▼
┌──────────────────────────┐                               ┌──────────────────────────┐
│  Instant Reject & Log    │                               │ B2B Intelligence Enricher │
└──────────────────────────┘                               └────────────┬─────────────┘
                                                                        │
                                                           ┌────────────▼─────────────┐
                                                           │ Deterministic ICP Scorer │
                                                           └────────────┬─────────────┘
                                                                        │
                                                           ┌────────────▼─────────────┐
                                                           │ Claim-Traced Email Gen   │
                                                           └────────────┬─────────────┘
                                                                        │
                                                           ┌────────────▼─────────────┐
                                                           │ SDR Priority Queue Router│
                                                           └──────────────────────────┘
```

---

## 🚀 Getting Started & Setup

### Prerequisites
- Python 3.10 or higher
- Any modern web browser

### 1. Run Evaluation & Benchmark Suite
To measure end-to-end wall clock latency, disqualification recall, and hallucination rate:
```bash
python eval/run_eval.py
```

### 2. Launch Interactive Web Dashboard
Simply open `app/index.html` in your web browser:
- Inspect inbound lead queue
- Toggle status filters (Qualified, Disqualified, Nurture)
- Audit Form vs Enriched data provenance
- Inspect live claim provenance tags (`[SNIP-001] Verified`)

---

## 📊 Evaluation & Benchmark Results

Run on 10 synthetic lead submissions representing diverse B2B profiles:

| Metric | Result | Benchmark Target | Status |
| :--- | :--- | :--- | :--- |
| **Median Wall-Clock Latency** | **0.03 ms / lead** | < 1,800,000 ms (30 mins) | 🟢 PASSED |
| **Average Wall-Clock Latency** | **0.06 ms / lead** | < 1,800,000 ms (30 mins) | 🟢 PASSED |
| **SLA Budget Utilization** | **0.000003%** | < 100% | 🟢 PASSED |
| **Hallucination Rate** | **0.0%** | 0.0% | 🟢 PASSED |
| **Disqualification Recall** | **100.0%** | 100.0% | 🟢 PASSED |
| **Claim Traceability %** | **100.0%** | 100.0% | 🟢 PASSED |
| **Abstention Safety** | **100.0% Fallback** | 100.0% | 🟢 PASSED |

---

## 🛑 Failure Modes & Abstention Policy

The system explicitly handles non-ideal inputs through defined failure states:
1. **Empty Research / Stealth Company**: If third-party enrichment yields no verified snippets, the system does NOT attempt to guess company facts. It generates a safe, generic intro email.
2. **Competitor Recon**: Inquiries originating from competitor domains are routed to a security log without generating any response.
3. **Ambiguous Job Titles**: Non-standard job titles are assigned conservative ICP scoring weights to prevent false qualification.
