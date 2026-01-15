import { FormEvent, useCallback, useEffect, useState } from "react";

import { useAuth } from "../context/AuthContext";
import {
  addWhitelistUser,
  disableWhitelistUser,
  listWhitelist,
} from "../services/admin";
import type { User } from "../services/types";
import "../styles/admin.css";

export default function AdminUsers() {
  const { isAdmin } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [form, setForm] = useState({
    ldap_id: "",
    ssh_login: "",
    display_name: "",
    team_id: "",
    password: "",
  });

  const loadUsers = useCallback(async () => {
    setError(null);
    try {
      const data = await listWhitelist();
      setUsers(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load users";
      setError(message);
    }
  }, []);

  useEffect(() => {
    if (isAdmin) {
      loadUsers();
    }
  }, [isAdmin, loadUsers]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await addWhitelistUser({
        ldap_id: form.ldap_id.trim(),
        ssh_login: form.ssh_login.trim() || undefined,
        display_name: form.display_name.trim() || undefined,
        team_id: form.team_id.trim() || undefined,
        password: form.password.trim() || undefined,
      });
      setForm({ ldap_id: "", ssh_login: "", display_name: "", team_id: "", password: "" });
      await loadUsers();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to add user";
      setError(message);
    } finally {
      setBusy(false);
    }
  };

  const handleDisable = async (ldapId: string) => {
    setBusy(true);
    setError(null);
    try {
      await disableWhitelistUser(ldapId);
      await loadUsers();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Disable failed";
      setError(message);
    } finally {
      setBusy(false);
    }
  };

  if (!isAdmin) {
    return (
      <section className="admin-page">
        <h1 className="page-title">Admin Users</h1>
        <div className="empty-state">Admin access required.</div>
      </section>
    );
  }

  return (
    <section className="admin-page">
      <div className="admin-header">
        <div>
          <h1 className="page-title">Whitelist Management</h1>
          <p className="page-subtitle">Add, enable, or disable whitelist accounts.</p>
        </div>
        <button className="secondary-button" type="button" onClick={loadUsers}>
          Refresh
        </button>
      </div>

      {error ? <div className="form-error">{error}</div> : null}

      <div className="admin-grid">
        <form className="card admin-card" onSubmit={handleSubmit}>
          <h2>Add user</h2>
          <label>
            Account ID
            <input
              value={form.ldap_id}
              onChange={(event) => setForm({ ...form, ldap_id: event.target.value })}
              required
            />
          </label>
          <label>
            SSH Login
            <input
              value={form.ssh_login}
              onChange={(event) => setForm({ ...form, ssh_login: event.target.value })}
            />
          </label>
          <label>
            Display name
            <input
              value={form.display_name}
              onChange={(event) => setForm({ ...form, display_name: event.target.value })}
            />
          </label>
          <label>
            Team ID
            <input
              value={form.team_id}
              onChange={(event) => setForm({ ...form, team_id: event.target.value })}
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={form.password}
              onChange={(event) => setForm({ ...form, password: event.target.value })}
            />
          </label>
          <button className="primary-button" type="submit" disabled={busy}>
            {busy ? "Saving..." : "Add user"}
          </button>
        </form>

        <div className="card admin-card">
          <h2>Whitelisted users</h2>
          {users.length === 0 ? (
            <div className="empty-state">No users yet.</div>
          ) : (
            <div className="admin-list">
              {users.map((user) => (
                <div key={user.id} className="admin-item">
                  <div>
                    <strong>{user.ldap_id}</strong>
                    <div className="muted">{user.display_name || user.team_id || ""}</div>
                    <div className="muted">Status: {user.status}</div>
                  </div>
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={() => handleDisable(user.ldap_id)}
                    disabled={busy || user.status === "disabled"}
                  >
                    {user.status === "disabled" ? "Disabled" : "Disable"}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
