from typing import Any
from app.services.ai.base import AIProvider
from app.schemas.investigation import InvestigationResult, EvidenceItem, ConfidenceLevel


class MockAIProvider(AIProvider):
    """
    Deterministic Mock AI Provider for testing and rock-solid offline demos.
    Generates structured, evidence-backed explanations without making external API calls.
    """

    async def investigate(self, trace_context: dict[str, Any]) -> InvestigationResult:
        tx = trace_context.get("transaction", {})
        tx_id = tx.get("id", "unknown")
        failure = trace_context.get("failure_analysis", {})
        reconciliation = trace_context.get("reconciliation", {})
        integrity = trace_context.get("integrity", {})
        canonical_events = trace_context.get("canonical_events", [])

        # Scenario 1: Primary failure demo (dec_987654321)
        if tx_id == "dec_987654321":
            return InvestigationResult(
                summary="The ₹25,000 IMPS payout was accepted by Decentro and routed to the bank partner switch, but encountered a terminal failure at the beneficiary bank switch due to beneficiary bank unavailability.",
                failure_stage="BENEFICIARY_BANK",
                root_cause="Beneficiary bank system was unreachable during settlement (NPCI response 91 / Provider error E1042: BENEFICIARY_BANK_UNAVAILABLE).",
                evidence=[
                    EvidenceItem(
                        event_id="evt_proc_003",
                        reason="Confirms transfer was dispatched to NPCI_IMPS_FAST switch at 10:31:08 UTC."
                    ),
                    EvidenceItem(
                        event_id="evt_fail_004",
                        reason="Terminal callback received at 10:31:14 UTC with error code E1042 (BENEFICIARY_BANK_UNAVAILABLE)."
                    ),
                    EvidenceItem(
                        event_id="evt_rev_005",
                        reason="Automatic ledger reversal restored ₹25,000 to client balance at 10:31:15 UTC."
                    )
                ],
                recommended_action="Notify beneficiary of destination bank downtime. Safe to retry payout once destination bank switch health stabilizes, as client funds are fully reversed.",
                confidence=ConfidenceLevel.HIGH,
                uncertainty=None
            )

        # Scenario 2: Out of order demo (dec_out_of_order_01)
        if tx_id == "dec_out_of_order_01":
            return InvestigationResult(
                summary="The ₹10,000 NEFT payout failed due to invalid beneficiary account details. Ingestion logs show duplicate and out-of-order callback delivery, which was resolved by temporal trace reconstruction.",
                failure_stage="BENEFICIARY_SWITCH",
                root_cause="Beneficiary account validation failed at switch routing with error code E3001 (INVALID_BENEFICIARY_DETAILS).",
                evidence=[
                    EvidenceItem(
                        event_id="evt_ooo_004_early_arrival",
                        reason="Callback indicated failure reason INVALID_BENEFICIARY_DETAILS."
                    ),
                    EvidenceItem(
                        event_id="evt_ooo_005",
                        reason="Full reversal entry restoring ₹10,000 confirmed."
                    )
                ],
                recommended_action="Do not retry with current account details. Prompt customer to verify IFSC and account number before re-initiating.",
                confidence=ConfidenceLevel.HIGH,
                uncertainty="Events arrived out-of-order over network, but causal timeline was reconstructed from occurred_at timestamps."
            )

        # Scenario 3: State Conflict (dec_conflict_999)
        if tx_id == "dec_conflict_999" or len(integrity.get("state_conflicts", [])) > 0:
            return InvestigationResult(
                summary="The UPI payout encountered conflicting status signals: a webhook reported FAILURE (U30 timeout), while a subsequent NPCI direct query returned SUCCESS.",
                failure_stage="PROVIDER_ROUTING",
                root_cause="Asynchronous callback timed out at payee PSP switch, but beneficiary bank subsequently credited payee account before status poll.",
                evidence=[
                    EvidenceItem(
                        event_id="evt_conf_003_callback_failure",
                        reason="Callback reported payee PSP timeout."
                    ),
                    EvidenceItem(
                        event_id="evt_conf_004_poll_success",
                        reason="NPCI status lookup confirmed successful credit."
                    )
                ],
                recommended_action="Do NOT trigger automatic reversal or retry. Request manual UTR bank confirmation before adjusting ledger.",
                confidence=ConfidenceLevel.MEDIUM,
                uncertainty="Conflicting signals between partner callback and direct switch lookup. Direct lookup is authoritative but requires bank statement cross-check."
            )

        # Scenario 4: Success transaction (dec_123456789)
        if not failure.get("failed", False):
            return InvestigationResult(
                summary=f"The {tx.get('currency', 'INR')} {tx.get('amount', 0):,.2f} {tx.get('transfer_type', 'transfer')} payout completed smoothly with full terminal settlement.",
                failure_stage=None,
                root_cause="Transaction processed and settled successfully with beneficiary partner without anomalies.",
                evidence=[
                    EvidenceItem(
                        event_id=canonical_events[-1].get("id", "evt_end") if canonical_events else "evt_success",
                        reason="Terminal confirmation received from partner switch."
                    )
                ],
                recommended_action="No engineering action required. Transaction is closed and reconciled.",
                confidence=ConfidenceLevel.HIGH,
                uncertainty=None
            )

        # Generic fallback based on deterministic trace
        return InvestigationResult(
            summary=f"Transaction {tx_id} finished with status {trace_context.get('lifecycle', {}).get('final_status', 'UNKNOWN')}.",
            failure_stage=failure.get("failure_stage", "UNKNOWN"),
            root_cause=failure.get("observed_error_message") or "Provider reported failure during settlement processing.",
            evidence=[
                EvidenceItem(
                    event_id=failure.get("failure_event_id") or (canonical_events[0].get("id") if canonical_events else "evt_001"),
                    reason="Event contains terminal failure payload."
                )
            ],
            recommended_action="Inspect provider response codes and verify ledger reversal state before retrying.",
            confidence=ConfidenceLevel.MEDIUM,
            uncertainty=None
        )
