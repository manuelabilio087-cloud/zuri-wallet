"use client";

import { useState } from "react";
import { AuthenticatedLayout } from "@/components/AuthenticatedLayout";
import { useAuth } from "@/lib/auth-context";
import { api, getErrorMessage } from "@/lib/api";

export default function ProfilePage() {
  const { user, refreshUser } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [phone, setPhone] = useState(user?.phone || "");
  const [city, setCity] = useState(user?.city || "");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const [pinPassword, setPinPassword] = useState("");
  const [pin, setPin] = useState("");
  const [pinConfirm, setPinConfirm] = useState("");
  const [pinMessage, setPinMessage] = useState<string | null>(null);
  const [pinError, setPinError] = useState<string | null>(null);
  const [pinSubmitting, setPinSubmitting] = useState(false);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setSubmitting(true);
    try {
      await api.patch("/profile", { full_name: fullName, phone, city });
      await refreshUser();
      setMessage("Perfil atualizado com sucesso.");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleSetPin(e: React.FormEvent) {
    e.preventDefault();
    setPinError(null);
    setPinMessage(null);

    if (pin !== pinConfirm) {
      setPinError("Os dois PINs não coincidem.");
      return;
    }

    setPinSubmitting(true);
    try {
      await api.post("/profile/pin", { account_password: pinPassword, pin });
      await refreshUser();
      setPinMessage("PIN de levantamento definido com sucesso.");
      setPinPassword("");
      setPin("");
      setPinConfirm("");
    } catch (err) {
      setPinError(getErrorMessage(err));
    } finally {
      setPinSubmitting(false);
    }
  }

  if (!user) return null;

  return (
    <AuthenticatedLayout>
      <div className="mx-auto max-w-md space-y-8">
        <div>
          <h1 className="font-display text-2xl font-medium text-sand-100">O teu perfil</h1>
          <p className="mt-1 text-sm text-sand-400">Gere os teus dados pessoais</p>

          <form onSubmit={handleSave} className="mt-6 space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-sand-200">E-mail</label>
              <input
                disabled
                value={user.email}
                className="w-full rounded-lg border border-ocean-700 bg-ocean-800/50 px-3.5 py-2.5 text-sand-400"
              />
              <p className="mt-1 text-xs text-sand-400">O e-mail não pode ser alterado.</p>
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-sand-200">Nome completo</label>
              <input
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full rounded-lg border border-ocean-700 bg-ocean-800 px-3.5 py-2.5 text-sand-100 focus:border-tide-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-sand-200">Telefone</label>
              <input
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full rounded-lg border border-ocean-700 bg-ocean-800 px-3.5 py-2.5 text-sand-100 focus:border-tide-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-sand-200">Cidade</label>
              <input
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="w-full rounded-lg border border-ocean-700 bg-ocean-800 px-3.5 py-2.5 text-sand-100 focus:border-tide-500 focus:outline-none"
              />
            </div>

            <div className="rounded-lg border border-ocean-700 bg-ocean-800/40 px-3.5 py-2.5 text-xs text-sand-400">
              Conta criada em {new Date(user.created_at).toLocaleDateString("pt-MZ")}
              {user.last_login_at && (
                <> · Último acesso em {new Date(user.last_login_at).toLocaleDateString("pt-MZ")}</>
              )}
            </div>

            {message && (
              <div className="rounded-lg border border-tide-600 bg-tide-500/10 px-3.5 py-2.5 text-sm text-tide-400">
                {message}
              </div>
            )}
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
              {submitting ? "A guardar..." : "Guardar alterações"}
            </button>
          </form>
        </div>

        <div className="border-t border-ocean-800 pt-6">
          <h2 className="font-display text-lg font-medium text-sand-100">PIN de levantamento</h2>
          <p className="mt-1 text-sm text-sand-400">
            {user.has_transaction_pin
              ? "Já tens um PIN definido. Usa este formulário para o mudar."
              : "Precisas de definir um PIN de 4 dígitos antes de conseguires levantar fundos."}
          </p>

          <form onSubmit={handleSetPin} className="mt-4 space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-sand-200">Senha da conta</label>
              <input
                type="password"
                value={pinPassword}
                onChange={(e) => setPinPassword(e.target.value)}
                required
                className="w-full rounded-lg border border-ocean-700 bg-ocean-800 px-3.5 py-2.5 text-sand-100 placeholder:text-sand-400 focus:border-tide-500 focus:outline-none"
                placeholder="Confirma com a tua senha"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-sand-200">Novo PIN</label>
                <input
                  type="password"
                  inputMode="numeric"
                  maxLength={4}
                  value={pin}
                  onChange={(e) => setPin(e.target.value.replace(/\D/g, ""))}
                  required
                  className="w-full rounded-lg border border-ocean-700 bg-ocean-800 px-3.5 py-2.5 text-center tracking-[0.5em] text-sand-100 focus:border-tide-500 focus:outline-none"
                  placeholder="••••"
                />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-sand-200">Confirmar PIN</label>
                <input
                  type="password"
                  inputMode="numeric"
                  maxLength={4}
                  value={pinConfirm}
                  onChange={(e) => setPinConfirm(e.target.value.replace(/\D/g, ""))}
                  required
                  className="w-full rounded-lg border border-ocean-700 bg-ocean-800 px-3.5 py-2.5 text-center tracking-[0.5em] text-sand-100 focus:border-tide-500 focus:outline-none"
                  placeholder="••••"
                />
              </div>
            </div>

            {pinMessage && (
              <div className="rounded-lg border border-tide-600 bg-tide-500/10 px-3.5 py-2.5 text-sm text-tide-400">
                {pinMessage}
              </div>
            )}
            {pinError && (
              <div className="rounded-lg border border-red-900 bg-red-950/50 px-3.5 py-2.5 text-sm text-red-300">
                {pinError}
              </div>
            )}

            <button
              type="submit"
              disabled={pinSubmitting}
              className="w-full rounded-lg border border-tide-600 bg-transparent py-2.5 text-sm font-semibold text-tide-400 hover:bg-tide-500/10 disabled:opacity-60"
            >
              {pinSubmitting ? "A guardar..." : user.has_transaction_pin ? "Mudar PIN" : "Definir PIN"}
            </button>
          </form>
        </div>
      </div>
    </AuthenticatedLayout>
  );
}

