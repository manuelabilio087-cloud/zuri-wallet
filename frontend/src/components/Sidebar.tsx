"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import clsx from "clsx";
import { useAuth } from "@/lib/auth-context";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Início", icon: "⌂" },
  { href: "/deposit", label: "Depositar", icon: "↓" },
  { href: "/history", label: "Histórico", icon: "≡" },
  { href: "/profile", label: "Perfil", icon: "◐" },
];

export function Sidebar() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <>
      {/* Botão hambúrguer — só visível em mobile */}
      <button
        onClick={() => setOpen(true)}
        className="zuri-mobile-trigger fixed left-4 top-4 z-30 flex h-10 w-10 items-center justify-center rounded-lg bg-ocean-800 text-sand-100 shadow-lg"
        aria-label="Abrir menu"
      >
        ☰
      </button>

      {/* Overlay mobile */}
      {open && (
        <div
          className="zuri-overlay fixed inset-0 z-40 bg-black/60"
          onClick={() => setOpen(false)}
        />
      )}

      <aside className={clsx("zuri-sidebar", open && "zuri-sidebar-open")}>
        <div className="flex h-full flex-col px-5 py-6">
          <div className="mb-8 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-sunset-line bg-gradient-to-br from-sunset-400 to-tide-500" />
              <span className="font-display text-lg font-medium text-sand-100">Zuri Wallet</span>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="zuri-close-btn text-sand-400 hover:text-sand-100"
              aria-label="Fechar menu"
            >
              ✕
            </button>
          </div>

          <nav className="flex flex-1 flex-col gap-1">
            {NAV_ITEMS.map((item) => {
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setOpen(false)}
                  className={clsx(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    active
                      ? "bg-tide-500/15 text-tide-400"
                      : "text-sand-400 hover:bg-ocean-800 hover:text-sand-100"
                  )}
                >
                  <span className="w-4 text-center">{item.icon}</span>
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="mt-auto border-t border-ocean-700 pt-4">
            <p className="truncate text-sm font-medium text-sand-100">{user?.full_name}</p>
            <p className="truncate text-xs text-sand-400">{user?.email}</p>
            <button
              onClick={logout}
              className="mt-3 text-xs font-medium text-sunset-400 hover:text-sunset-300"
            >
              Terminar sessão
            </button>
          </div>
        </div>
      </aside>

      <style>{`
        .zuri-sidebar {
          position: fixed;
          top: 0;
          left: 0;
          height: 100vh;
          width: 260px;
          background-color: #0B1B2B;
          border-right: 1px solid #1B3A54;
          z-index: 50;
          transform: translateX(-100%);
          transition: transform 0.25s ease;
        }
        .zuri-sidebar-open {
          transform: translateX(0);
        }
        .zuri-close-btn {
          display: block;
        }
        .zuri-mobile-trigger {
          display: flex;
        }

        @media (min-width: 1024px) {
          .zuri-sidebar {
            transform: translateX(0);
          }
          .zuri-mobile-trigger {
            display: none;
          }
          .zuri-overlay {
            display: none;
          }
          .zuri-close-btn {
            display: none;
          }
        }
      `}</style>
    </>
  );
}
