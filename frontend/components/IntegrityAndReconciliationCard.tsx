'use client';

import React from 'react';
import { TraceIntegrity, ReconciliationResult } from '../lib/types';
import { ShieldCheck, AlertTriangle, Scale, CheckCircle2, XCircle, ArrowRightLeft, DollarSign, Layers } from 'lucide-react';

interface Props {
  integrity: TraceIntegrity;
  reconciliation: ReconciliationResult;
}

export default function IntegrityAndReconciliationCard({
  integrity,
  reconciliation,
}: Props) {
  const formatCurrency = (amt: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2,
    }).format(amt);
  };

  return (
    <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
      {/* 1. TRACE INTEGRITY */}
      <div className="rounded-2xl border border-slate-800 bg-[#0F172A]/80 p-5 shadow-xl backdrop-blur-md">
        <div className="mb-4 flex items-center justify-between border-b border-slate-800/80 pb-3">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="h-4 w-4 text-[#0080F6]" />
            <h3 className="text-sm font-semibold text-white">Trace Integrity</h3>
          </div>
          {integrity.is_clean ? (
            <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-950/40 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-400">
              <CheckCircle2 className="h-3 w-3" />
              Trace Clean
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 rounded-full border border-amber-500/30 bg-amber-950/40 px-2.5 py-0.5 text-[11px] font-semibold text-amber-400">
              <AlertTriangle className="h-3 w-3" />
              Anomalies Observed
            </span>
          )}
        </div>

        <div className="space-y-2.5 text-xs">
          <div className="flex items-center justify-between rounded-lg bg-slate-900/50 px-3 py-2">
            <span className="text-slate-400">Total Events Received:</span>
            <span className="font-mono font-bold text-white">{integrity.total_events_received}</span>
          </div>

          <div className="flex items-center justify-between rounded-lg bg-slate-900/50 px-3 py-2">
            <span className="text-slate-400">Canonical Unique Events:</span>
            <span className="font-mono font-bold text-slate-200">{integrity.canonical_events_count}</span>
          </div>

          <div className="flex items-center justify-between rounded-lg bg-slate-900/50 px-3 py-2">
            <span className="text-slate-400">Duplicate Webhooks Detected:</span>
            <span
              className={`font-mono font-bold ${
                integrity.duplicate_events_count > 0 ? 'text-amber-400' : 'text-slate-400'
              }`}
            >
              {integrity.duplicate_events_count}
            </span>
          </div>

          <div className="flex items-center justify-between rounded-lg bg-slate-900/50 px-3 py-2">
            <span className="text-slate-400">Out-of-Order Ingestion:</span>
            <span
              className={`font-mono font-bold ${
                integrity.out_of_order_received ? 'text-amber-400' : 'text-emerald-400'
              }`}
            >
              {integrity.out_of_order_received ? 'YES (Handled)' : 'NO'}
            </span>
          </div>

          <div className="flex items-center justify-between rounded-lg bg-slate-900/50 px-3 py-2">
            <span className="text-slate-400">Missing Expected Stages:</span>
            <span
              className={`font-mono font-bold ${
                integrity.missing_expected_events.length > 0 ? 'text-amber-400' : 'text-slate-400'
              }`}
            >
              {integrity.missing_expected_events.length}
            </span>
          </div>

          {integrity.missing_expected_events.length > 0 && (
            <div className="mt-2 rounded-lg border border-amber-900/40 bg-amber-950/20 p-2 text-amber-300">
              <span className="font-semibold">Missing Stages:</span>
              <ul className="mt-1 list-disc pl-4 text-[11px]">
                {integrity.missing_expected_events.map((m, i) => (
                  <li key={i}>{m}</li>
                ))}
              </ul>
            </div>
          )}

          {integrity.state_conflicts.length > 0 && (
            <div className="mt-2 rounded-lg border border-red-900/40 bg-red-950/20 p-2 text-red-300">
              <span className="font-semibold">Conflicting Observations Flagged:</span>
              {integrity.state_conflicts.map((c, i) => (
                <p key={i} className="mt-1 text-[11px] font-mono">
                  {c.description}
                </p>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 2. MONEY RECONCILIATION */}
      <div className="rounded-2xl border border-slate-800 bg-[#0F172A]/80 p-5 shadow-xl backdrop-blur-md">
        <div className="mb-4 flex items-center justify-between border-b border-slate-800/80 pb-3">
          <div className="flex items-center space-x-2">
            <Scale className="h-4 w-4 text-[#0080F6]" />
            <h3 className="text-sm font-semibold text-white">Money Reconciliation</h3>
          </div>
          {reconciliation.reconciled ? (
            <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-950/40 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-400">
              <CheckCircle2 className="h-3 w-3" />
              RECONCILED: YES
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 rounded-full border border-red-500/30 bg-red-950/40 px-2.5 py-0.5 text-[11px] font-semibold text-red-400">
              <XCircle className="h-3 w-3" />
              UNRECONCILED
            </span>
          )}
        </div>

        <div className="grid grid-cols-2 gap-3 text-xs sm:grid-cols-3">
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-3">
            <span className="text-[10px] uppercase text-slate-500">Debited</span>
            <p className="mt-1 text-sm font-bold text-white">{formatCurrency(reconciliation.debited_amount)}</p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-3">
            <span className="text-[10px] uppercase text-slate-500">Reversed</span>
            <p className="mt-1 text-sm font-bold text-blue-400">{formatCurrency(reconciliation.reversed_amount)}</p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-3 col-span-2 sm:col-span-1">
            <span className="text-[10px] uppercase text-slate-500">Net Financial Impact</span>
            <p
              className={`mt-1 text-sm font-bold ${
                reconciliation.net_impact === 0 ? 'text-emerald-400' : 'text-red-400'
              }`}
            >
              {formatCurrency(reconciliation.net_impact)}
            </p>
          </div>
        </div>

        {/* Ledger Equation breakdown */}
        <div className="mt-4 rounded-xl border border-slate-800/80 bg-slate-950/60 p-3 text-xs">
          <div className="flex items-center justify-between text-slate-400">
            <span>Reconciliation Logic:</span>
            <span className="font-mono text-[11px] text-slate-300">Net = Debit - Reversal</span>
          </div>
          <p className="mt-2 text-[11px] text-slate-400">
            {reconciliation.reconciled ? (
              <span className="text-emerald-400">
                ✓ Funds are fully balanced. Client account debits match corresponding ledger reversal entries.
              </span>
            ) : (
              <span className="text-red-400">
                ✕ Financial mismatch detected! Net impact is non-zero. Manual ledger adjustment required.
              </span>
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
