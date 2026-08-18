'use client';

import React from 'react';
import { Transaction, TransactionStatus } from '../lib/types';
import { IndianRupee, ArrowUpRight, Clock, CheckCircle2, XCircle, RefreshCw, Hash, UserCheck } from 'lucide-react';

interface Props {
  transaction: Transaction;
  finalStatus: TransactionStatus;
  durationMs?: number | null;
}

export default function TransactionSummaryCard({
  transaction,
  finalStatus,
  durationMs,
}: Props) {
  const formatCurrency = (amt: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2,
    }).format(amt);
  };

  const getStatusBadge = (status: TransactionStatus) => {
    switch (status) {
      case 'SUCCESS':
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-950/40 px-3 py-1 text-xs font-semibold text-emerald-400">
            <CheckCircle2 className="h-3.5 w-3.5" />
            SUCCESS
          </span>
        );
      case 'FAILURE':
      case 'REVERSED':
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full border border-red-500/30 bg-red-950/40 px-3 py-1 text-xs font-semibold text-red-400">
            <XCircle className="h-3.5 w-3.5" />
            {status}
          </span>
        );
      case 'PROCESSING':
      case 'PENDING':
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-500/30 bg-amber-950/40 px-3 py-1 text-xs font-semibold text-amber-400">
            <RefreshCw className="h-3.5 w-3.5 animate-spin" />
            {status}
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full border border-slate-700 bg-slate-800 px-3 py-1 text-xs font-semibold text-slate-300">
            <Clock className="h-3.5 w-3.5" />
            {status}
          </span>
        );
    }
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-[#0F172A]/80 p-5 shadow-xl backdrop-blur-md">
      <div className="flex flex-col justify-between gap-4 border-b border-slate-800/80 pb-4 md:flex-row md:items-center">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-medium uppercase tracking-wider text-slate-400">Transaction ID</span>
            <span className="rounded bg-[#0080F6]/10 px-2 py-0.5 font-mono text-xs font-bold text-[#0080F6]">
              {transaction.id}
            </span>
          </div>
          <div className="mt-1 flex items-center space-x-3 text-xs text-slate-400">
            <span>Ref: <strong className="font-mono text-slate-200">{transaction.reference_id}</strong></span>
            <span>•</span>
            <span>Modality: <strong className="rounded bg-slate-800 px-1.5 py-0.5 text-slate-200">{transaction.transfer_type}</strong></span>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {durationMs !== undefined && durationMs !== null && (
            <div className="hidden rounded-lg bg-slate-900/60 px-3 py-1.5 text-right sm:block">
              <span className="text-[10px] uppercase text-slate-400">Elapsed Time</span>
              <p className="font-mono text-xs font-semibold text-slate-200">{(durationMs / 1000).toFixed(2)}s</p>
            </div>
          )}
          {getStatusBadge(finalStatus)}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="rounded-xl border border-slate-800/60 bg-slate-900/40 p-3">
          <span className="text-[11px] font-medium text-slate-400">Payout Amount</span>
          <p className="mt-1 text-lg font-bold tracking-tight text-white">{formatCurrency(transaction.amount)}</p>
        </div>

        <div className="rounded-xl border border-slate-800/60 bg-slate-900/40 p-3">
          <span className="text-[11px] font-medium text-slate-400">Beneficiary ID</span>
          <p className="mt-1 font-mono text-sm font-semibold text-slate-200 truncate">{transaction.beneficiary_id}</p>
        </div>

        <div className="rounded-xl border border-slate-800/60 bg-slate-900/40 p-3">
          <span className="text-[11px] font-medium text-slate-400">Transfer Channel</span>
          <p className="mt-1 text-sm font-semibold text-slate-200">{transaction.transfer_type} Network</p>
        </div>

        <div className="rounded-xl border border-slate-800/60 bg-slate-900/40 p-3">
          <span className="text-[11px] font-medium text-slate-400">Initiation Timestamp</span>
          <p className="mt-1 font-mono text-xs text-slate-300 truncate">
            {new Date(transaction.created_at).toLocaleTimeString('en-US', { hour12: false, timeZone: 'UTC' })} UTC
          </p>
        </div>
      </div>
    </div>
  );
}
