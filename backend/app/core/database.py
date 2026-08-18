import json
import sqlite3
from datetime import datetime
from typing import Optional
from app.models.transaction import Transaction
from app.models.event import Event
from app.models.ledger import LedgerEntry

DB_FILE = "decentro_trace.db"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            reference_id TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'INR',
            transfer_type TEXT NOT NULL,
            beneficiary_id TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            transaction_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            source TEXT NOT NULL,
            status TEXT NOT NULL,
            occurred_at TEXT NOT NULL,
            received_at TEXT NOT NULL,
            correlation_id TEXT,
            sequence INTEGER NOT NULL DEFAULT 0,
            payload_json TEXT NOT NULL DEFAULT '{}',
            FOREIGN KEY (transaction_id) REFERENCES transactions(id)
        )
    """)
    
    # Ledger entries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ledger_entries (
            id TEXT PRIMARY KEY,
            transaction_id TEXT NOT NULL,
            entry_type TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'INR',
            occurred_at TEXT NOT NULL,
            reference_id TEXT NOT NULL,
            payload_json TEXT NOT NULL DEFAULT '{}',
            FOREIGN KEY (transaction_id) REFERENCES transactions(id)
        )
    """)
    
    conn.commit()
    conn.close()


def save_transaction(tx: Transaction):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO transactions (id, reference_id, amount, currency, transfer_type, beneficiary_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (tx.id, tx.reference_id, tx.amount, tx.currency, tx.transfer_type.value, tx.beneficiary_id, tx.created_at.isoformat())
    )
    conn.commit()
    conn.close()


def save_event(event: Event):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO events (id, transaction_id, event_type, source, status, occurred_at, received_at, correlation_id, sequence, payload_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event.id,
            event.transaction_id,
            event.event_type.value,
            event.source.value,
            event.status.value,
            event.occurred_at.isoformat(),
            event.received_at.isoformat(),
            event.correlation_id,
            event.sequence,
            json.dumps(event.payload)
        )
    )
    conn.commit()
    conn.close()


def save_ledger_entry(entry: LedgerEntry):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO ledger_entries (id, transaction_id, entry_type, amount, currency, occurred_at, reference_id, payload_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            entry.id,
            entry.transaction_id,
            entry.entry_type.value,
            entry.amount,
            entry.currency,
            entry.occurred_at.isoformat(),
            entry.reference_id,
            json.dumps(entry.payload)
        )
    )
    conn.commit()
    conn.close()


def get_transaction(tx_id: str) -> Optional[Transaction]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return Transaction(
        id=row["id"],
        reference_id=row["reference_id"],
        amount=row["amount"],
        currency=row["currency"],
        transfer_type=row["transfer_type"],
        beneficiary_id=row["beneficiary_id"],
        created_at=datetime.fromisoformat(row["created_at"])
    )


def list_transactions() -> list[Transaction]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [
        Transaction(
            id=r["id"],
            reference_id=r["reference_id"],
            amount=r["amount"],
            currency=r["currency"],
            transfer_type=r["transfer_type"],
            beneficiary_id=r["beneficiary_id"],
            created_at=datetime.fromisoformat(r["created_at"])
        )
        for r in rows
    ]


def get_events_for_transaction(tx_id: str) -> list[Event]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE transaction_id = ? ORDER BY rowid ASC", (tx_id,))
    rows = cursor.fetchall()
    conn.close()
    return [
        Event(
            id=r["id"],
            transaction_id=r["transaction_id"],
            event_type=r["event_type"],
            source=r["source"],
            status=r["status"],
            occurred_at=datetime.fromisoformat(r["occurred_at"]),
            received_at=datetime.fromisoformat(r["received_at"]),
            correlation_id=r["correlation_id"],
            sequence=r["sequence"],
            payload=json.loads(r["payload_json"])
        )
        for r in rows
    ]


def get_ledger_entries_for_transaction(tx_id: str) -> list[LedgerEntry]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ledger_entries WHERE transaction_id = ? ORDER BY occurred_at ASC", (tx_id,))
    rows = cursor.fetchall()
    conn.close()
    return [
        LedgerEntry(
            id=r["id"],
            transaction_id=r["transaction_id"],
            entry_type=r["entry_type"],
            amount=r["amount"],
            currency=r["currency"],
            occurred_at=datetime.fromisoformat(r["occurred_at"]),
            reference_id=r["reference_id"],
            payload=json.loads(r["payload_json"])
        )
        for r in rows
    ]
