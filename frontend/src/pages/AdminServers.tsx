import { FormEvent, useCallback, useEffect, useState } from "react";

import { useAuth } from "../context/AuthContext";
import { addServer, discoverServer, listServers } from "../services/servers";
import type { Server } from "../services/types";
import "../styles/admin.css";

export default function AdminServers() {
  const { isAdmin } = useAuth();
  const [servers, setServers] = useState<Server[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [form, setForm] = useState({
    ip: "",
    access_account: "",
    hostname: "",
    model: "",
    card_count: "",
  });

  const loadServers = useCallback(async () => {
    setError(null);
    try {
      const data = await listServers();
      setServers(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load servers";
      setError(message);
    }
  }, []);

  useEffect(() => {
    if (isAdmin) {
      loadServers();
    }
  }, [isAdmin, loadServers]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await addServer({
        ip: form.ip.trim(),
        access_account: form.access_account.trim(),
        hostname: form.hostname.trim() || undefined,
        model: form.model.trim() || undefined,
        card_count: form.card_count ? Number(form.card_count) : undefined,
      });
      setForm({ ip: "", access_account: "", hostname: "", model: "", card_count: "" });
      await loadServers();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to add server";
      setError(message);
    } finally {
      setBusy(false);
    }
  };

  const handleDiscover = async (serverId: string) => {
    setBusy(true);
    setError(null);
    try {
      await discoverServer(serverId);
      await loadServers();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Discovery failed";
      setError(message);
    } finally {
      setBusy(false);
    }
  };

  if (!isAdmin) {
    return (
      <section className="admin-page">
        <h1 className="page-title">Admin Servers</h1>
        <div className="empty-state">Admin access required.</div>
      </section>
    );
  }

  return (
    <section className="admin-page">
      <div className="admin-header">
        <div>
          <h1 className="page-title">Server Registry</h1>
          <p className="page-subtitle">Register and discover NPU hosts.</p>
        </div>
        <button className="secondary-button" type="button" onClick={loadServers}>
          Refresh
        </button>
      </div>

      {error ? <div className="form-error">{error}</div> : null}

      <div className="admin-grid">
        <form className="card admin-card" onSubmit={handleSubmit}>
          <h2>Add server</h2>
          <label>
            IP address
            <input
              value={form.ip}
              onChange={(event) => setForm({ ...form, ip: event.target.value })}
              required
            />
          </label>
          <label>
            Access account
            <input
              value={form.access_account}
              onChange={(event) => setForm({ ...form, access_account: event.target.value })}
              required
            />
          </label>
          <label>
            Hostname
            <input
              value={form.hostname}
              onChange={(event) => setForm({ ...form, hostname: event.target.value })}
            />
          </label>
          <label>
            Model
            <input
              value={form.model}
              onChange={(event) => setForm({ ...form, model: event.target.value })}
            />
          </label>
          <label>
            Card count
            <input
              type="number"
              min="1"
              value={form.card_count}
              onChange={(event) => setForm({ ...form, card_count: event.target.value })}
            />
          </label>
          <button className="primary-button" type="submit" disabled={busy}>
            {busy ? "Saving..." : "Add server"}
          </button>
        </form>

        <div className="card admin-card">
          <h2>Registered servers</h2>
          {servers.length === 0 ? (
            <div className="empty-state">No servers yet.</div>
          ) : (
            <div className="admin-list">
              {servers.map((server) => (
                <div key={server.id} className="admin-item">
                  <div>
                    <strong>{server.hostname || server.ip}</strong>
                    <div className="muted">{server.ip}</div>
                    <div className="muted">Status: {server.status}</div>
                    <div className="muted">Cards: {server.card_count ?? "n/a"}</div>
                  </div>
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={() => handleDiscover(server.id)}
                    disabled={busy}
                  >
                    Discover
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
