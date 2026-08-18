import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css';

const inter = Inter({
  variable: '--font-sans',
  subsets: ['latin'],
});

const jetbrainsMono = JetBrains_Mono({
  variable: '--font-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'Decentro Trace — AI-Powered Fintech Transaction Debugger',
  description:
    'Deterministic lifecycle reconstruction, failure detection, ledger reconciliation, and AI investigation for fintech payout workflows.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable} dark antialiased`}>
      <body className="min-h-screen bg-[#0B1120] text-slate-100 font-sans selection:bg-[#0080F6]/30 selection:text-white">
        {children}
      </body>
    </html>
  );
}
