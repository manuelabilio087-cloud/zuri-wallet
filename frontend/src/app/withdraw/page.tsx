"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AuthenticatedLayout } from "@/components/AuthenticatedLayout";
import { useAuth } from "@/lib/auth-context";
import { api, getErrorMessage } from "@/lib/api";
import { Wallet, Withdrawal } from "@/types";

type Step = "form" | "done";

const NETWORKS = ["BSC", "TRX", "ETH"];

export default function WithdrawPage() {
  const router = useRouter();
  const { user } = useAuth();

  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [loadingWallet, setLoadingWallet] = useState(true);

  const [step, setStep] = useState<Step>("form");
  const [amount, setAmount] = useState("");
  const [address, setAddress] = useState("");
  const [network, setNetwork] = useState("BSC");
  const [pin, setPin] = useState("");
  const [withdrawal, setWithdrawal] = useState<Withdrawal | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api
      .get<Wallet>("/wallet/me")
      .then(({ data }) => setWallet(data))
      .finally(() => setLoadingWallet(false));
  }, []);

  const usdBalance = wallet?.balances.find((b) => b.currency === "USD")?.balance ?? "0.00";

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const { data } = await api.post<Withdrawal>("/withdrawals", {
        currency: "USD",
        amount: parseFloat(amount),
        destination_address: address,
        network,
        pin,
      });
      setWithdrawal(data);
      setStep("done");
    } catch (err) {
      setError(getErrorMessage(err));
      setPin(""); // nunca reaproveitar o PIN escrito depois de um erro
    } finally {
      setSubmitting(false);
    }
  }

  if (loadingWallet) return null;

  if (user && !user.has_transaction_pin) {
    return (
      <AuthenticatedLayout>
        <div className="mx-auto max-w-md">
          <h1 className="font-display text-2xl font-medium text-sand-100">Levantar</h1>
          <div className="mt-6 rounded-xl border border-ocean-700 bg-ocean-800/50 p-6 text-center">
            <p className="text-sm text-sand-300">
              Antes de levantares, precisas de definir o teu PIN de levantamento.
            </p>
            <Link
              href="/profile"
              className="mt-5 inline-block w-full rounded-lg bg-tide-500 py-2.5 text-sm font-semibold text-ocean-950 hover:bg-tide-400"
            >
              Definir PIN no perfil
            </Link>
          </div>
        </div>
      </AuthenticatedLayout>
    );
  }

  return (
    <AuthenticatedLayout>
      <div className="mx-auto max-w-md">
        <h1 className="font-display text-2xl font-medium text-sand-100">Levantar</h1>
        <p className="mt-1 text-sm text-sand-400">Envia o teu saldo em USD para a tua conta Binance</p>

        {step === "form" && (
          <form onSubmit={handleSubmit} className="mt-6 space-y-5">
            <div className="rounded-lg border border-ocean-700 bg-ocean-800/40 px-3.5 py-2.5 text-sm text-sand-300">
              Saldo disponível: <span className="font-mono text-tide-400">{usdBalance} USD</span>
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-sand-200">Valor (USD)</label>
              <input
                type="number"
                min="10"
                step="0.01"
                required
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="w-full rounded-lg border border-ocean-700 bg-ocean-800 px-3.5 py-2.5 font-mono text-sand-100 placeholder:text-sand-400 focus:border-tide-500 focus:outline-none"
                placeholder="0.00"
              />
              <p className="mt-1 text-xs text-sand-400">Mínimo de 10 USD por levantamento.</p>
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-sand-200">Rede</label>
              <div className="grid grid-cols-3 gap-2">
                {NETWORKS.map((n) => (
                  <button
                    type="button"
                    key={n}
                    onClick={() => setNetwork(n)}
                    className={
                      "rounded-lg border px-3 py-2 text-sm font-medium transition-colors " +
                      (network === n
                        ? "border-tide-500 bg-tide-500/10 text-tide-400"
                        : "border-ocean-700 text-sand-400 hover:bg-ocean-800")
                    }
                  >
                    {n}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-sand-200">
                Endereço/UID da tua conta Binance
              </label>
              <input
                required
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                className="w-full rounded-lg border border-ocean-700 bg-ocean-800 px-3.5 py-2.5 font-mono text-sm text-sand-100 placeholder:text-sand-400 focus:border-tide-500 focus:outline-none"
                placeholder="0x... ou UID Binance"
              />
              <p className="mt-1 text-xs text-sand-400">
                Confirma bem este endereço — envios para a rede errada não são recuperáveis.
              </p>
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-sand-200">PIN de levantamento</label>
              <input
                type="password"
                inputMode="numeric"
                maxLength={4}
                required
                value={pin}
                onChange={(e) => setPin(e.target.value.replace(/\D/g, ""))}
                className="w-full rounded-lg border border-ocean-700 bg-ocean-800 px-3.5 py-2.5 text-center text-lg tracking-[0.6em] text-sand-100 focus:border-tide-500 focus:outline-none"
                placeholder="••••"
              />
            </div>

            {error && (
              <div className="rounded-lg border border-red-900 bg-red-950/50 px-3.5 py-2.5 text-sm text-red-300">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={submitting || pin.length !== 4}
              className="w-full rounded-lg bg-tide-500 py-2.5 text-sm font-semibold text-ocean-950 hover:bg-tide-400 disabled:opacity-60"
            >
              {submitting ? "A processar..." : "Confirmar levantamento"}
            </button>
          </form>
        )}

        {step === "done" && withdrawal && (
          <div className="mt-6 rounded-xl border border-tide-600 bg-tide-500/10 p-6 text-center">
            <p className="text-lg font-medium text-tide-400">Levantamento enviado</p>
            <p className="mt-1 text-sm text-sand-300">
              {withdrawal.amount} {withdrawal.currency} a caminho de {withdrawal.destination_address.slice(0, 10)}...
              via {withdrawal.network}
            </p>
            <p className="mt-1 text-xs text-sand-400">Estado: {withdrawal.status}</p>
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
