from datetime import datetime
from app.services.event_normalizer import EventNormalizer
from app.models.enums import EventType, EventSource, TransactionStatus


def test_normalize_event_standardizes_fields():
    raw = {
        "id": "evt_raw_1",
        "transaction_id": "dec_test",
        "event_type": "payout_initiated",
        "source": "api_client",
        "status": "initiated",
        "occurred_at": "2026-08-18T10:00:00.000Z",
        "received_at": "2026-08-18T10:00:00.050Z",
        "sequence": 1,
        "payload": {"amount": 5000}
    }
    event = EventNormalizer.normalize_event(raw)
    assert event.event_type == EventType.PAYOUT_INITIATED
    assert event.source == EventSource.API_CLIENT
    assert event.status == TransactionStatus.INITIATED
    assert isinstance(event.occurred_at, datetime)
    assert event.payload["amount"] == 5000


def test_extract_error_details():
    raw = {
        "id": "evt_err_1",
        "transaction_id": "dec_test",
        "event_type": "PAYOUT_STATUS_CALLBACK",
        "source": "BANK_PARTNER_CALLBACK",
        "status": "FAILURE",
        "occurred_at": "2026-08-18T10:00:00Z",
        "sequence": 2,
        "payload": {
            "provider_error_code": "E1042",
            "provider_error_message": "BENEFICIARY_BANK_UNAVAILABLE"
        }
    }
    event = EventNormalizer.normalize_event(raw)
    code, msg = EventNormalizer.extract_error_details(event)
    assert code == "E1042"
    assert msg == "BENEFICIARY_BANK_UNAVAILABLE"
