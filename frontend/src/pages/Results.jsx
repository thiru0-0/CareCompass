import { useLocation, useNavigate } from "react-router-dom";
import HospitalCard from "../components/HospitalCard";
import CostBreakdown from "../components/CostBreakdown";
import ConfidenceBar from "../components/ConfidenceBar";

export default function Results() {
  const { state } = useLocation();
  const navigate  = useNavigate();

  if (!state?.estimate) {
    navigate("/");
    return null;
  }

  const { estimate, hospitals, query } = state;

  const budget = query?.budget || estimate?.budget;
  const maxCost = estimate?.total_range ? estimate.total_range[1] : 0;
  
  let coverageAmount = 0;
  let coverageSource = null;
  
  if (estimate.applicable_schemes?.length > 0) {
    const topScheme = estimate.applicable_schemes[0];
    if (topScheme.tier === 1) {
      coverageAmount = maxCost; // Assume full coverage up to 5L
      coverageSource = topScheme.name;
    } else if (topScheme.tier === 3 && topScheme.type === "Insurance") {
      coverageAmount = maxCost * 0.75; // Assume 75% coverage
      coverageSource = topScheme.name;
    } else if (topScheme.tier === 3) {
      coverageAmount = maxCost; 
      coverageSource = topScheme.name;
    }
  }

  const residualCost = Math.max(0, maxCost - coverageAmount);
  const financingGap = budget && residualCost > budget ? residualCost - budget : 0;

  const handlePreQualify = () => {
    alert("This would open the Poonawalla Fincorp Loan Pre-qualification flow with your profile pre-filled!");
  };

  const isDesperate = estimate?.financial_signals?.budget_sentiment === "desperate" || 
                      estimate?.financial_signals?.income_signal === "below_poverty";

const schemeUrls = {
    "Ayushman Bharat PMJAY": "https://pmjay.gov.in",
    "PMJAY": "https://pmjay.gov.in",
    "Ayushman": "https://pmjay.gov.in",
    "CGHS": "https://cghs.mohfw.gov.in",
    "ESI": "https://www.esic.nic.in",
    "Rashtriya Swasthya Bima Yojana": "https://www.rsby.gov.in",
    "Karunya": "https://karunya.arogyaservices.kerala.gov.in",
    "Madhya Pradesh": "https://www.shmpichaat.in",
    "Delhi": "https://health.delhigovt.nic.in",
    "Maharashtra": "https://aarogyamahaarogya.gov.in",
    "Karnataka": "https://arogyakarnataka.gov.in",
    "Tamil Nadu": "https://tnhealth.tn.gov.in",
};

  const getSchemeUrl = (name) => {
    for (const key in schemeUrls) {
      if (name.toLowerCase().includes(key.toLowerCase())) {
        return schemeUrls[key];
      }
    }
    return "https://pmjay.gov.in";
  };

  const schemesBlock = estimate.applicable_schemes?.length > 0 && (
    <section className="section schemes-section" style={{ borderLeftColor: isDesperate ? 'var(--danger)' : 'var(--success)' }}>
      <h3 className="section-title">🏛️ Available Financial Assistance</h3>
      <div className="schemes-list">
        {estimate.applicable_schemes.map((scheme, i) => (
          <div key={i} className={`scheme-card tier-${scheme.tier}`}>
            <div className="scheme-header">
              <span className="scheme-tier">Tier {scheme.tier}</span>
              <span className="scheme-type">{scheme.type}</span>
            </div>
            <h4 className="scheme-name">{scheme.name}</h4>
            <p className="scheme-desc">{scheme.description}</p>
            <button className="verify-btn" onClick={() => window.open(getSchemeUrl(scheme.name), "_blank")}>
              Verify Eligibility →
            </button>
          </div>
        ))}
      </div>
    </section>
  );

  if (estimate?.urgency === "emergency") {
    return (
      <div className="results-page emergency-override">
        <button className="back-btn" onClick={() => navigate(-1)}>← Back to search</button>
        <div className="emergency-banner">
          <h2>🚨 MEDICAL EMERGENCY DETECTED 🚨</h2>
          <p><strong>{estimate.urgency_reason}</strong></p>
          <p>This sounds like an emergency. Call 112 immediately or go to the nearest casualty ward. The hospitals below have 24/7 emergency departments within your area.</p>
        </div>
        
        <div className="results-grid">
          <div className="left-col" style={{ display: 'none' }}></div>
          <div className="right-col" style={{ width: '100%' }}>
            <section className="section">
              <h3 className="section-title">🏥 Nearest Emergency Departments</h3>
              <div className="hospital-list">
                {(hospitals || []).map((h, i) => (
                  <HospitalCard key={h.id} hospital={h} rank={i + 1} />
                ))}
              </div>
            </section>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="results-page">
      <button className="back-btn" onClick={() => navigate(-1)}>← Back to search</button>

      <div className="results-header">
        <h2 className="results-condition">{estimate.condition}</h2>
        <p className="results-procedure">Recommended: <strong>{estimate.procedure}</strong></p>
        <p className="results-location">📍 {estimate.city}</p>
      </div>

      <div className="results-grid">
        <div className="left-col">
          <section className="section">
            <h3 className="section-title">💰 Cost Estimate</h3>
            <CostBreakdown breakdown={estimate.breakdown} total={estimate.total_range} />
            <ConfidenceBar score={estimate.confidence_score} />
          </section>

          {estimate.risk_flags?.length > 0 && (
            <section className="section flags-section">
              <h3 className="section-title">⚠️ Risk Flags</h3>
              <ul className="flag-list">
                {estimate.risk_flags.map((f, i) => <li key={i}>{f}</li>)}
              </ul>
            </section>
          )}

          {estimate.notes?.length > 0 && (
            <section className="section">
              <h3 className="section-title">📝 Notes</h3>
              <ul className="note-list">
                {estimate.notes.map((n, i) => <li key={i}>{n}</li>)}
              </ul>
            </section>
          )}

<div className="disclaimer-box">
             🛡️ {estimate.disclaimer}
           </div>

          <button className="loan-btn" onClick={() => navigate("/loan", { state: { estimate, hospitals, query } })} style={{ marginTop: "16px", width: "100%" }}>
            🏦 Check Loan Eligibility & Schemes →
          </button>

           {isDesperate ? null : schemesBlock}

           {financingGap > 0 ? (
             <section className="section gap-section">
               <h3 className="section-title">💸 Financing Gap</h3>
               {coverageAmount > 0 ? (
                 <p>After your estimated <strong>{coverageSource}</strong> coverage, your residual cost is ₹{residualCost.toLocaleString()}. You may only need a loan for <strong>₹{financingGap.toLocaleString()}</strong>.</p>
               ) : (
                 <p>You may need <strong>₹{financingGap.toLocaleString()}</strong> in additional financing based on your stated budget of ₹{budget.toLocaleString()}.</p>
               )}
               <button className="loan-btn" onClick={() => navigate("/loan", { state: { estimate, hospitals, query } })}>
                 Check Loan Eligibility →
               </button>
             </section>
           ) : (
            <section className="section gap-section" style={{ borderLeftColor: 'var(--success)', background: '#f0fdf4' }}>
              <h3 className="section-title" style={{ color: 'var(--success)' }}>✅ Fully Covered</h3>
              {coverageAmount > 0 ? (
                <p>Based on your <strong>{coverageSource}</strong> coverage and budget, you do not need a loan for this procedure.</p>
              ) : (
                <p>Your declared budget covers the estimated cost of this procedure. No loan needed!</p>
              )}
            </section>
          )}
        </div>

        <div className="right-col">
          {isDesperate && schemesBlock}

          <section className="section">
            <h3 className="section-title">🏥 Recommended Hospitals</h3>
            <div className="hospital-list">
              {(hospitals || []).map((h, i) => (
                <HospitalCard key={h.id} hospital={h} rank={i + 1} />
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
