# Decentro Trace 🔍⚡

> **AI-Powered Transaction Debugger for Fintech Payout Workflows**  
> *"The system determines what happened. AI explains why it matters."*

---

## 1. Problem Statement

In modern fintech platforms (like Decentro), asynchronous payout lifecycles span multiple disconnected systems:
1. **Client API Requests** (`/initiate_payout`)
2. **Gateway Queuing & Idempotency** (`PENDING`)
3. **Banking Partner & Switch Routing** (`NPCI`, `IMPS / NEFT / RTGS / UPI`)
4. **Asynchronous Webhook Callbacks** (Which may arrive out of order or duplicate)
5. **Ledger Book Entries** (Debits, holds, and auto-reversals)

When a payout fails or experiences latency, engineers often have to manually correlate logs across multiple microservices, inspect cryptic banking switch error codes, and audit balance sheets. 

**Decentro Trace** solves this by turning a single **Transaction ID** into a deterministic, canonical timeline with automatic integrity checks, money reconciliation, and an AI-driven root cause explanation.

---

## 2. Architecture & The Source-of-Truth Hierarchy

```text
┌─────────────────────────────────────────────────────────────┐
│                      Next.js Frontend                       │
│  (Timeline, Event Inspector, Integrity & AI Investigation)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                       │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │               Layer 1: Observed Facts                 │  │
│  │   (API requests, raw callbacks, bank error codes,     │  │
│  │    ledger debits, reversal entries)                   │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │                              │
│  ┌───────────────────────────▼───────────────────────────┐  │
│  │           Layer 2: Deterministic Conclusions          │  │
│  │   - Temporal Sorting (occurred_at ASC)                │  │
│  │   - Deduplication (group exact callback duplicates)   │  │
│  │   - Lifecycle Transitions & Failure Stage Mapping     │  │
│  │   - Anomaly Detection (out-of-order, missing, conflict)│ │
│  │   - Financial Reconciliation (Debits vs Reversals)    │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              │                              │
│  ┌───────────────────────────▼───────────────────────────┐  │
│  │               Layer 3: AI Inference Layer             │  │
│  │   - Isolated behind AIProvider adapter                │  │
│  │   - Strict Pydantic JSON schema output                │  │
│  │   - Evidence linking to specific event IDs            │  │
│  │   - Operational next action & retry safety advice     │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                      ┌────────┴────────┐
                      ▼                 ▼
               ┌──────────────┐  ┌─────────────┐
               │ SQLite Store │  │ LLM Adapter │
               └──────────────┘  └─────────────┘
```

### Deterministic vs AI Boundary

| Layer | Responsibility | Source of Truth | Can AI Override? |
|---|---|---|:---:|
| **Layer 1: Observed Facts** | Raw HTTP status, payloads, timestamps, error codes, ledger entries | Stored database records | **NO** |
| **Layer 2: Deterministic Engine** | Canonical ordering, deduplication, missing event detection, state conflict detection, financial balance calculation | Python domain logic | **NO** |
| **Layer 3: AI Interpretation** | Contextual summary, human explanation of bank codes, recommended engineering next actions, confidence score | LLM Provider (GPT/Mock) | N/A (Consumes L1 + L2 only) |

---

## 3. Demo Scenarios & Test Datasets

### Primary Demo: `dec_987654321` (IMPS ₹25,000 Payout Failure + Reversal)
- **Lifecycle**: `INITIATED` $\rightarrow$ `PENDING` $\rightarrow$ `PROVIDER_PROCESSING` $\rightarrow$ `FAILURE` $\rightarrow$ `REVERSED`
- **Observed Provider Code**: `E1042: BENEFICIARY_BANK_UNAVAILABLE` (NPCI 91)
- **Reconciliation**: Debited ₹25,000, Reversed ₹25,000, **Net Impact: ₹0 (RECONCILED: YES)**
- **AI Diagnosis**: Pinpoints destination bank switch outage, links evidence to `evt_proc_003` & `evt_fail_004`, confirms client funds are safe, and advises retrying once destination bank recovers.

### Secondary Demo: `dec_out_of_order_01` (NEFT ₹10,000 Out-of-Order Webhook)
- Demonstrates distributed network resilience: Webhooks arrived out of order and with an exact duplicate callback.
- Trace engine correctly deduplicates the duplicate and reconstructs causal order by `occurred_at`.

### Success Flow: `dec_123456789` (RTGS ₹75,000 Clean Settlement)
- Clean end-to-end lifecycle with zero anomalies.

### State Conflict Scenario: `dec_conflict_999` (UPI ₹5,000 State Conflict)
- Demonstrates anomaly detection when partner callback reports `FAILURE` while NPCI direct query reports `SUCCESS`.

---

## 4. Local Setup & Running

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm

### 1. Backend Setup
```bash
cd backend
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server (auto-seeds synthetic data on boot)
uvicorn app.main:app --reload --port 8000
```
Backend Swagger API Docs: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

### 3. Running Automated Tests
```bash
# Run pytest unit and API test suite (16 tests)
pytest backend/tests/ -v
```

---

## 5. 90-Second Loom Demo Runbook

1. **0:00 - 0:15 (The Problem)**:  
   *"When an asynchronous fintech payout fails, engineers have to manually reconstruct what happened across API requests, webhooks, and ledger books."*
2. **0:15 - 0:35 (Deterministic Reconstruction)**:  
   Select `dec_987654321`. Point out the ordered timeline (`INITIATED` $\rightarrow$ `ACCEPTED` $\rightarrow$ `PROCESSING` $\rightarrow$ `FAILURE` $\rightarrow$ `REVERSAL`).
3. **0:35 - 0:50 (Inspecting Evidence)**:  
   Click `Payload` on the failure event to reveal the raw JSON payload with error code `E1042 (BENEFICIARY_BANK_UNAVAILABLE)`.
4. **0:50 - 1:10 (Integrity & Money Reconciliation)**:  
   Show the **Trace Integrity** card (5 canonical events, 0 duplicates) and **Money Reconciliation** (Debit: ₹25k, Reversal: ₹25k, Net Impact: ₹0, Reconciled: YES).
5. **1:10 - 1:30 (AI Investigation)**:  
   Click **"Run AI Investigation"**. Highlight the root cause explanation, clickable evidence badges, and safe operational recommendation.
