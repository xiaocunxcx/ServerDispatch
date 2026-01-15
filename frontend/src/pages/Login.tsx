import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import "../styles/login.css";

export default function Login() {
  const { login, token } = useAuth();
  const navigate = useNavigate();
  const [ldapId, setLdapId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (token) {
      navigate("/dashboard", { replace: true });
    }
  }, [token, navigate]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await login(ldapId, password);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Login failed";
      setError(message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="login-page">
      <section className="login-card card fade-up">
        <span className="login-kicker">Secure Access</span>
        <h1 className="page-title">Sign in to the NPU Platform</h1>
        <p className="page-subtitle">
          Use your account credentials to access reservations, telemetry, and admin
          controls.
        </p>
        <form className="login-form" onSubmit={handleSubmit}>
          <label>
            Account ID
            <input
              type="text"
              placeholder="account.id"
              value={ldapId}
              onChange={(event) => setLdapId(event.target.value)}
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              placeholder="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          {error ? <div className="form-error">{error}</div> : null}
          <button
            className="primary-button"
            type="submit"
            disabled={busy || !ldapId || !password}
          >
            {busy ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </section>
    </div>
  );
}
