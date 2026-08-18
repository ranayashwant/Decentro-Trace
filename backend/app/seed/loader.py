import os
import json
import glob
from pathlib import Path
from typing import Optional
from app.models.transaction import Transaction
from app.models.event import Event
from app.models.ledger import LedgerEntry
from app.services.event_normalizer import EventNormalizer
from app.core.database import init_db, save_transaction, save_event, save_ledger_entry


def load_seed_files(seed_dir: Optional[str] = None):
    """
    Loads all synthetic seed transaction JSON files into the SQLite database.
    """
    init_db()

    if not seed_dir:
        # Default to ../../seed or ./seed relative to backend
        possible_dirs = [
            Path(__file__).parent.parent.parent / "seed",
            Path("seed"),
            Path("../seed")
        ]
        for p in possible_dirs:
            if p.exists():
                seed_dir = str(p.resolve())
                break

    if not seed_dir or not os.path.exists(seed_dir):
        print(f"Warning: Seed directory '{seed_dir}' not found.")
        return

    json_files = glob.glob(os.path.join(seed_dir, "*.json"))
    print(f"Loading seed data from {len(json_files)} files in {seed_dir}...")

    for file_path in json_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 1. Transaction
            raw_tx = data["transaction"]
            tx = Transaction(
                id=raw_tx["id"],
                reference_id=raw_tx["reference_id"],
                amount=float(raw_tx["amount"]),
                currency=raw_tx.get("currency", "INR"),
                transfer_type=raw_tx.get("transfer_type", "IMPS"),
                beneficiary_id=raw_tx["beneficiary_id"],
                created_at=EventNormalizer.normalize_timestamp(raw_tx["created_at"])
            )
            save_transaction(tx)

            # 2. Events
            for raw_evt in data.get("events", []):
                evt = EventNormalizer.normalize_event(raw_evt)
                save_event(evt)

            # 3. Ledger Entries
            for raw_led in data.get("ledger_entries", []):
                led = LedgerEntry(
                    id=raw_led["id"],
                    transaction_id=raw_led["transaction_id"],
                    entry_type=raw_led["entry_type"],
                    amount=float(raw_led["amount"]),
                    currency=raw_led.get("currency", "INR"),
                    occurred_at=EventNormalizer.normalize_timestamp(raw_led["occurred_at"]),
                    reference_id=raw_led["reference_id"],
                    payload=raw_led.get("payload", {})
                )
                save_ledger_entry(led)

            print(f" Successfully seeded transaction: {tx.id} ({tx.reference_id})")
        except Exception as e:
            print(f" Error loading seed file {file_path}: {e}")


if __name__ == "__main__":
    load_seed_files()
