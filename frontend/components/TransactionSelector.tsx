'use client';

import React, { useState } from 'react';
import { Search, Sparkles, ArrowRight, Zap, RefreshCw, CheckCircle2, AlertOctagon } from 'lucide-react';
import { Transaction } from '../lib/types';

interface Props {
  transactions: Transaction[];
  currentId: string;
  onSelectTransaction: (id: string) => void;
  isLoading: boolean;
}

export default function TransactionSelector({
  transactions,
  currentId,
  onSelectTransaction,
  isLoading,
}: Props) {
  const [searchInput, setSearchInput] = useState('');

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      onSelectTransaction(searchInput.trim());
    }
  };

  const samplePresets = [
    {
      id: 'dec_987654321',
      label: 'Demo 1: ₹25,000 IMPS Failure + Reversal',
      badge: 'Primary Failure Scenario',
      color: 'border-red-500/40 bg-red-950/20 text-red-300 hover:border-red-400',
      icon: AlertOctagon,
    },
    {
      id: 'dec_out_of_order_01',
      label: 'Demo 2: ₹10,000 NEFT Out-of-Order Webhook',
      badge: 'Secondary Demo',
      color: 'border-amber-500/40 bg-amber-950/20 text-amber-300 hover:border-amber-400',
      icon: RefreshCw,
    },
    {
      id: 'dec_123456789',
      label: 'Demo 3: ₹75,000 RTGS Success Settlement',
      badge: 'Success Flow',
      color: 'border-emerald-500/40 bg-emerald-950/20 text-emerald-300 hover:border-emerald-400',
      icon: CheckCircle2,
    },
    {
      id: 'dec_conflict_999',
      label: 'Demo 4: ₹5,000 UPI State Conflict',
      badge: 'Anomaly Flow',
      color: 'border-purple-500/40 bg-purple-950/20 text-purple-300 hover:border-purple-400',
      icon: Zap,
    },
  ];

  return (
    <div className="rounded-2xl border border-slate-800 bg-[#0F172A]/80 p-5 shadow-xl backdrop-blur-md">
      <div className="mb-4 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-base font-semibold text-white">Investigate Transaction</h2>
          <p className="text-xs text-slate-400">
            Enter a Decentro transaction ID or select a seeded scenario to reconstruct its deterministic lifecycle.
          </p>
        </div>
      </div>

      {/* Search Input Form */}
      <form onSubmit={handleSearchSubmit} className="relative mb-5">
        <div className="relative flex items-center">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400">
            <Search className="h-4 w-4" />
          </div>
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Enter Transaction ID (e.g. dec_987654321)..."
            className="w-full rounded-xl border border-slate-700 bg-slate-900/90 py-2.5 pl-10 pr-32 font-mono text-sm text-white placeholder-slate-500 transition-all focus:border-[#0080F6] focus:outline-none focus:ring-2 focus:ring-[#0080F6]/30"
          />
          <button
            type="submit"
            disabled={isLoading || !searchInput.trim()}
            className="absolute right-1.5 flex items-center space-x-1.5 rounded-lg bg-[#0080F6] px-4 py-1.5 text-xs font-semibold text-white shadow-md transition-all hover:bg-blue-600 disabled:opacity-50"
          >
            <span>Trace</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>
      </form>

      {/* Seed Presets */}
      <div>
        <div className="mb-2 flex items-center space-x-1.5 text-xs font-medium text-slate-400">
          <Sparkles className="h-3.5 w-3.5 text-[#0080F6]" />
          <span>Quick Load Seed Scenarios:</span>
        </div>
        <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2 lg:grid-cols-4">
          {samplePresets.map((preset) => {
            const Icon = preset.icon;
            const isSelected = currentId === preset.id;
            return (
              <button
                key={preset.id}
                type="button"
                onClick={() => onSelectTransaction(preset.id)}
                disabled={isLoading}
                className={`flex flex-col rounded-xl border p-3 text-left transition-all ${preset.color} ${
                  isSelected ? 'ring-2 ring-[#0080F6] shadow-lg shadow-[#0080F6]/10' : 'opacity-85 hover:opacity-100'
                }`}
              >
                <div className="mb-1 flex items-center justify-between">
                  <span className="font-mono text-xs font-bold">{preset.id}</span>
                  <Icon className="h-3.5 w-3.5" />
                </div>
                <span className="text-xs font-medium text-slate-200">{preset.label}</span>
                <span className="mt-1 text-[10px] text-slate-400">{preset.badge}</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
