export default function ConfidenceBar({ score }) {
  const pct = Math.round(score * 100);
  const color = pct >= 70 ? "#22c55e" : pct >= 50 ? "#f59e0b" : "#ef4444";
  const label = pct >= 70 ? "High confidence" : pct >= 50 ? "Moderate confidence" : "Low confidence";
  return (
    <div className="confidence-bar">
      <div className="confidence-header">
        <span className="confidence-label">{label}</span>
        <span className="confidence-pct" style={{ color }}>{pct}%</span>
      </div>
      <div className="bar-track">
        <div className="bar-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <p className="confidence-note">Based on procedure data availability and comorbidity complexity</p>
    </div>
  );
}
