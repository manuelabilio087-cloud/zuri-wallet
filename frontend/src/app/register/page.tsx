"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { api, getErrorMessage } from "@/lib/api";

interface RegisterForm {
  full_name: string;
  email: string;
  password: string;
  confirm_password: string;
  phone?: string;
}

export default function RegisterPage() {
  const router = useRouter();
  const [serverError, setServerError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterForm>();

  async function onSubmit(data: RegisterForm) {
    setServerError(null);
    setSubmitting(true);
    try {
      await api.post("/auth/register", {
        full_name: data.full_name,
        email: data.email,
        password: data.password,
        phone: data.phone || undefined,
      });
      router.push("/login?registered=true");
    } catch (err) {
      setServerError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-ocean-950 px-4 py-10">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 h-10 w-10 rounded-xl bg-gradient-to-br from-sunset-400 to-tide-500" />
          <h1 className="font-display text-2xl font-medium text-sand-100">Cria a tua conta</h1>
          <p className="mt-1 text-sm text-sand-400">Leva menos de um minuto</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-sand-200">Nome completo</label>
            <input
              {...register("full_name", { required: "Introduz o teu nome completo", minLength: { value: 3, message: "Nome muito curto" } })}
              className="w-full rounded-lg border border-ocean-700 bg-ocean-800 px-3.5 py-2.5 text-sand-100 placeholder:text-sand-400 focus:border-tide-500 focus:outline-none"
              placeholder="Manuel Abílio"
            />
            {errors.full_name && <p className="mt-1 text-xs text-red-400">{errors.full_name.message}</p>}
          </div>

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
            <label className="mb-1.5 block text-sm font-medium text-sand-200">Telefone (opcional)</label>
            <input
              {...register("phone")}
              className="w-full rounded-lg border border-ocean-700 bg-ocean-800 px-3.5 py-2.5 text-sand-100 placeholder:text-sand-400 focus:border-tide-500 focus:outline-none"
              placeholder="84 123 4567"
            />
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium text-sand-200">Senha</label>
            <input
              type="password"
              {...register("password", {
                required: "Cria uma senha",
                minLength: { value: 8, message: "Mínimo de 8 caracteres" },
                pattern: {
                  value: /^(?=.*[a-zA-Z])(?=.*\d).+$/,
                  message: "A senha precisa de letras e números",
                },
              })}
              className="w-full rounded-lg border border-ocean-700 bg-ocean-800 px-3.5 py-2.5 text-sand-100 placeholder:text-sand-400 focus:border-tide-500 focus:outline-none"
              placeholder="Mínimo 8 caracteres, letras e números"
            />
            {errors.password && <p className="mt-1 text-xs text-red-400">{errors.password.message}</p>}
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium text-sand-200">Confirmar senha</label>
            <input
              type="password"
              {...register("confirm_password", {
                required: "Confirma a tua senha",
                validate: (value) => value === watch("password") || "As senhas não coincidem",
              })}
              className="w-full rounded-lg border border-ocean-700 bg-ocean-800 px-3.5 py-2.5 text-sand-100 placeholder:text-sand-400 focus:border-tide-500 focus:outline-none"
              placeholder="••••••••"
            />
            {errors.confirm_password && (
              <p className="mt-1 text-xs text-red-400">{errors.confirm_password.message}</p>
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
            {submitting ? "A criar conta..." : "Criar conta"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-sand-400">
          Já tens conta?{" "}
          <Link href="/login" className="font-medium text-tide-400 hover:text-tide-300">
            Entrar
          </Link>
        </p>
      </div>
    </div>
  );
}
