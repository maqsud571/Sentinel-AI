import Link from "next/link";
import { Activity, History, Radar, ShieldCheck } from "lucide-react";

const nav = [
  { href: "/", label: "Dashboard", icon: Activity },
  { href: "/scan/new", label: "New Scan", icon: Radar },
  { href: "/history", label: "History", icon: History },
];

export function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-frame">
      <aside className="sidebar">
        <Link className="brand" href="/">
          <ShieldCheck aria-hidden="true" />
          <span>Sentinel AI</span>
        </Link>
        <nav className="nav-list" aria-label="Main navigation">
          {nav.map((item) => {
            const Icon = item.icon;
            return (
              <Link key={item.href} className="nav-link" href={item.href}>
                <Icon aria-hidden="true" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>
      <main className="main-surface">{children}</main>
    </div>
  );
}

