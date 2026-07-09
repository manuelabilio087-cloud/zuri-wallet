"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AuthenticatedLayout } from "@/components/AuthenticatedLayout";
import { api, getErrorMessage } from "@/lib/api";
import { Deposit, DepositProvider } from "@/types";
import clsx from "clsx";

type Step = "form" | "pending" | "done";

export default function DepositPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("form");
  const [provider, setProvider] = useState<DepositProvider>("mpesa");
  const [amount, setAmount] = useState("");
  const [phone, setPhone] = useState("");
  const [deposit, setDeposit] = useState<Deposit | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleCreateDeposit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const { data } = await api.post<Deposit>("/deposits", {
        provider,
        amount: parseFloat(amount),
        phone,
      });
      setDeposit(data);
      setStep("pending");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleConfirm() {
    if (!deposit) return;
    setSubmitting(true);
    setError(null);
    try {
      await api.post<Deposit>("/deposits/confirm", { reference_code: deposit.reference_code });
      setStep("done");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthenticatedLayout>
      <div className="mx-auto max-w-md">
        <h1 className="font-display text-2xl font-medium text-sand-100">Depositar</h1>
        <p className="mt-1 text-sm text-sand-400">Adiciona saldo via M-Pesa ou e-Mola</p>

        {step === "form" && (
          <form onSubmit={handleCreateDeposit} className="mt-6 space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-sand-200">Método</label>
              <div className="grid grid-cols-2 gap-3">
                {(["mpesa", "emola"] as DepositProvider[]).map((p) => (
                  <button
                    type="button"
                    key={p}
                    onClick={() => setProvider(p)}
                    className={clsx(
                      "rounded-lg border px-4 py-3 text-sm font-medium capitalize transition-colors",
                      provider === p
                        ? "border-tide-500 bg-tide-500/10 text-tide-400"
                        : "border-ocean-700 text-sand-400 hover:bg-ocean-800"
                    )}
                  >
                    {p === "mpesa" ? "M-Pesa" : "e-Mola"}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-sand-200">Valor (MZN)</label>
              <input
                type="number"
                min="1"
                step="0.01"
                required
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="w-full rounded-lg border border-ocean-700 bg-ocean-800 px-3.5 py-2.5 font-mono text-sand-100 placeholder:text-sand-400 focus:border-tide-500 focus:outline-none"
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-sand-200">Número de telefone</label>
              <input
                required
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full rounded-lg border border-ocean-700 bg-ocean-800 px-3.5 py-2.5 text-sand-100 placeholder:text-sand-400 focus:border-tide-500 focus:outline-none"
                placeholder="84 123 4567"
              />
            </div>

            {error && (
              <div className="rounded-lg border border-red-900 bg-red-950/50 px-3.5 py-2.5 text-sm text-red-300">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="w-full rounded-lg bg-tide-500 py-2.5 text-sm font-semibold text-ocean-950 hover:bg-tide-400 disabled:opacity-60"
            >
              {submitting ? "A gerar referência..." : "Continuar"}
            </button>
          </form>
        )}

        {step === "pending" && deposit && (
          <div className="mt-6 rounded-xl border border-ocean-700 bg-ocean-800/50 p-6 text-center">
            <p className="text-sm text-sand-400">Referência gerada</p>
            <p className="mt-2 font-mono text-2xl font-medium tracking-wider text-tide-400">
              {deposit.reference_code}
            </p>
            <p className="mt-4 text-sm text-sand-300">
              Confirma o pagamento de <strong>{deposit.amount} MZN</strong> na app do{" "}
              {deposit.provider === "mpesa" ? "M-Pesa" : "e-Mola"}.
            </p>
            <p className="mt-1 text-xs text-sand-400">
              (Ambiente de desenvolvimento: a confirmação é simulada — clica abaixo para simular o pagamento)
            </p>

            {error && <p className="mt-3 text-sm text-red-400">{error}</p>}

            <button
              onClick={handleConfirm}
              disabled={submitting}
              className="mt-5 w-full rounded-lg bg-tide-500 py-2.5 text-sm font-semibold text-ocean-950 hover:bg-tide-400 disabled:opacity-60"
            >
              {submitting ? "A confirmar..." : "Simular confirmação de pagamento"}
            </button>
          </div>
        )}

        {step === "done" && (
          <div className="mt-6 rounded-xl border border-tide-600 bg-tide-500/10 p-6 text-center">
            <p className="text-lg font-medium text-tide-400">Depósito confirmado</p>
            <p className="mt-1 text-sm text-sand-300">O saldo já está disponível na tua carteira.</p>
            <button
              onClick={() => router.push("/dashboard")}
              className="mt-5 w-full rounded-lg bg-tide-500 py-2.5 text-sm font-semibold text-ocean-950 hover:bg-tide-400"
            >
              Voltar ao início
            </button>
          </div>
        )}
      </div>
    </AuthenticatedLayout>
  );
}
