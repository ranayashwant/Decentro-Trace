'use client';

import React from 'react';
import { Event, TransactionStatus } from '../lib/types';
import {
  CheckCircle2,
  XCircle,
  Clock,
  ArrowRight,
  Code2,
  RotateCcw,
  AlertTriangle,
  Layers,
  Send,
  Building2,
  Cpu,
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
      <div className="mb-4 flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center space-x-2">
          <Layers className="h-4 w-4 text-[#0080F6]" />
          <h3 className="text-sm font-semibold text-white">Canonical Lifecycle Timeline</h3>
          <span className="rounded-full bg-slate-800 px-2 py-0.5 text-[11px] font-medium text-slate-300">
            {canonicalEvents.length} Events
          </span>
        </div>
        <span className="text-[11px] text-slate-400">Chronological Causal Order (occurred_at ASC)</span>
      </div>

      <div className="relative pl-4 sm:pl-6">
        {/* Timeline connector bar */}
        <div className="absolute bottom-4 left-[23px] sm:left-[31px] top-4 w-0.5 bg-slate-800" />

        <div className="space-y-4">
          {canonicalEvents.map((evt, idx) => {
            const isSelected = selectedEventId === evt.id;
            const isOutOfOrder =
              idx > 0 &&
              new Date(evt.received_at).getTime() <
                new Date(canonicalEvents[idx - 1].received_at).getTime();

            return (
              <div
                key={evt.id}
                id={`timeline-${evt.id}`}
                className={`group relative flex items-start space-x-3 rounded-xl border p-3.5 transition-all ${
                  isSelected
                    ? 'border-[#0080F6] bg-slate-900 shadow-md shadow-[#0080F6]/10 ring-1 ring-[#0080F6]/50'
                    : 'border-slate-800/80 bg-slate-900/50 hover:border-slate-700 hover:bg-slate-900/80'
                }`}
              >
                {/* Timeline node icon */}
                <div
                  className={`relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border ${
                    evt.status === 'FAILURE'
                      ? 'border-red-500/50 bg-red-950/80'
                      : evt.status === 'SUCCESS'
                      ? 'border-emerald-500/50 bg-emerald-950/80'
                      : 'border-slate-700 bg-slate-800'
                  }`}
                >
                  {getEventIcon(evt)}
                </div>

                {/* Event Information */}
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center justify-between gap-1.5">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-xs font-bold text-white">
                        {evt.event_type.replace(/_/g, ' ')}
                      </span>
                      <span
                        className={`rounded px-1.5 py-0.2 text-[10px] font-medium border ${getEventBadgeColor(
                          evt.status
                        )}`}
                      >
                        {evt.status}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-xs text-slate-400">
                        {formatTimestamp(evt.occurred_at)} UTC
                      </span>
                      <button
                        type="button"
                        onClick={() => onSelectEvent(evt)}
                        className="flex items-center space-x-1 rounded bg-slate-800 px-2 py-0.5 text-[11px] font-medium text-slate-300 transition-colors hover:bg-slate-700 hover:text-white"
                      >
                        <Code2 className="h-3 w-3" />
                        <span>Payload</span>
                      </button>
                    </div>
                  </div>

                  <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-400">
                    <span className="flex items-center space-x-1">
                      <Building2 className="h-3 w-3 text-slate-500" />
                      <span className="rounded bg-slate-800/80 px-1.5 py-0.5 text-[10px] text-slate-300">
                        {evt.source}
                      </span>
                    </span>
                    {evt.correlation_id && (
                      <span className="font-mono text-[11px] text-slate-400">
                        Correlation: <strong className="text-slate-300">{evt.correlation_id}</strong>
                      </span>
                    )}
                    {isOutOfOrder && (
                      <span className="inline-flex items-center gap-1 rounded bg-amber-950/60 px-1.5 py-0.5 text-[10px] font-medium text-amber-400 border border-amber-800/40">
                        <AlertTriangle className="h-2.5 w-2.5" />
                        Received out of order
                      </span>
                    )}
                  </div>

                  {/* Provider payload highlights if failing */}
                  {evt.status === 'FAILURE' && evt.payload && (
                    <div className="mt-2 rounded-lg border border-red-900/50 bg-red-950/30 p-2 text-xs text-red-300">
                      <p className="font-semibold text-red-200">
                        Observed Error:{' '}
                        <span className="font-mono">
                          {String(
                            evt.payload.provider_error_code ||
                              evt.payload.response_code ||
                              evt.payload.error_code ||
                              'FAILURE'
                          )}
                        </span>{' '}
                        —{' '}
                        {String(
                          evt.payload.provider_error_message ||
                            evt.payload.message ||
                            'Provider failure reported'
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
    </div>
  );
}
