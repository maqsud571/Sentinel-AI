"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Play } from "lucide-react";
import { API_BASE } from "@/lib/api";

export function NewScanForm() {
  const router = useRouter();
  const [target, setTarget] = useState("");
  const [authorized, setAuthorized] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target, authorized }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail ?? "Scan yaratilmadi.");
      }
      router.push(`/scan/${data.id}`);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "Noma'lum xatolik.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="form-panel" onSubmit={submit}>
      <label className="field">
        <span>Target</span>
        <input
          required
          minLength={3}
          maxLength={255}
          placeholder="example.com yoki 192.0.2.10"
          value={target}
          onChange={(event) => setTarget(event.target.value)}
        />
      </label>
      <label className="check-row">
        <input type="checkbox" checked={authorized} onChange={(event) => setAuthorized(event.target.checked)} />
        <span>Men ushbu targetni skan qilishga egaman yoki yozma ruxsatim bor.</span>
      </label>
      {error && <p className="error-line">{error}</p>}
      <button className="primary-button" disabled={loading || !authorized} type="submit">
        {loading ? <Loader2 className="spin" aria-hidden="true" /> : <Play aria-hidden="true" />}
        <span>Scan boshlash</span>
      </button>
    </form>
  );
}

