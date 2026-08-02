"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AuthenticatedLayout } from "@/components/AuthenticatedLayout";
import { CurrencyBadge } from "@/components/CurrencyBadge";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { Wallet, Transaction, Currency } from "@/types";

function formatMoney(value: string, currency: Currency) {
  const n = parseFloat(value);
  return new Intl.NumberFormat("pt-MZ", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n) + " " + currency;
}

function EyeIcon({ open }: { open: boolean }) {
  if (open) {
    return (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8Z" />
        <circle cx="12" cy="12" r="3" />
      </svg>
    );
  }
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
      <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 11 7 11 7a13.16 13.16 0 0 1-1.67 2.68" />
      <path d="M6.61 6.61A13.526 13.526 0 0 0 1 12s4 7 11 7a9.74 9.74 0 0 0 5.39-1.61" />
      <line x1="1" y1="1" x2="23" y2="23" />
    </svg>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [hideBalance, setHideBalance] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [walletRes, txRes] = await Promise.all([
          api.get<Wallet>("/wallet/me"),
          api.get("/transactions", { params: { page: 1, page_size: 5 } }),
        ]);
        setWallet(walletRes.data);
        setTransactions(txRes.data.items);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const mznBalance = wallet?.balances.find((b) => b.currency === "MZN");
  const firstName = user?.full_name?.split(" ")[0];
  const displayBalance = loading
    ? "···"
    : hideBalance
      ? "•••• •• MZN"
      : mznBalance
        ? formatMoney(mznBalance.balance, "MZN")
        : "0,00 MZN";

  return (
    <AuthenticatedLayout>
      <div className="mx-auto max-w-4xl">
        <h1 className="font-display text-2xl font-medium text-sand-100">Olá, {firstName}</h1>
        <p className="mt-1 text-sm text-sand-400">Aqui está o resumo da tua carteira</p>

        {/* Cartão principal — moeda base MZN */}
        <div className="mt-6 rounded-2xl bg-wallet-card p-6 shadow-xl">
          <div className="flex items-center gap-2">
            <p className="text-xs font-medium uppercase tracking-wider text-sand-400">Saldo disponível</p>
            <button
              onClick={() => setHideBalance((v) => !v)}
              aria-label={hideBalance ? "Mostrar saldo" : "Esconder saldo"}
              className="text-sand-400 transition-colors hover:text-sand-100"
            >
              <EyeIcon open={!hideBalance} />
            </button>
          </div>
          <p className="mt-2 font-mono text-3xl font-medium text-sand-100">{displayBalance}</p>
          <div className="mt-6 flex gap-3">
            <Link
              href="/deposit"
              className="rounded-lg bg-tide-500 px-4 py-2 text-sm font-semibold text-ocean-950 hover:bg-tide-400"
            >
              Depositar
            </Link>
            <button
              disabled
              title="Levantamentos chegam numa próxima fase"
              className="cursor-not-allowed rounded-lg border border-ocean-600 px-4 py-2 text-sm font-medium text-sand-400 opacity-60"
            >
              Levantar
            </button>
            <Link
              href="/history"
              className="rounded-lg border border-ocean-600 px-4 py-2 text-sm font-medium text-sand-100 hover:bg-ocean-800"
            >
              Histórico
            </Link>
          </div>
        </div>

        {/* Grid de saldos por moeda */}
        <h2 className="mb-3 mt-8 text-sm font-medium uppercase tracking-wider text-sand-400">
          Saldos por moeda
        </h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {loading
            ? Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="h-20 animate-pulse rounded-xl bg-ocean-800" />
              ))
            : wallet?.balances.map((b) => (
                <div key={b.currency} className="rounded-xl border border-ocean-700 bg-ocean-800/50 p-4">
                  <CurrencyBadge currency={b.currency} />
                  <p className="mt-2 font-mono text-lg text-sand-100">{formatMoney(b.balance, b.currency)}</p>
                </div>
              ))}
        </div>

        {/* Histórico recente */}
        <h2 className="mb-3 mt-8 text-sm font-medium uppercase tracking-wider text-sand-400">
          Atividade recente
        </h2>
        <div className="overflow-hidden rounded-xl border border-ocean-700">
          {loading ? (
            <div className="space-y-2 p-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-12 animate-pulse rounded-lg bg-ocean-800" />
              ))}
            </div>
          ) : transactions.length === 0 ? (
            <div className="p-8 text-center text-sm text-sand-400">
              Ainda não tens transações. Faz o teu primeiro depósito para começar.
            </div>
          ) : (
            <table className="w-full text-sm">
              <tbody className="zuri-tx-body">
                {transactions.map((tx) => (
                  <tr key={tx.id} className="zuri-tx-row border-b border-ocean-700 last:border-0">
                    <td data-label="Tipo" className="px-4 py-3 text-sand-100">
                      {tx.type === "deposit" ? "Depósito" : tx.type === "conversion" ? "Conversão" : tx.type}
                    </td>
                    <td data-label="Valor" className="px-4 py-3 text-right font-mono text-sand-100">
                      {formatMoney(tx.amount, tx.currency)}
                    </td>
                    <td data-label="Data" className="px-4 py-3 text-right text-sand-400">
                      {new Date(tx.created_at).toLocaleDateString("pt-MZ")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <style>{`
        @media (max-width: 640px) {
          .zuri-tx-row {
            display: flex;
            flex-direction: column;
            padding: 0.75rem 1rem;
          }
          .zuri-tx-row td {
            display: flex;
            justify-content: space-between;
            padding: 0.2rem 0;
            text-align: left !important;
          }
          .zuri-tx-row td::before {
            content: attr(data-label);
            color: #9FB3C8;
            font-size: 0.75rem;
          }
        }
      `}</style>
    </AuthenticatedLayout>
  );
}
