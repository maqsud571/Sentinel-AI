"use client";

import { useEffect, useMemo, useState } from "react";
import { Download, RefreshCw } from "lucide-react";
import { getScanResult, reportUrl, type Finding, type ScanResult } from "@/lib/api";
import { RiskGauge } from "@/components/RiskGauge";
import { SeverityBadge } from "@/components/SeverityBadge";

const activeStatuses = new Set(["queued", "running", "analyzing"]);

export function ScanResultView({ id }: { id: string }) {
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;

    async function load() {
      try {
        const data = await getScanResult(id);
        if (cancelled) return;
        setResult(data);
        if (activeStatuses.has(data.status)) {
          timer = setTimeout(load, 2500);
        }
      } catch (exc) {
        if (!cancelled) setError(exc instanceof Error ? exc.message : "Natija kelmadi.");
      }
    }

    load();
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [id]);

  const severityCounts = useMemo(() => countSeverities(result?.findings ?? []), [result]);

  if (error) return <p className="error-line">{error}</p>;
  if (!result) return <p className="muted">Natija yuklanmoqda...</p>;

  return (
    <div className="stack">
      <section className="result-header">
        <div>
          <p className="eyebrow">{result.status}</p>
          <h1>{result.normalized_target}</h1>
        </div>
        <div className="header-actions">
          {activeStatuses.has(result.status) && <RefreshCw className="spin status-icon" aria-hidden="true" />}
          {result.status === "completed" && (
            <a className="secondary-button" href={reportUrl(result.id)}>
              <Download aria-hidden="true" />
              <span>PDF</span>
            </a>
          )}
        </div>
      </section>

      {result.error && <p className="error-line">{result.error}</p>}

      <section className="overview-grid">
        <RiskGauge score={result.score} />
        {(["Critical", "High", "Medium", "Low"] as const).map((severity) => (
          <div className="metric" key={severity}>
            <span>{severity}</span>
            <strong>{severityCounts[severity] ?? 0}</strong>
          </div>
        ))}
      </section>

      <section>
        <div className="section-title">
          <h2>AI tahlil</h2>
        </div>
        <p className="analysis-text">{result.summary ?? "Scan yakunlangach AI xulosa shu yerda ko'rinadi."}</p>
      </section>

      <section>
        <div className="section-title">
          <h2>Topilmalar</h2>
          <span>{result.findings.length}</span>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Severity</th>
                <th>Category</th>
                <th>Topilma</th>
                <th>Dalil</th>
                <th>Tavsiya</th>
              </tr>
            </thead>
            <tbody>
              {result.findings.map((finding) => (
                <tr key={finding.id}>
                  <td>
                    <SeverityBadge severity={finding.severity} />
                  </td>
                  <td>{finding.category}</td>
                  <td>{finding.title}</td>
                  <td>{finding.evidence}</td>
                  <td>{finding.recommendation}</td>
                </tr>
              ))}
              {result.findings.length === 0 && (
                <tr>
                  <td colSpan={5}>Hali topilma yo'q.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function countSeverities(findings: Finding[]) {
  return findings.reduce<Record<string, number>>((acc, finding) => {
    acc[finding.severity] = (acc[finding.severity] ?? 0) + 1;
    return acc;
  }, {});
}

