'use client';

import React, { useState } from 'react';
import { Event } from '../lib/types';
import { X, Copy, Check, Terminal, Clock, ShieldCheck } from 'lucide-react';

interface Props {
  event: Event | null;
  onClose: () => void;
}

export default function EventPayloadModal({ event, onClose }: Props) {
  const [copied, setCopied] = useState(false);

  if (!event) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(event.payload, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
      <div className="relative w-full max-w-3xl rounded-2xl border border-slate-700 bg-[#0F172A] p-6 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-2">
            <Terminal className="h-5 w-5 text-[#0080F6]" />
            <div>
              <h3 className="text-base font-bold text-white">Event Raw Payload</h3>
              <p className="font-mono text-xs text-slate-400">ID: {event.id}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Metadata info row */}
        <div className="my-4 grid grid-cols-1 gap-2.5 sm:grid-cols-2 lg:grid-cols-4">
          <div className="min-w-0 rounded-xl border border-slate-800/90 bg-slate-900/80 p-3">
            <span className="block text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-1">
              Event Type
            </span>
            <p className="font-mono text-xs font-semibold text-slate-200 break-words">
              {event.event_type}
            </p>
          </div>
          <div className="min-w-0 rounded-xl border border-slate-800/90 bg-slate-900/80 p-3">
            <span className="block text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-1">
              Source
            </span>
            <p className="font-mono text-xs font-semibold text-[#0080F6] break-words">
              {event.source}
            </p>
          </div>
          <div className="min-w-0 rounded-xl border border-slate-800/90 bg-slate-900/80 p-3">
            <span className="block text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-1">
              Occurred At (UTC)
            </span>
            <p className="font-mono text-xs text-slate-300 truncate" title={new Date(event.occurred_at).toISOString()}>
              {new Date(event.occurred_at).toISOString()}
            </p>
          </div>
          <div className="min-w-0 rounded-xl border border-slate-800/90 bg-slate-900/80 p-3">
            <span className="block text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-1">
              Received At (UTC)
            </span>
            <p className="font-mono text-xs text-slate-300 truncate" title={new Date(event.received_at).toISOString()}>
              {new Date(event.received_at).toISOString()}
            </p>
          </div>
        </div>

        {/* Payload JSON view */}
        <div className="relative">
          <div className="flex items-center justify-between rounded-t-xl bg-slate-950 px-4 py-2 text-xs text-slate-400">
            <span>JSON Body</span>
            <button
              type="button"
              onClick={handleCopy}
              className="flex items-center space-x-1 text-xs text-slate-400 hover:text-white"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
              <span>{copied ? 'Copied' : 'Copy JSON'}</span>
            </button>
          </div>
          <pre className="max-h-72 overflow-y-auto rounded-b-xl border border-slate-800 bg-black/80 p-4 font-mono text-xs text-emerald-400">
            {JSON.stringify(event.payload, null, 2)}
          </pre>
        </div>

        {/* Footer */}
        <div className="mt-5 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl bg-slate-800 px-5 py-2 text-xs font-semibold text-white hover:bg-slate-700"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
