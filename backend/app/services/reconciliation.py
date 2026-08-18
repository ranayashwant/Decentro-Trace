from app.models.ledger import LedgerEntry
from app.models.enums import LedgerEntryType, TransactionStatus
from app.models.trace import ReconciliationResult


class ReconciliationEngine:
    """
    Computes deterministic financial reconciliation from ledger entries.
    Money movement is separate from transaction status.
    """

    @staticmethod
    def calculate(
        entries: list[LedgerEntry],
        final_status: TransactionStatus,
        expected_amount: float
    ) -> ReconciliationResult:
        debited = 0.0
        reversed_amt = 0.0
        credited = 0.0

        for entry in entries:
            if entry.entry_type == LedgerEntryType.DEBIT:
                debited += entry.amount
            elif entry.entry_type == LedgerEntryType.REVERSAL:
                reversed_amt += entry.amount
            elif entry.entry_type == LedgerEntryType.CREDIT:
                credited += entry.amount

        # Net impact on client balance
        # Positive net impact means client has funds debited that haven't reached beneficiary or been reversed
        # For a failed payout with full reversal: debited (25k) - reversed (25k) = net 0 (reconciled)
        # For a successful payout: debited (25k) = expected (25k), reversed = 0 (reconciled)
        net_impact = round(debited - reversed_amt, 2)

        if final_status in (TransactionStatus.FAILURE, TransactionStatus.REVERSED):
            # Failed transaction must be fully reversed to be reconciled
            reconciled = (debited > 0 and debited == reversed_amt and net_impact == 0.0) or (debited == 0.0)
        elif final_status == TransactionStatus.SUCCESS:
            # Successful transaction must have debited the expected amount with 0 reversal
            reconciled = (debited == round(expected_amount, 2) and reversed_amt == 0.0)
        else:
            # Pending / in-flight transactions are balanced if debit matches expected amount or is in progress
            reconciled = (debited <= expected_amount)

        return ReconciliationResult(
            debited_amount=round(debited, 2),
            reversed_amount=round(reversed_amt, 2),
            credited_amount=round(credited, 2),
            net_impact=net_impact,
            currency="INR",
            reconciled=reconciled,
            entries_count=len(entries)
        )
