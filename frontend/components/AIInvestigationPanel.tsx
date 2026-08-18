'use client';

import React, { useState } from 'react';
import { InvestigationResult } from '../lib/types';
import { Sparkles, Bot, ArrowRight, ShieldAlert, CheckCircle2, AlertCircle, Link2, HelpCircle } from 'lucide-react';

interface Props {
  transactionId: string;
  onInvestigate: () => Promise<void>;
  investigation: InvestigationResult | null;
  isLoading: boolean;
  onHighlightEvent?: (eventId: string) => void;
}

export default function AIInvestigationPanel({
  transactionId,
  onInvestigate,
  investigation,
  isLoading,
  onHighlightEvent,
}: Props) {
  const getConfidenceBadge = (confidence: 'high' | 'medium' | 'low') => {
    switch (confidence) {
      case 'high':
        return (
          <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-950/40 px-2.5 py-0.5 text-xs font-semibold text-emerald-400">
            <CheckCircle2 className="h-3 w-3" />
            Confidence: HIGH
          </span>
        );
      case 'medium':
        return (
          <span className="inline-flex items-center gap-1 rounded-full border border-amber-500/30 bg-amber-950/40 px-2.5 py-0.5 text-xs font-semibold text-amber-400">
            <AlertCircle className="h-3 w-3" />
            Confidence: MEDIUM
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 rounded-full border border-red-500/30 bg-red-950/40 px-2.5 py-0.5 text-xs font-semibold text-red-400">
            <HelpCircle className="h-3 w-3" />
            Confidence: LOW
          </span>
        );
    }
  };

  return (
    <div className="rounded-2xl border border-blue-500/30 bg-gradient-to-br from-[#0F172A] via-[#0F172A] to-blue-950/20 p-5 shadow-2xl backdrop-blur-md">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-blue-500/20 pb-4">
        <div className="flex items-center space-x-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#0080F6]/20 text-[#0080F6] border border-[#0080F6]/30">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">AI INVESTIGATION & DIAGNOSIS</h3>
            <span className="text-[10px] font-medium uppercase tracking-wider text-blue-400">
              Layer 3 Interpretation (Explains Why It Matters)
            </span>
          </div>
        </div>

        {investigation ? (
          <div className="flex items-center space-x-2">
            {getConfidenceBadge(investigation.confidence)}
          </div>
        ) : (
          <button
            type="button"
            onClick={onInvestigate}
            disabled={isLoading}
            className="flex items-center space-x-2 rounded-xl bg-gradient-to-r from-[#0080F6] to-cyan-500 px-4 py-2 text-xs font-bold text-white shadow-lg shadow-blue-500/25 transition-all hover:opacity-95 hover:shadow-blue-500/40 disabled:opacity-50"
          >
            {isLoading ? (
              <>
                <div className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                <span>Synthesizing Trace...</span>
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                <span>Run AI Investigation</span>
              </>
            )}
          </button>
        )}
      </div>

      {/* Investigation Body */}
      {investigation ? (
        <div className="mt-4 space-y-4">
          {/* Summary */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
            <span className="text-[11px] font-bold uppercase tracking-wider text-[#0080F6]">What Happened</span>
            <p className="mt-1 text-xs leading-relaxed text-slate-200">{investigation.summary}</p>
          </div>

          {/* Root Cause */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
            <span className="text-[11px] font-bold uppercase tracking-wider text-amber-400">Root Cause Interpretation</span>
            <p className="mt-1 text-xs leading-relaxed text-slate-200">{investigation.root_cause}</p>
          </div>

          {/* Supporting Evidence References */}
          {investigation.evidence.length > 0 && (
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
              <div className="mb-2 flex items-center justify-between">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                  Observed Evidence Links
                </span>
                <span className="text-[10px] text-slate-500">Click to jump to event</span>
              </div>
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                {investigation.evidence.map((item, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      if (onHighlightEvent) onHighlightEvent(item.event_id);
                      const el = document.getElementById(`timeline-${item.event_id}`);
                      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }}
                    className="flex flex-col rounded-lg border border-slate-700/60 bg-slate-950/60 p-2.5 text-left transition-colors hover:border-[#0080F6] hover:bg-slate-900"
                  >
                    <div className="flex items-center space-x-1.5 font-mono text-[11px] font-bold text-[#0080F6]">
                      <Link2 className="h-3 w-3" />
                      <span>{item.event_id}</span>
                    </div>
                    <span className="mt-1 text-[11px] text-slate-300">{item.reason}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Recommended Next Action */}
          <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-4">
            <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-400">
              Recommended Next Action
            </span>
            <p className="mt-1 text-xs font-medium leading-relaxed text-slate-100">
              {investigation.recommended_action}
            </p>
          </div>

          {/* Uncertainty if present */}
          {investigation.uncertainty && (
            <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-3 text-xs text-amber-300">
              <span className="font-semibold">Observation Gaps: </span>
              <span>{investigation.uncertainty}</span>
            </div>
          )}
        </div>
      ) : (
        <div className="mt-5 flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-800 p-8 text-center">
          <Sparkles className="h-8 w-8 text-[#0080F6] opacity-60 animate-pulse" />
          <p className="mt-3 text-xs font-semibold text-slate-300">AI Investigation Ready</p>
          <p className="mt-1 max-w-md text-[11px] text-slate-500">
            Click &quot;Run AI Investigation&quot; to synthesize the canonical trace into a human-readable diagnosis, root cause breakdown, and next operational steps.
          </p>
        </div>
      )}
    </div>
  );
}
