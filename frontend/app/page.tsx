import Link from "next/link";
import { ArrowRight, Clock, Radar, ShieldAlert } from "lucide-react";
import { getHistory } from "@/lib/api";
import { RiskGauge } from "@/components/RiskGauge";

export default async function DashboardPage() {
  const history = await getHistory();
  const latest = history[0];
  const completed = history.filter((item) => item.status === "completed");
  const averageScore = completed.length
    ? Math.round(completed.reduce((sum, item) => sum + item.score, 0) / completed.length)
    : 0;
  const openFindings = history.reduce((sum, item) => sum + item.findings_count, 0);

  return (
    <div className="stack">
      <section className="page-heading">
        <div>
          <p className="eyebrow">AI Pentest Assistant</p>
          <h1>Security scan boshqaruvi</h1>
        </div>
        <Link className="primary-button" href="/scan/new">
          <Radar aria-hidden="true" />
          <span>New scan</span>
        </Link>
      </section>

      <section className="overview-grid">
        <RiskGauge score={averageScore} />
        <div className="metric">
          <span>Scans</span>
          <strong>{history.length}</strong>
        </div>
        <div className="metric">
          <span>Findings</span>
          <strong>{openFindings}</strong>
        </div>
        <div className="metric">
          <span>Last status</span>
          <strong>{latest?.status ?? "none"}</strong>
        </div>
      </section>

      <section className="split-layout">
        <div>
          <div className="section-title">
            <h2>Oxirgi scanlar</h2>
            <Clock aria-hidden="true" />
          </div>
          <div className="history-list">
            {history.slice(0, 6).map((item) => (
              <Link className="history-row" href={`/scan/${item.id}`} key={item.id}>
                <span>{item.target}</span>
                <strong>{item.score}</strong>
                <ArrowRight aria-hidden="true" />
              </Link>
            ))}
            {history.length === 0 && <p className="muted">Hali scanlar mavjud emas.</p>}
          </div>
        </div>
        <div>
          <div className="section-title">
            <h2>Priority</h2>
            <ShieldAlert aria-hidden="true" />
          </div>
          <p className="analysis-text">
            Internetga ochiq DB, Redis, Elasticsearch, Telnet va sertifikat muammolari yuqori ustuvorlikda ko'riladi.
            Header hardening masalalari risk scorega qo'shiladi va hisobotda remediation bilan chiqadi.
          </p>
        </div>
      </section>
    </div>
  );
}

