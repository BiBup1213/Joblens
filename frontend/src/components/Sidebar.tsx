import { FileText, LayoutDashboard, Settings, UserRound } from "lucide-react";

const navItems = [
  { label: "Dashboard", icon: LayoutDashboard, active: true },
  { label: "Profil", icon: UserRound },
  { label: "Dokumente", icon: FileText },
  { label: "Einstellungen", icon: Settings },
];

export function Sidebar() {
  return (
    <aside className="sidebar" aria-label="Hauptnavigation">
      <div className="brand">
        <div className="brand-mark" aria-hidden="true">
          <span />
        </div>
        <span className="brand-text">
          Job<span>Lens</span>
        </span>
      </div>

      <nav className="nav-list">
        {navItems.map((item) => {
          const Icon = item.icon;

          return (
            <button
              className={`nav-item${item.active ? " is-active" : ""}`}
              key={item.label}
              type="button"
            >
              <Icon aria-hidden="true" size={23} />
              {item.label}
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
