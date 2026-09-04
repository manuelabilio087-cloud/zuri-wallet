"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { api, getErrorMessage } from "@/lib/api";

interface ResetPasswordForm {
  new_password: string;
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={null}>
      <ResetPasswordInner />
    </Suspense>
  );
}

function ResetPasswordInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "";

  const [submitting, setSubmitting] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordForm>();

  async function onSubmit(data: ResetPasswordForm) {
    setServerError(null);
    setSubmitting(true);
    try {
      await api.post("/auth/password-reset/confirm", { token, new_password: data.new_password });
      setDone(true);
      setTimeout(() => router.push("/login"), 2000);
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
          <h1 className="font-display text-2xl font-medium text-sand-100">Nova senha</h1>
          <p className="mt-1 text-sm text-sand-400">Escolhe uma nova senha para a tua conta</p>
        </div>

        {!token ? (
          <div className="rounded-lg border border-red-900 bg-red-950/50 px-3.5 py-3 text-sm text-red-300">
            Link inválido. Pede um novo link de recuperação.
          </div>
        ) : done ? (
          <div className="rounded-lg border border-tide-800 bg-tide-950/50 px-3.5 py-3 text-sm text-tide-300">
            Senha alterada com sucesso. A redirecionar para o login...
          </div>
        ) : (
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-sand-200">Nova senha</label>
              <input
                type="password"
                {...register("new_password", {
                  required: "Introduz a nova senha",
                  minLength: { value: 8, message: "Mínimo de 8 caracteres" },
                })}
                className="w-full rounded-lg border border-ocean-700 bg-ocean-800 px-3.5 py-2.5 text-sand-100 placeholder:text-sand-400 focus:border-tide-500 focus:outline-none"
                placeholder="••••••••"
              />
              {errors.new_password && (
                <p className="mt-1 text-xs text-red-400">{errors.new_password.message}</p>
              )}
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
              {submitting ? "A guardar..." : "Guardar nova senha"}
            </button>
          </form>
        )}

        <p className="mt-6 text-center text-sm text-sand-400">
          <Link href="/login" className="font-medium text-tide-400 hover:text-tide-300">
            Voltar ao login
          </Link>
        </p>
      </div>
    </div>
  );
}
