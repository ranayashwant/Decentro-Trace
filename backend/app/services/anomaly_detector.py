from app.models.event import Event
from app.models.enums import EventType, TransactionStatus
from app.models.trace import StateConflict


class AnomalyDetector:
    """
    Deterministically detects integrity anomalies: duplicates, out-of-order ingestion,
    missing expected lifecycle events, and conflicting status observations.
    """

    @staticmethod
    def detect_duplicates(events: list[Event]) -> tuple[list[Event], list[Event]]:
        """
        Separates canonical unique events from duplicate events.
        Does not silently drop duplicates — records them for integrity reporting.
        """
        seen_keys = set()
        canonical: list[Event] = []
        duplicates: list[Event] = []

        for evt in events:
            # Key based on event_type, status, source, occurred_at, and correlation_id
            dedup_key = (
                evt.event_type,
                evt.status,
                evt.source,
                evt.occurred_at.isoformat(),
                evt.correlation_id or evt.payload.get("bank_reference")
            )
            if dedup_key in seen_keys:
                duplicates.append(evt)
            else:
                seen_keys.add(dedup_key)
                canonical.append(evt)

        return canonical, duplicates

    @staticmethod
    def detect_out_of_order(raw_events: list[Event], canonical_ordered_events: list[Event]) -> bool:
        """
        Returns True if the order in which events were received at the gateway
        differs from their chronological/causal occurrence order.
        """
        if len(raw_events) <= 1:
            return False

        # Check if received_at timestamps are strictly monotonically non-decreasing
        # or if raw event IDs order differs from canonical sorted order
        for i in range(len(raw_events) - 1):
            if raw_events[i].received_at > raw_events[i + 1].received_at:
                return True

        # Check if arrival order of canonical items differs from occurred_at order
        raw_canonical_order = [e.id for e in raw_events if any(c.id == e.id for c in canonical_ordered_events)]
        ordered_ids = [e.id for e in canonical_ordered_events]

        return raw_canonical_order != ordered_ids

    @staticmethod
    def detect_missing_events(canonical_events: list[Event]) -> list[str]:
        """
        Checks for missing intermediate stages in the canonical payout lifecycle.
        Expected progression: INITIATED -> ACCEPTED -> PROVIDER_PROCESSING -> TERMINAL
        """
        present_types = {e.event_type for e in canonical_events}
        missing: list[str] = []

        # If transaction reached terminal callback or failure/success,
        # it should ideally have passed ACCEPTED and PROVIDER_PROCESSING
        has_terminal = any(e.status in (TransactionStatus.SUCCESS, TransactionStatus.FAILURE) for e in canonical_events)

        if has_terminal:
            if EventType.PAYOUT_ACCEPTED not in present_types and EventType.PAYOUT_INITIATED in present_types:
                missing.append("PAYOUT_ACCEPTED (Gateway Acceptance)")
            if EventType.PROVIDER_PROCESSING not in present_types:
                missing.append("PROVIDER_PROCESSING (Partner Switch Routing)")

        return missing

    @staticmethod
    def detect_state_conflicts(canonical_events: list[Event]) -> list[StateConflict]:
        """
        Detects if multiple sources report contradictory transaction statuses
        (e.g. Webhook reports FAILURE while Status Check reports SUCCESS).
        The system records the conflict without AI guessing a winner.
        """
        conflicts: list[StateConflict] = []
        terminal_events = [
            e for e in canonical_events
            if e.status in (TransactionStatus.SUCCESS, TransactionStatus.FAILURE)
        ]

        for i in range(len(terminal_events)):
            for j in range(i + 1, len(terminal_events)):
                e1 = terminal_events[i]
                e2 = terminal_events[j]
                if e1.status != e2.status:
                    conflicts.append(
                        StateConflict(
                            event_1_id=e1.id,
                            event_1_type=e1.event_type.value,
                            event_1_status=e1.status,
                            event_2_id=e2.id,
                            event_2_type=e2.event_type.value,
                            event_2_status=e2.status,
                            description=(
                                f"Contradictory terminal statuses observed: Event {e1.id} ({e1.source.value}) "
                                f"reported {e1.status.value}, whereas Event {e2.id} ({e2.source.value}) "
                                f"reported {e2.status.value}."
                            )
                        )
                    )

        return conflicts
