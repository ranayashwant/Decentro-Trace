from datetime import datetime
from typing import Any, Optional
from app.models.event import Event
from app.models.enums import EventType, EventSource, TransactionStatus


class EventNormalizer:
    """
    Normalizes raw events into standardized domain events with parsed timestamps,
    consistent status strings, and extracted error payloads.
    """

    @staticmethod
    def normalize_timestamp(ts: Any) -> datetime:
        if isinstance(ts, datetime):
            return ts
        if isinstance(ts, str):
            # Handle ISO string with trailing Z or timezone offsets
            cleaned_ts = ts.replace("Z", "+00:00")
            return datetime.fromisoformat(cleaned_ts)
        raise ValueError(f"Unsupported timestamp format: {ts}")

    @classmethod
    def normalize_event(cls, raw_event: dict[str, Any]) -> Event:
        # Event type normalization
        event_type_str = raw_event.get("event_type", "").upper().strip()
        event_type = EventType(event_type_str)

        # Source normalization
        source_str = raw_event.get("source", "UNKNOWN").upper().strip()
        source = EventSource(source_str) if source_str in EventSource.__members__ else EventSource.API_CLIENT

        # Status normalization
        status_str = raw_event.get("status", "PENDING").upper().strip()
        status = TransactionStatus(status_str) if status_str in TransactionStatus.__members__ else TransactionStatus.PENDING

        occurred_at = cls.normalize_timestamp(raw_event["occurred_at"])
        received_at = cls.normalize_timestamp(raw_event.get("received_at", raw_event["occurred_at"]))

        return Event(
            id=raw_event["id"],
            transaction_id=raw_event["transaction_id"],
            event_type=event_type,
            source=source,
            status=status,
            occurred_at=occurred_at,
            received_at=received_at,
            correlation_id=raw_event.get("correlation_id"),
            sequence=int(raw_event.get("sequence", 0)),
            payload=raw_event.get("payload", {})
        )

    @classmethod
    def extract_error_details(cls, event: Event) -> tuple[Optional[str], Optional[str]]:
        """
        Extracts observed provider error code and message from event payload.
        This provides deterministic facts, not AI interpretations.
        """
        payload = event.payload
        code = (
            payload.get("provider_error_code")
            or payload.get("response_code")
            or payload.get("npci_response_code")
            or payload.get("error_code")
        )
        msg = (
            payload.get("provider_error_message")
            or payload.get("message")
            or payload.get("error_message")
            or payload.get("response_message")
        )
        return code, msg
