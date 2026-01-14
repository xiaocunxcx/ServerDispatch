import { ReactNode } from "react";
import { NavLink } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import "../styles/shell.css";

const navItems = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/reservations", label: "Reservations" },
  { to: "/profile", label: "Profile" },
  { to: "/admin/users", label: "Admin Users", admin: true },
  { to: "/admin/servers", label: "Admin Servers", admin: true },
  { to: "/admin/audit", label: "Audit Logs", admin: true },
];

interface AppShellProps {
  children: ReactNode;
}

export default function AppShell({ children }: AppShellProps) {
  const { user, logout, isAdmin } = useAuth();
  const visibleNav = navItems.filter((item) => !item.admin || isAdmin);

  return (
    <div className="app-shell">
      <aside className="side-panel">
        <div className="brand">
          <span className="brand-kicker">ServerDispatch</span>
          <span className="brand-title">NPU Control Surface</span>
        </div>
        <nav className="nav-links">
          {visibleNav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `nav-link${isActive ? " nav-link-active" : ""}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main-panel">
        <header className="top-bar">
          <div className="top-bar-title">
            <span className="top-bar-kicker">Operations</span>
            <span className="top-bar-sub">Resource Control Center</span>
          </div>
          <div className="top-bar-actions">
            {user ? (
              <div className="user-chip">
                <span>{user.ldap_id}</span>
                <span className="user-meta">{user.display_name || user.team_id || ""}</span>
              </div>
            ) : null}
            <button className="secondary-button" type="button" onClick={logout}>
              Sign out
            </button>
          </div>
        </header>
        <div className="content-wrap">{children}</div>
      </main>
    </div>
  );
}
