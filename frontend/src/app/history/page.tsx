"use client";

import { useEffect, useState } from "react";
import { AuthenticatedLayout } from "@/components/AuthenticatedLayout";
import { api } from "@/lib/api";
import { Transaction, Currency } from "@/types";

function formatMoney(value: string, currency: Currency) {
  const n = parseFloat(value);
  return new Intl.NumberFormat("pt-MZ", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n) + " " + currency;
}

const STATUS_LABELS: Record<string, string> = {
  completed: "Concluída",
  pending: "Pendente",
  failed: "Falhou",
  cancelled: "Cancelada",
};

const TYPE_LABELS: Record<string, string> = {
  deposit: "Depósito",
  conversion: "Conversão",
  withdrawal: "Levantamento",
  adjustment: "Ajuste",
};

export default function HistoryPage() {
  const [items, setItems] = useState<Transaction[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const pageSize = 10;

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const { data } = await api.get("/transactions", { params: { page, page_size: pageSize } });
        setItems(data.items);
        setTotal(data.total);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [page]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <AuthenticatedLayout>
      <div className="mx-auto max-w-3xl">
        <h1 className="font-display text-2xl font-medium text-sand-100">Histórico</h1>
        <p className="mt-1 text-sm text-sand-400">Todas as tuas transações, sem exceção</p>

        <div className="mt-6 space-y-2">
          {loading ? (
            Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-16 animate-pulse rounded-xl bg-ocean-800" />
            ))
          ) : items.length === 0 ? (
            <div className="rounded-xl border border-ocean-700 p-8 text-center text-sm text-sand-400">
              Nenhuma transação encontrada.
            </div>
          ) : (
            items.map((tx) => (
              <div
                key={tx.id}
                className="flex items-center justify-between rounded-xl border border-ocean-700 bg-ocean-800/40 px-4 py-3.5"
              >
                <div>
                  <p className="text-sm font-medium text-sand-100">{TYPE_LABELS[tx.type] || tx.type}</p>
                  <p className="text-xs text-sand-400">
                    {new Date(tx.created_at).toLocaleString("pt-MZ")} · {STATUS_LABELS[tx.status] || tx.status}
                  </p>
                  {tx.notes && <p className="mt-0.5 text-xs text-sand-400">{tx.notes}</p>}
                </div>
                <p className="font-mono text-sm font-medium text-sand-100">{formatMoney(tx.amount, tx.currency)}</p>
              </div>
            ))
          )}
        </div>

        {totalPages > 1 && (
          <div className="mt-6 flex items-center justify-center gap-3">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="rounded-lg border border-ocean-700 px-3 py-1.5 text-sm text-sand-200 disabled:opacity-40"
            >
              Anterior
            </button>
            <span className="text-sm text-sand-400">
              Página {page} de {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="rounded-lg border border-ocean-700 px-3 py-1.5 text-sm text-sand-200 disabled:opacity-40"
            >
              Próxima
            </button>
          </div>
        )}
      </div>
    </AuthenticatedLayout>
  );
}
