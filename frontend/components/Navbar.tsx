'use client';

import React from 'react';
import { Activity, ShieldCheck, Terminal } from 'lucide-react';

export default function Navbar() {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-[#0B1120]/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3.5 sm:px-6 lg:px-8">
        {/* Brand Logo & Name */}
        <div className="flex items-center space-x-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-tr from-[#0080F6] to-cyan-400 shadow-md shadow-blue-500/20">
            <Activity className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-lg font-bold tracking-tight text-white">DECENTRO</span>
              <span className="rounded bg-[#0080F6]/20 px-1.5 py-0.5 text-xs font-semibold text-[#0080F6] border border-[#0080F6]/30">
                TRACE
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Fintech Transaction Debugger & Lifecycle Engine</p>
          </div>
        </div>

        {/* System Badges */}
        <div className="flex items-center space-x-3">
          <div className="hidden items-center space-x-1.5 rounded-full border border-emerald-500/30 bg-emerald-950/40 px-3 py-1 text-xs font-medium text-emerald-400 sm:flex">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
            </span>
            <span>Deterministic Engine Active</span>
          </div>

          <div className="flex items-center space-x-1.5 rounded-full border border-slate-700 bg-slate-800/60 px-3 py-1 text-xs font-medium text-slate-300">
            <ShieldCheck className="h-3.5 w-3.5 text-[#0080F6]" />
            <span>Synthetic Sandbox</span>
          </div>
        </div>
      </div>
    </header>
  );
}
