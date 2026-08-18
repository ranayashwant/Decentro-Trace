'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Navbar from '../components/Navbar';
import TransactionSelector from '../components/TransactionSelector';
import TransactionSummaryCard from '../components/TransactionSummaryCard';
import TraceTimeline from '../components/TraceTimeline';
import DeterministicDiagnosisCard from '../components/DeterministicDiagnosisCard';
import IntegrityAndReconciliationCard from '../components/IntegrityAndReconciliationCard';
import AIInvestigationPanel from '../components/AIInvestigationPanel';
import EventPayloadModal from '../components/EventPayloadModal';
import { fetchTransactions, fetchTrace, investigateTransaction } from '../lib/api';
import { Transaction, Trace, Event, InvestigationResult } from '../lib/types';
import { AlertCircle, RefreshCw, Layers, ShieldCheck, Sparkles, Terminal } from 'lucide-react';

export default function HomePage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [selectedTxId, setSelectedTxId] = useState<string>('dec_987654321');
  const [trace, setTrace] = useState<Trace | null>(null);
  const [investigation, setInvestigation] = useState<InvestigationResult | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [highlightedEventId, setHighlightedEventId] = useState<string | null>(null);

  const [isLoadingTrace, setIsLoadingTrace] = useState<boolean>(false);
  const [isLoadingAI, setIsLoadingAI] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Load transactions list on mount
  useEffect(() => {
    async function loadTxList() {
      try {
        const list = await fetchTransactions();
        setTransactions(list);
      } catch (err) {
        console.error('Could not load transactions list:', err);
      }
    }
    loadTxList();
  }, []);

  // Load trace when selectedTxId changes
  const loadTrace = useCallback(async (txId: string) => {
    setIsLoadingTrace(true);
    setErrorMessage(null);
    setInvestigation(null);
    setHighlightedEventId(null);
    try {
      const traceData = await fetchTrace(txId);
      setTrace(traceData);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load trace data.';
      setErrorMessage(msg);
      setTrace(null);
    } finally {
      setIsLoadingTrace(false);
    }
  }, []);

  useEffect(() => {
    if (selectedTxId) {
      loadTrace(selectedTxId);
    }
  }, [selectedTxId, loadTrace]);

  // Trigger AI Investigation
  const handleRunAI = async () => {
    if (!selectedTxId) return;
    setIsLoadingAI(true);
    try {
      const result = await investigateTransaction(selectedTxId);
      setInvestigation(result);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'AI Investigation failed.';
      alert(msg);
    } finally {
      setIsLoadingAI(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B1120] text-slate-100 pb-16">
      <Navbar />

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {/* Top Search & Presets */}
        <TransactionSelector
          transactions={transactions}
          currentId={selectedTxId}
          onSelectTransaction={(id) => setSelectedTxId(id)}
          isLoading={isLoadingTrace}
        />

        {/* Error state */}
        {errorMessage && (
          <div className="mt-6 rounded-2xl border border-red-500/40 bg-red-950/30 p-5 text-red-200">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <h3 className="font-bold">Transaction Trace Error</h3>
            </div>
            <p className="mt-1 text-xs">{errorMessage}</p>
          </div>
        )}

        {/* Loading state */}
        {isLoadingTrace && (
          <div className="mt-12 flex flex-col items-center justify-center space-y-3 py-16">
            <div className="h-9 w-9 animate-spin rounded-full border-3 border-[#0080F6] border-t-transparent shadow-lg shadow-blue-500/20" />
            <p className="font-mono text-xs text-slate-400">Reconstructing deterministic transaction trace…</p>
          </div>
        )}

        {/* Loaded Trace Dashboard */}
        {!isLoadingTrace && trace && (
          <div className="mt-6 space-y-6">
            {/* 1. Transaction Overview Card */}
            <TransactionSummaryCard
              transaction={trace.transaction}
              finalStatus={trace.lifecycle.final_status}
              durationMs={trace.lifecycle.duration_ms}
            />

            {/* 2. Deterministic Diagnosis (Software Layer) */}
            <DeterministicDiagnosisCard failureAnalysis={trace.failure_analysis} />

            {/* 3. Main Split View: Lifecycle Timeline vs AI Investigation */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
              {/* Left Column: Timeline (7 cols) */}
              <div className="lg:col-span-7">
                <TraceTimeline
                  canonicalEvents={trace.canonical_events}
                  duplicateEvents={trace.duplicate_events}
                  onSelectEvent={(evt) => setSelectedEvent(evt)}
                  selectedEventId={highlightedEventId}
                />
              </div>

              {/* Right Column: AI Investigation (5 cols) */}
              <div className="lg:col-span-5 space-y-6">
                <AIInvestigationPanel
                  transactionId={trace.transaction.id}
                  onInvestigate={handleRunAI}
                  investigation={investigation}
                  isLoading={isLoadingAI}
                  onHighlightEvent={(evtId) => setHighlightedEventId(evtId)}
                />
              </div>
            </div>

            {/* 4. Integrity & Money Reconciliation Cards */}
            <IntegrityAndReconciliationCard
              integrity={trace.integrity}
              reconciliation={trace.reconciliation}
            />
          </div>
        )}
      </main>

      {/* Raw JSON Payload Modal */}
      <EventPayloadModal event={selectedEvent} onClose={() => setSelectedEvent(null)} />
    </div>
  );
}
