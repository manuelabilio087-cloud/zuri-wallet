"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Sidebar } from "@/components/Sidebar";

export function AuthenticatedLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [user, loading, router]);

  if (loading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-ocean-950">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-tide-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-ocean-950">
      <Sidebar />
      <main className="zuri-main px-5 py-8 sm:px-8">{children}</main>
      <style>{`
        .zuri-main {
          margin-left: 0;
          padding-top: 4.5rem;
        }
        @media (min-width: 1024px) {
          .zuri-main {
            margin-left: 260px;
            padding-top: 2rem;
          }
        }
      `}</style>
    </div>
  );
}
