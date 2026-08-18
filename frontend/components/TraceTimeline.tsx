'use client';

import React from 'react';
import { Event, TransactionStatus } from '../lib/types';
import {
  CheckCircle2,
  XCircle,
  Clock,
  Code2,
  RotateCcw,
  AlertTriangle,
  Layers,
  Send,
  Building2,
  Cpu,
  ArrowDown,
} from 'lucide-react';

interface Props {
  canonicalEvents: Event[];
  duplicateEvents: Event[];
  onSelectEvent: (event: Event) => void;
  selectedEventId?: string | null;
}

export default function TraceTimeline({
  canonicalEvents,
  duplicateEvents,
  onSelectEvent,
  selectedEventId,
}: Props) {
  const getEventIcon = (event: Event) => {
    switch (event.status) {
      case 'SUCCESS':
        return <CheckCircle2 className="h-4 w-4 text-emerald-400" />;
      case 'FAILURE':
        return <XCircle className="h-4 w-4 text-red-400" />;
      case 'REVERSED':
        return <RotateCcw className="h-4 w-4 text-blue-400" />;
      case 'PROCESSING':
        return <Cpu className="h-4 w-4 text-amber-400 animate-pulse" />;
      case 'PENDING':
        return <Clock className="h-4 w-4 text-amber-400" />;
      default:
        return <Send className="h-4 w-4 text-[#0080F6]" />;
    }
  };

  const getEventBadgeColor = (status: TransactionStatus) => {
    switch (status) {
      case 'SUCCESS':
        return 'border-emerald-500/30 bg-emerald-950/40 text-emerald-300';
      case 'FAILURE':
        return 'border-red-500/30 bg-red-950/40 text-red-300';
      case 'REVERSED':
        return 'border-blue-500/30 bg-blue-950/40 text-blue-300';
      case 'PROCESSING':
      case 'PENDING':
        return 'border-amber-500/30 bg-amber-950/40 text-amber-300';
      default:
        return 'border-slate-700 bg-slate-800 text-slate-300';
    }
  };

  const formatTimestamp = (isoStr: string) => {
    const d = new Date(isoStr);
    return d.toISOString().substring(11, 23); // HH:mm:ss.sss
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-[#0F172A]/80 p-5 shadow-xl backdrop-blur-md">
      {/* Header */}
      <div className="mb-5 flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-3.5">
        <div className="flex items-center space-x-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#0080F6]/10 text-[#0080F6] border border-[#0080F6]/20">
            <Layers className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Canonical Lifecycle Timeline</h3>
            <p className="text-[11px] text-slate-400">Deterministic causal order (occurred_at ASC)</p>
          </div>
        </div>
        <span className="rounded-full border border-slate-700 bg-slate-800/80 px-2.5 py-0.5 text-xs font-semibold text-slate-300">
          {canonicalEvents.length} Verified Stages
        </span>
      </div>

      {/* Connected Stream Timeline */}
      <div className="relative space-y-4">
        {canonicalEvents.map((evt, idx) => {
          const isSelected = selectedEventId === evt.id;
          const isLast = idx === canonicalEvents.length - 1;
          const isOutOfOrder =
            idx > 0 &&
            new Date(evt.received_at).getTime() <
              new Date(canonicalEvents[idx - 1].received_at).getTime();

          return (
            <div key={evt.id} id={`timeline-${evt.id}`} className="relative flex items-stretch space-x-4">
              {/* Left Column: Step Node & Vertical Line */}
              <div className="relative flex flex-col items-center">
                {/* Step Circle Node */}
                <div
                  className={`relative z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border shadow-md transition-all ${
                    evt.status === 'FAILURE'
                      ? 'border-red-500/50 bg-red-950 text-red-400 shadow-red-500/20 ring-2 ring-red-500/20'
                      : evt.status === 'SUCCESS'
                      ? 'border-emerald-500/50 bg-emerald-950 text-emerald-400 shadow-emerald-500/20 ring-2 ring-emerald-500/20'
                      : evt.status === 'REVERSED'
                      ? 'border-blue-500/50 bg-blue-950 text-blue-400 shadow-blue-500/20 ring-2 ring-blue-500/20'
                      : isSelected
                      ? 'border-[#0080F6] bg-slate-900 text-[#0080F6] shadow-[#0080F6]/30 ring-2 ring-[#0080F6]/40'
                      : 'border-slate-700 bg-slate-900 text-slate-300'
                  }`}
                >
                  {getEventIcon(evt)}
                </div>

                {/* Vertical Connector Line between nodes */}
                {!isLast && (
                  <div className="w-0.5 flex-1 bg-gradient-to-b from-slate-700 to-slate-800 my-1" />
                )}
              </div>

              {/* Right Column: Event Content Card */}
              <div
                className={`flex-1 rounded-xl border p-4 transition-all ${
                  isSelected
                    ? 'border-[#0080F6] bg-slate-900 shadow-lg shadow-[#0080F6]/10 ring-1 ring-[#0080F6]/50'
                    : 'border-slate-800/90 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900/90'
                }`}
              >
                {/* Event Top Bar */}
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs font-bold tracking-tight text-white sm:text-sm">
                      {evt.event_type.replace(/_/g, ' ')}
                    </span>
                    <span
                      className={`rounded px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider border ${getEventBadgeColor(
                        evt.status
                      )}`}
                    >
                      {evt.status}
                    </span>
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs font-medium text-slate-400">
                      {formatTimestamp(evt.occurred_at)} UTC
                    </span>
                    <button
                      type="button"
                      onClick={() => onSelectEvent(evt)}
                      className="flex items-center space-x-1 rounded-lg border border-slate-700 bg-slate-800/90 px-2.5 py-1 text-[11px] font-medium text-slate-200 shadow-sm transition-all hover:border-[#0080F6] hover:bg-[#0080F6]/10 hover:text-white"
                    >
                      <Code2 className="h-3.5 w-3.5 text-[#0080F6]" />
                      <span>Payload</span>
                    </button>
                  </div>
                </div>

                {/* Event Source & Correlation Meta */}
                <div className="mt-2.5 flex flex-wrap items-center gap-2 text-xs text-slate-400">
                  <span className="inline-flex items-center space-x-1.5 rounded-md border border-slate-800 bg-slate-950/60 px-2 py-0.5">
                    <Building2 className="h-3 w-3 text-slate-400" />
                    <span className="font-medium text-slate-300">{evt.source}</span>
                  </span>

                  {evt.correlation_id && (
                    <span className="font-mono text-[11px] text-slate-400">
                      Correlation: <strong className="text-slate-200">{evt.correlation_id}</strong>
                    </span>
                  )}

                  {isOutOfOrder && (
                    <span className="inline-flex items-center gap-1 rounded-md border border-amber-800/40 bg-amber-950/60 px-2 py-0.5 text-[10px] font-semibold text-amber-300">
                      <AlertTriangle className="h-3 w-3 text-amber-400" />
                      Received out-of-order
                    </span>
                  )}
                </div>

                {/* Observed error callout box if failing */}
                {evt.status === 'FAILURE' && evt.payload && (
                  <div className="mt-3 rounded-lg border border-red-900/60 bg-red-950/30 p-3 text-xs text-red-200">
                    <p className="font-semibold text-red-300">
                      Observed Error Code:{' '}
                      <span className="rounded bg-red-950/80 px-1.5 py-0.5 font-mono text-red-200 border border-red-800/60">
                        {String(
                          evt.payload.provider_error_code ||
                            evt.payload.response_code ||
                            evt.payload.error_code ||
                            'FAILURE'
                        )}
                      </span>
                    </p>
                    <p className="mt-1 text-[11px] text-red-300/90">
                      {String(
                        evt.payload.provider_error_message ||
                          evt.payload.message ||
                          'Downstream partner system reported failure.'
                      )}
                    </p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
