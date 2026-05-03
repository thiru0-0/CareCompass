function fmt(n) {
  if (n >= 100000) return `₹${(n/100000).toFixed(1)}L`;
  if (n >= 1000)   return `₹${(n/1000).toFixed(0)}K`;
  return `₹${n}`;
}
const TIER_COLOR = { premium: "#8b5cf6", mid: "#3b82f6", budget: "#22c55e" };

export default function HospitalCard({ hospital, rank }) {
  const { name, city, tier, rating, review_count, nabh_accredited, distance_km, estimated_cost_range, strengths, warnings, score } = hospital;
  return (
    <div className="hospital-card">
      <div className="card-header">
        <div className="rank-badge">#{rank}</div>
        <div className="hospital-info">
          <h3 className="hospital-name">{name}</h3>
          <p className="hospital-city">📍 {city}{distance_km > 0 ? ` · ${distance_km} km away` : ""}</p>
        </div>
        <div className="tier-badge" style={{ background: TIER_COLOR[tier] }}>
          {tier.charAt(0).toUpperCase() + tier.slice(1)}
        </div>
      </div>

      <div className="card-metrics">
        <div className="metric">
          <span className="metric-value">⭐ {rating}</span>
          <span className="metric-label">{review_count.toLocaleString()} reviews</span>
        </div>
        {nabh_accredited && <div className="nabh-badge">✓ NABH</div>}
        <div className="metric">
          <span className="metric-value">{fmt(estimated_cost_range[0])}–{fmt(estimated_cost_range[1])}</span>
          <span className="metric-label">Est. cost range</span>
        </div>
        <div className="metric">
          <span className="metric-value">{Math.round(score * 100)}</span>
          <span className="metric-label">Match score</span>
        </div>
      </div>

      {strengths.length > 0 && (
        <div className="card-strengths">
          {strengths.map((s,i) => <span key={i} className="strength-tag">✓ {s}</span>)}
        </div>
      )}
      {warnings.length > 0 && (
        <div className="card-warnings">
          {warnings.map((w,i) => <span key={i} className="warning-tag">⚠ {w}</span>)}
        </div>
      )}
    </div>
  );
}
