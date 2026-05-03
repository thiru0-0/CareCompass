function fmt(n) {
  if (n >= 100000) return `₹${(n/100000).toFixed(1)}L`;
  if (n >= 1000)   return `₹${(n/1000).toFixed(0)}K`;
  return `₹${n}`;
}
const LABELS = {
  procedure: "Procedure / Surgery",
  consultation: "Doctor Consultation",
  hospital_stay: "Hospital Stay",
  diagnostics: "Diagnostics & Tests",
  medicines: "Medicines & Consumables",
  contingency: "Contingency Buffer",
};
const ICONS = { procedure:"🔬", consultation:"👨‍⚕️", hospital_stay:"🏥", diagnostics:"📋", medicines:"💊", contingency:"🛡️" };

export default function CostBreakdown({ breakdown, total }) {
  return (
    <div className="cost-breakdown">
      <div className="total-range">
        <span className="total-label">Total Estimated Cost</span>
        <span className="total-value">{fmt(total[0])} – {fmt(total[1])}</span>
      </div>
      <div className="breakdown-list">
        {Object.entries(breakdown).map(([key, [low, high]]) => (
          <div key={key} className="breakdown-row">
            <span className="breakdown-icon">{ICONS[key]}</span>
            <span className="breakdown-name">{LABELS[key] || key}</span>
            <span className="breakdown-range">{fmt(low)} – {fmt(high)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
