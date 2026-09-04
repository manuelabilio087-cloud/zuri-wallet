"use client";

import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { useAuth } from "@/lib/auth-context";
import { getErrorMessage } from "@/lib/api";

interface LoginForm {
  email: string;
  password: string;
}

export default function LoginPage() {
  const { login } = useAuth();
  const [serverError, setServerError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>();

  async function onSubmit(data: LoginForm) {
    setServerError(null);
    setSubmitting(true);
    try {
      await login(data.email, data.password);
    } catch (err) {
      setServerError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-ocean-950 px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 h-10 w-10 rounded-xl bg-gradient-to-br from-sunset-400 to-tide-500" />
          <h1 className="font-display text-2xl font-medium text-sand-100">Bem-vindo de volta</h1>
          <p className="mt-1 text-sm text-sand-400">Entra na tua Zuri Wallet</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-sand-200">E-mail</label>
            <input
              type="email"
              {...register("email", { required: "Introduz o teu e-mail" })}
              className="w-full rounded-lg border border-ocean-700 bg-ocean-800 px-3.5 py-2.5 text-sand-100 placeholder:text-sand-400 focus:border-tide-500 focus:outline-none"
              placeholder="teu@email.com"
            />
            {errors.email && <p className="mt-1 text-xs text-red-400">{errors.email.message}</p>}
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium text-sand-200">Senha</label>
            <input
              type="password"
              {...register("password", { required: "Introduz a tua senha" })}
              className="w-full rounded-lg border border-ocean-700 bg-ocean-800 px-3.5 py-2.5 text-sand-100 placeholder:text-sand-400 focus:border-tide-500 focus:outline-none"
              placeholder="••••••••"
            />
            {errors.password && <p className="mt-1 text-xs text-red-400">{errors.password.message}</p>}
            <div className="mt-1.5 text-right">
              <Link href="/forgot-password" className="text-xs text-sand-400 hover:text-tide-400">
                Esqueceste-te da senha?
              </Link>
            </div>
          </div>

          {serverError && (
            <div className="rounded-lg border border-red-900 bg-red-950/50 px-3.5 py-2.5 text-sm text-red-300">
              {serverError}
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-tide-500 py-2.5 text-sm font-semibold text-ocean-950 transition-colors hover:bg-tide-400 disabled:opacity-60"
          >
            {submitting ? "A entrar..." : "Entrar"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-sand-400">
          Ainda não tens conta?{" "}
          <Link href="/register" className="font-medium text-tide-400 hover:text-tide-300">
            Criar conta
          </Link>
        </p>
      </div>
    </div>
  );
}
