import { FormEvent, useState } from "react";

import { useAuth } from "../context/AuthContext";
import { updateSshKey } from "../services/user";
import "../styles/profile.css";

export default function Profile() {
  const { user, hasSshKey, markSshKey, refresh } = useAuth();
  const [sshKey, setSshKey] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (!user) {
    return null;
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setMessage(null);
    setBusy(true);
    try {
      await updateSshKey(sshKey.trim());
      markSshKey(true);
      await refresh();
      setMessage("SSH key updated. Reservation access is now enabled.");
      setSshKey("");
    } catch (err) {
      const messageText = err instanceof Error ? err.message : "Update failed";
      setError(messageText);
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="profile-page">
      <div className="profile-header">
        <div>
          <h1 className="page-title">Profile & SSH Access</h1>
          <p className="page-subtitle">
            Keep your SSH public key up to date to unlock reservation access.
          </p>
        </div>
        <div className={`status-pill ${hasSshKey ? "ok" : "warn"}`}>
          {hasSshKey ? "SSH key on file" : "SSH key missing"}
        </div>
      </div>

      <div className="profile-grid">
        <div className="card profile-card">
          <h2>Account</h2>
          <div className="profile-meta">
            <div>
              <span>Account ID</span>
              <strong>{user.ldap_id}</strong>
            </div>
            <div>
              <span>SSH Login</span>
              <strong>{user.ssh_login}</strong>
            </div>
            <div>
              <span>Team</span>
              <strong>{user.team_id || "Unassigned"}</strong>
            </div>
            <div>
              <span>Status</span>
              <strong>{user.status}</strong>
            </div>
          </div>
        </div>

        <form className="card profile-card" onSubmit={handleSubmit}>
          <h2>Update SSH Public Key</h2>
          <label>
            Public Key
            <textarea
              rows={5}
              placeholder="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA..."
              value={sshKey}
              onChange={(event) => setSshKey(event.target.value)}
              required
            />
          </label>
          {error ? <div className="form-error">{error}</div> : null}
          {message ? <div className="form-success">{message}</div> : null}
          <button className="primary-button" type="submit" disabled={busy}>
            {busy ? "Updating..." : "Save SSH key"}
          </button>
          <p className="profile-note">
            Changes apply immediately. Reservations are blocked until a key is on
            file.
          </p>
        </form>
      </div>
    </section>
  );
}
