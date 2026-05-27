export function riskLabel(score: number): string {
  if (score <= 25) return "Xavfsiz";
  if (score <= 50) return "O'rtacha";
  if (score <= 75) return "Yuqori";
  return "Kritik";
}

export function RiskGauge({ score }: { score: number }) {
  const bounded = Math.max(0, Math.min(score, 100));
  return (
    <div className="risk-gauge" aria-label={`Risk score ${bounded}`}>
      <div className="risk-ring" style={{ "--score": `${bounded}%` } as React.CSSProperties}>
        <strong>{bounded}</strong>
        <span>/100</span>
      </div>
      <div>
        <p className="eyebrow">Risk score</p>
        <h2>{riskLabel(bounded)}</h2>
      </div>
    </div>
  );
}

