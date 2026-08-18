'use client';

import React from 'react';
import { FailureAnalysis } from '../lib/types';
import { ShieldCheck, AlertOctagon, CheckCircle2, Server, Clock, AlertTriangle } from 'lucide-react';

interface Props {
  failureAnalysis: FailureAnalysis;
}

export default function DeterministicDiagnosisCard({ failureAnalysis }: Props) {
  if (!failureAnalysis.failed) {
    return (
      <div className="rounded-2xl border border-emerald-500/30 bg-emerald-950/20 p-5 shadow-xl backdrop-blur-md">
        <div className="flex items-center space-x-2 text-emerald-400">
          <CheckCircle2 className="h-5 w-5" />
          <h3 className="text-sm font-bold uppercase tracking-wider">Deterministic State: SUCCESS</h3>
        </div>
        <p className="mt-2 text-xs text-slate-300">
          No terminal failure or processing anomalies were detected in the lifecycle trace. All intermediate gateway transitions completed normally.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-red-500/40 bg-gradient-to-br from-[#0F172A] to-red-950/20 p-5 shadow-xl backdrop-blur-md">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-red-500/20 pb-3">
        <div className="flex items-center space-x-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-red-500/20 text-red-400 border border-red-500/30">
            <AlertOctagon className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">DETERMINISTIC DIAGNOSIS</h3>
            <span className="text-[10px] font-medium uppercase tracking-wider text-red-400">
              Computed by Software (Source of Truth)
            </span>
          </div>
        </div>
        <span className="rounded-full border border-red-500/40 bg-red-950/60 px-2.5 py-0.5 font-mono text-xs font-bold text-red-300">
          STAGE: {failureAnalysis.failure_stage}
        </span>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {/* Failure Point */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-3">
          <span className="text-[11px] font-medium text-slate-400">Failure Stage Point</span>
          <p className="mt-1 font-mono text-sm font-bold text-red-300">
            {failureAnalysis.failure_stage.replace(/_/g, ' ')}
          </p>
        </div>

        {/* Observed Status */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-3">
          <span className="text-[11px] font-medium text-slate-400">Observed Status</span>
          <p className="mt-1 font-mono text-sm font-bold text-red-400">
            {failureAnalysis.observed_status || 'FAILURE'}
          </p>
        </div>

        {/* Error Code & Message */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-3 sm:col-span-2 lg:col-span-1">
          <span className="text-[11px] font-medium text-slate-400">Observed Error Code</span>
          <p className="mt-1 font-mono text-xs font-semibold text-slate-200">
            <span className="rounded bg-red-950 px-1.5 py-0.5 text-red-300 border border-red-800/40">
              {failureAnalysis.observed_error_code || 'N/A'}
            </span>{' '}
            <span className="text-slate-300">{failureAnalysis.observed_error_message}</span>
          </p>
        </div>
      </div>

      {failureAnalysis.failure_timestamp && (
        <div className="mt-3 flex items-center space-x-2 text-[11px] text-slate-400">
          <Clock className="h-3.5 w-3.5 text-slate-500" />
          <span>
            Terminal failure callback registered at{' '}
            <strong className="font-mono text-slate-300">
              {new Date(failureAnalysis.failure_timestamp).toISOString()}
            </strong>
          </span>
        </div>
      )}
    </div>
  );
}
