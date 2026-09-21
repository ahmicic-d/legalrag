import { NavLink, Outlet } from "react-router-dom";
import { Search, FileText, BarChart3, Info, Scale } from "lucide-react";

const navItems = [
  { to: "/", label: "Pretraživanje", icon: Search, end: true },
  { to: "/dokumenti", label: "Dokumenti", icon: FileText, end: false },
  { to: "/evaluacija", label: "Evaluacija", icon: BarChart3, end: false },
  { to: "/o-radu", label: "O radu", icon: Info, end: false },
];

export default function Layout() {
  return (
    <div className="flex min-h-screen">
      <aside className="fixed inset-y-0 left-0 hidden w-60 flex-col bg-ink text-white md:flex">
        <div className="flex items-center gap-3 border-b border-white/10 px-5 py-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary font-display text-lg text-bronze-light">
            §
          </div>
          <div>
            <div className="font-display text-base font-semibold leading-tight">LegalRag</div>
            <div className="text-[11px] text-white/50">Pravni RAG sustav</div>
          </div>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-4" aria-label="Glavna navigacija">
          {navItems.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition-colors ${
                  isActive
                    ? "bg-primary text-white"
                    : "text-white/70 hover:bg-white/5 hover:text-white"
                }`
              }
            >
              <Icon size={17} strokeWidth={2} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-white/10 px-5 py-4 text-[11px] leading-relaxed text-white/40">
          <div className="mb-1 flex items-center gap-1.5 text-white/60">
            <Scale size={12} /> Pravna napomena
          </div>
          Odgovori sustava nisu pravni savjet.
        </div>
      </aside>

      {/* Mobilna gornja traka */}
      <div className="fixed inset-x-0 top-0 z-20 flex items-center justify-between bg-ink px-4 py-3 text-white md:hidden">
        <div className="flex items-center gap-2 font-display font-semibold">
          <span className="flex h-7 w-7 items-center justify-center rounded bg-primary text-bronze-light">§</span>
          LegalRag
        </div>
        <nav className="flex gap-1" aria-label="Navigacija">
          {navItems.map(({ to, icon: Icon, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              aria-label={label}
              className={({ isActive }) =>
                `rounded p-2 ${isActive ? "bg-primary" : "text-white/70"}`
              }
            >
              <Icon size={18} />
            </NavLink>
          ))}
        </nav>
      </div>

      <main className="flex-1 px-4 pb-16 pt-16 md:ml-60 md:px-10 md:pt-8">
        <div className="mx-auto max-w-5xl">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
