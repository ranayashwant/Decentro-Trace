# Decentro Trace — System Architecture

## 1. Executive Summary

**Decentro Trace** is an AI-powered transaction debugger designed for asynchronous fintech payout lifecycles. It deterministically reconstructs transaction events across client API requests, gateway processing, banking partner switches, webhook callbacks, and ledger book entries.

## 2. Core Architectural Principle

> **"The system determines what happened. AI explains why it matters."**

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

## 3. Layer Separation of Truth

| Layer | Responsibility | Source of Truth | Can AI Override? |
|---|---|---|:---:|
| **Layer 1: Observed Facts** | Raw HTTP status, payloads, timestamps, error codes, ledger entries | Stored database records | **NO** |
| **Layer 2: Deterministic Engine** | Canonical ordering, deduplication, missing event detection, state conflict detection, financial balance calculation | Python domain logic | **NO** |
| **Layer 3: AI Interpretation** | Contextual summary, human explanation of bank codes, recommended engineering next actions, confidence score | LLM Provider (GPT/Mock) | N/A (Consumes L1 + L2 only) |

## 4. Deterministic Pipeline

1. **Load Entity**: Fetch Transaction, raw Events, and Ledger entries.
2. **Normalize**: Standardize datetimes, source enums, and extract raw error payloads.
3. **Deduplicate**: Identify exact duplicates (same source, status, occurred_at, and correlation ID). Expose duplicate count without dropping audit history.
4. **Order**: Deterministic sorting by `occurred_at ASC`, sequence tiebreaker, and event ID tiebreaker.
5. **Anomaly Detection**:
   - Out-of-order arrival check (`received_at` vs `occurred_at`).
   - Missing intermediate lifecycle steps (`PROVIDER_PROCESSING`, `PAYOUT_ACCEPTED`).
   - Conflicting terminal observations (e.g. Webhook failure vs direct status query success).
6. **Financial Reconciliation**:
   $$\text{Net Impact} = \text{Debited Amount} - \text{Reversed Amount}$$
   Reconciled is `True` if net impact is zero (for failed payout) or if debited matches expected amount (for successful payout).
7. **AI Context Assembly**: Inject only structured deterministic facts into the LLM system prompt.
