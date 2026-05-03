import { useState } from "react";

const INDIAN_CITIES = [
  { name: "Mumbai", state: "Maharashtra" },
  { name: "Delhi", state: "NCT" },
  { name: "New Delhi", state: "NCT" },
  { name: "Bangalore", state: "Karnataka" },
  { name: "Chennai", state: "Tamil Nadu" },
  { name: "Hyderabad", state: "Telangana" },
  { name: "Kolkata", state: "West Bengal" },
  { name: "Pune", state: "Maharashtra" },
  { name: "Ahmedabad", state: "Gujarat" },
  { name: "Nagpur", state: "Maharashtra" },
  { name: "Jaipur", state: "Rajasthan" },
  { name: "Lucknow", state: "Uttar Pradesh" },
  { name: "Chandigarh", state: "Chandigarh" },
  { name: "Kochi", state: "Kerala" },
  { name: "Visakhapatnam", state: "Andhra Pradesh" },
  { name: "Bhopal", state: "Madhya Pradesh" },
  { name: "Indore", state: "Madhya Pradesh" },
  { name: "Gurgaon", state: "Haryana" },
  { name: "Noida", state: "Uttar Pradesh" },
  { name: "Mysore", state: "Karnataka" },
  { name: "Surat", state: "Gujarat" },
  { name: "Vadodara", state: "Gujarat" },
  { name: "Coimbatore", state: "Tamil Nadu" },
  { name: "Madurai", state: "Tamil Nadu" },
  { name: "Tiruchirappalli", state: "Tamil Nadu" },
  { name: "Guwahati", state: "Assam" },
  { name: "Bhubaneswar", state: "Odisha" },
  { name: "Ranchi", state: "Jharkhand" },
  { name: "Dehradun", state: "Uttarakhand" },
  { name: "Jammu", state: "Jammu & Kashmir" },
];

const SUGGESTIONS = [
  "Knee replacement surgery near Chennai under ₹3 lakh",
  "Angioplasty hospital in Nagpur, I have diabetes",
  "Cataract surgery near Mumbai, budget friendly",
  "Bypass surgery Bangalore, age 65",
];

export default function ChatInterface({ onSubmit, loading }) {
  const [text, setText] = useState("");
  const [location, setLocation] = useState("");
  const [age, setAge] = useState("");
  const [comorbidities, setComorbidities] = useState("");
  const [budget, setBudget] = useState("");
  const [showCityDropdown, setShowCityDropdown] = useState(false);
  const [citySearch, setCitySearch] = useState("");

  const filteredCities = INDIAN_CITIES.filter(city => 
    city.name.toLowerCase().includes(citySearch.toLowerCase()) ||
    city.state.toLowerCase().includes(citySearch.toLowerCase())
  ).slice(0, 8);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    onSubmit({
      text,
      location: location || undefined,
      age: age ? parseInt(age) : undefined,
      comorbidities: comorbidities ? comorbidities.split(",").map(s => s.trim()) : [],
      budget: budget ? parseInt(budget) * 100 : undefined,
    });
  };

  const selectCity = (cityName) => {
    setLocation(cityName);
    setShowCityDropdown(false);
    setCitySearch("");
  };

  return (
    <div className="chat-interface">
      <form onSubmit={handleSubmit} className="query-form">
        <div className="main-input-wrap">
          <textarea
            className="main-input"
            placeholder="Describe your condition or procedure... e.g. 'knee replacement near Nagpur under 3 lakh'"
            value={text}
            onChange={e => setText(e.target.value)}
            rows={3}
          />
        </div>

        <div className="optional-fields">
          <div className="city-select-wrapper">
            <input 
              className="opt-input city-input" 
              placeholder="Select City (optional)"
              value={location}
              onChange={e => {
                setLocation(e.target.value);
                setCitySearch(e.target.value);
                setShowCityDropdown(true);
              }}
              onFocus={() => setShowCityDropdown(true)}
              onBlur={() => setTimeout(() => setShowCityDropdown(false), 200)}
            />
            {showCityDropdown && citySearch && (
              <div className="city-dropdown">
                {filteredCities.map((city, idx) => (
                  <div 
                    key={idx} 
                    className="city-option"
                    onClick={() => selectCity(city.name)}
                  >
                    <span className="city-name">{city.name}</span>
                    <span className="city-state">{city.state}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
          <input className="opt-input" placeholder="Age (optional)" type="number" value={age} onChange={e => setAge(e.target.value)} />
          <input className="opt-input" placeholder="Conditions (e.g. diabetes, hypertension)" value={comorbidities} onChange={e => setComorbidities(e.target.value)} />
          <input className="opt-input" placeholder="Max budget (₹ in thousands, e.g. 300)" type="number" value={budget} onChange={e => setBudget(e.target.value)} />
        </div>

        <button className="submit-btn" type="submit" disabled={loading || !text.trim()}>
          {loading ? <span className="spinner" /> : "🔍 Find Hospitals & Estimate Cost"}
        </button>
      </form>

      <div className="suggestions">
        <p className="suggestions-label">Try these examples:</p>
        <div className="suggestion-chips">
          {SUGGESTIONS.map((s, i) => (
            <button key={i} className="chip" onClick={() => setText(s)}>{s}</button>
          ))}
        </div>
      </div>
    </div>
  );
}
