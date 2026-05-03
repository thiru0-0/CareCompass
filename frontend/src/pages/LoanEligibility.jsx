import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

export default function LoanEligibility() {
  const { state } = useLocation();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    monthlyIncome: "",
    employment: "",
    hasInsurance: "",
    creditScore: "",
  });
  const [results, setResults] = useState(null);

  if (!state?.estimate) {
    navigate("/");
    return null;
  }

  const { estimate, query } = state;
  
  // Use budget gap that's already calculated
  const costFromEstimate = estimate?.total_range ? estimate.total_range[1] : 0;
  const costFromHospitals = state?.hospitals && state.hospitals.length > 0 
    ? state.hospitals[0]?.estimated_cost_range?.[1] || 0 
    : 0;
  const treatmentCost = Math.max(costFromEstimate, costFromHospitals);
  const userBudget = query?.budget || 0;
  const budgetGap = treatmentCost > userBudget ? treatmentCost - userBudget : 0;

  // Quick 4-field form
  const handleCheckEligibility = async () => {
    const income = parseInt(formData.monthlyIncome) || 0;
    const annualIncome = income * 12;
    const employment = formData.employment;
    const hasInsurance = formData.hasInsurance === "yes";
    const creditScore = parseInt(formData.creditScore) || 0;
    
    const options = [];
    
    // 1. Government Schemes (Purple - Purple theme)
    if (annualIncome < 300000) {
      options.push({
        category: "government",
        name: "Ayushman Bharat PMJAY",
        maxAmount: 500000,
        confidence: 85,
        speed: "Slow (1-7 days)",
        docs: ["Aadhaar Card", "Ration Card", "Income Certificate"],
        url: "https://pmjay.gov.in",
        description: "Free coverage for families earning below ₹3L/year"
      });
    }
    if (employment === "government") {
      options.push({
        category: "government",
        name: "CGHS",
        maxAmount: treatmentCost,
        confidence: 90,
        speed: "Fast (1-2 days)",
        docs: ["CGHS Card", "ID Proof"],
        url: "https://cghs.mohfw.gov.in",
        description: "Government employee health scheme"
      });
    }
    if (employment === "salaried" || employment === "self-employed") {
      options.push({
        category: "government",
        name: "Ayushman CAPF",
        maxAmount: 500000,
        confidence: 75,
        speed: "Slow (3-5 days)",
        docs: ["Service ID", "Aadhaar"],
        url: "https://pmjay.gov.in",
        description: "For armed forces and paramilitary"
      });
    }
    
    // 2. Medical Loans (Teal)
    if ((employment === "salaried" || employment === "self-employed") && 
        (!creditScore || creditScore > 650)) {
      const maxLoan = Math.min(budgetGap * 1.2, annualIncome * 4);
      options.push({
        category: "loan",
        name: "Health Loan",
        maxAmount: maxLoan,
        confidence: creditScore > 750 ? 90 : 75,
        speed: "Fast (1-3 days)",
        docs: ["ID Proof", "Income Proof", "Bank Statement"],
        url: "https://www.bankbazaar.com/personal-loan/health-insurance-loan.html",
        description: `Loan at ${creditScore > 750 ? "10.5" : "12.5"}% interest`
      });
    }
    
    // 3. Insurance (Teal)
    if (!hasInsurance) {
      options.push({
        category: "insurance",
        name: "Health Insurance",
        maxAmount: budgetGap,
        confidence: 60,
        speed: "Medium (3-7 days)",
        docs: ["ID Proof", "Medical Reports", "Income Proof"],
        url: "https://www.policybazaar.com/health-insurance/",
        description: "Quick health insurance for coverage"
      });
    }
    
    // 4. NGO Funds (Purple)
    if (annualIncome < 200000) {
      options.push({
        category: "ngo",
        name: "PM Relief Fund",
        maxAmount: Math.min(100000, budgetGap),
        confidence: 50,
        speed: "Slow (5-14 days)",
        docs: ["ID Proof", "Income Proof", "Medical Documents"],
        url: "https://pmrelieffund.nic.in",
        description: "Government relief for medical emergencies"
      });
      options.push({
        category: "ngo",
        name: "State Illness Fund",
        maxAmount: Math.min(150000, budgetGap),
        confidence: 45,
        speed: "Slow (7-21 days)",
        docs: ["Residence Proof", "Income Proof", "Medical Certificate"],
        url: "https://nha.gov.in",
        description: "State-specific medical assistance"
      });
    }
    
    // Rank by: speed, coverage, ease
    const ranked = options.map(opt => {
      const covered = opt.maxAmount >= budgetGap ? 100 : (opt.maxAmount / budgetGap * 100);
      const speedScore = opt.speed.includes("Fast") ? 30 : opt.speed.includes("Medium") ? 20 : 10;
      const docsScore = (5 - opt.docs.length) * 10;
      opt.rankScore = covered * 0.4 + speedScore + docsScore + opt.confidence * 0.2;
      return opt;
    }).sort((a, b) => b.rankScore - a.rankScore);
    
    setResults(ranked);
  };

  // Group by category for display
  const purpleOptions = results?.filter(r => r.category === "government" || r.category === "ngo") || [];
  const tealOptions = results?.filter(r => r.category === "loan" || r.category === "insurance") || [];

  return (
    <div className="loan-page">
      <button className="back-btn" onClick={() => navigate(-1)}>← Back to results</button>
      
      <div className="loan-header">
        <h1>💰 Financial Options for Your Treatment</h1>
        <p>Based on your budget gap of <strong>₹{budgetGap.toLocaleString()}</strong></p>
      </div>

      {!results ? (
        <div className="quick-form">
          <div className="form-card">
            <h3>🖊️ Quick Profile (4 fields only)</h3>
            
            <div className="form-group">
              <label>Monthly Income (₹)</label>
              <input 
                type="number" 
                placeholder="e.g. 25000"
                value={formData.monthlyIncome}
                onChange={e => setFormData({...formData, monthlyIncome: e.target.value})}
              />
            </div>

            <div className="form-group">
              <label>Employment Type</label>
              <select 
                value={formData.employment}
                onChange={e => setFormData({...formData, employment: e.target.value})}
              >
                <option value="">Select...</option>
                <option value="salaried">Salaried Employee</option>
                <option value="self-employed">Self-Employed / Business</option>
                <option value="government">Government Employee</option>
                <option value="farmer">Farmer</option>
                <option value="unemployed">Unemployed</option>
                <option value="retired">Pensioner / Retired</option>
              </select>
            </div>

            <div className="form-group">
              <label>Have Health Insurance?</label>
              <select 
                value={formData.hasInsurance}
                onChange={e => setFormData({...formData, hasInsurance: e.target.value})}
              >
                <option value="">Select...</option>
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
            </div>

            <div className="form-group">
              <label>CIBIL Credit Score (optional)</label>
              <input 
                type="number" 
                placeholder="e.g. 750"
                value={formData.creditScore}
                onChange={e => setFormData({...formData, creditScore: e.target.value})}
              />
            </div>

            <button 
              className="check-btn" 
              onClick={handleCheckEligibility}
              disabled={!formData.monthlyIncome || !formData.employment}
            >
              ✨ Find My Options
            </button>
          </div>
        </div>
      ) : (
        <div className="results-section">
          <button className="back-link" onClick={() => setResults(null)}>
            ← Start Over
          </button>
          
          {purpleOptions.length > 0 && (
            <div className="options-group purple">
              <h3>🟣 Government & NGO Options (No repayment needed)</h3>
              {purpleOptions.map((opt, i) => (
                <ResultCard key={i} option={opt} budgetGap={budgetGap} />
              ))}
            </div>
          )}
          
          {tealOptions.length > 0 && (
            <div className="options-group teal">
              <h3>🔵 Loans & Insurance (Fast approval)</h3>
              {tealOptions.map((opt, i) => (
                <ResultCard key={i} option={opt} budgetGap={budgetGap} />
              ))}
            </div>
          )}
          
          {purpleOptions.length === 0 && tealOptions.length === 0 && (
            <div className="no-results">
              <p>😔 No options found. Try increasing your budget or check with a co-applicant.</p>
              <button className="check-btn" onClick={() => setResults(null)}>
                ↺ Try Different Profile
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ResultCard({ option, budgetGap }) {
  const covered = option.maxAmount >= budgetGap;
  
  return (
    <div className={`result-card ${covered ? "covers-gap" : ""}`}>
      <div className="result-header">
        <h4>{option.name}</h4>
        <span className="confidence">{option.confidence}% likely to qualify</span>
      </div>
      
      <p className="result-desc">{option.description}</p>
      
      <div className="result-details">
        <div className="detail">
          <span className="label">Max Amount</span>
          <span className="value">₹{option.maxAmount.toLocaleString()}</span>
        </div>
        <div className="detail">
          <span className="label">Speed</span>
          <span className="value">{option.speed}</span>
        </div>
        <div className="detail">
          <span className="label">Covers Gap?</span>
          <span className={`value ${covered ? "yes" : "no"}`}>
            {covered ? "✓ Yes" : "Partial"}
          </span>
        </div>
      </div>
      
      <div className="docs-needed">
        <span className="docs-label">📋 Documents needed:</span>
        <span className="docs-list">{option.docs.join(", ")}</span>
      </div>
      
      <div className="result-actions">
        <button className="apply-btn" onClick={() => window.open(option.url, "_blank")}>
          Apply Now →
        </button>
        <button className="docs-btn" onClick={() => {
          const text = `${option.name}\n\nDocuments needed:\n${option.docs.join("\n")}`;
          navigator.clipboard.writeText(text);
          alert("Documents list copied to clipboard!");
        }}>
          📋 Copy Checklist
        </button>
      </div>
    </div>
  );
}