import { useState, useRef, useEffect } from "react";
import ChatInterface from "../components/ChatInterface";
import { useNavigate } from "react-router-dom";
import { getFullEstimate, getRankedHospitals, parseQuery } from "../services/api";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState(null);
  const navigate = useNavigate();

  const [clarificationQuestion, setClarificationQuestion] = useState(null);
  const [clarificationTurns, setClarificationTurns] = useState(0);
  const [chatLog, setChatLog] = useState([]);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const clarifyInputRef = useRef(null);

  useEffect(() => {
    if (clarificationQuestion && clarifyInputRef.current) {
      clarifyInputRef.current.focus();
    }
  }, [clarificationQuestion]);

  const handleSubmit = async (payload) => {
    setLoading(true);
    setError(null);
    try {
      const parsed = await parseQuery(payload);
      
      if (parsed.flags?.needs_clarification && clarificationTurns < 3) {
        setClarificationQuestion(parsed.flags.clarification_question);
        setClarificationTurns(prev => prev + 1);
        setChatLog(prev => [...prev, { role: "user", content: payload.text }, { role: "agent", content: parsed.flags.clarification_question }]);
        setLoading(false);
        return;
      }
      
      setIsTransitioning(true);
      const estimate = await getFullEstimate(payload);
      const hospitals = await getRankedHospitals(parsed);
      
      await new Promise(resolve => setTimeout(resolve, 300));
      
      navigate("/results", { state: { estimate, hospitals, query: payload } });
    } catch (err) {
      setError(err?.response?.data?.detail || "Something went wrong. Please try again.");
      setIsTransitioning(false);
    } finally {
      setLoading(false);
    }
  };

  const handleClarificationAnswer = async (answer) => {
    if (!answer.trim() || loading) return;
    
    setLoading(true);
    try {
      const combinedText = chatLog
        .filter(m => m.role === "user")
        .map(m => m.content)
        .join(" | ") + " | Clarification: " + answer;
      
      const payload = { text: combinedText };
      const parsed = await parseQuery(payload);
      
      if (parsed.flags?.needs_clarification && clarificationTurns < 3) {
        setClarificationQuestion(parsed.flags.clarification_question);
        setClarificationTurns(prev => prev + 1);
        setChatLog(prev => [...prev, { role: "user", content: answer }, { role: "agent", content: parsed.flags.clarification_question }]);
        setLoading(false);
        return;
      }
      
      setIsTransitioning(true);
      const estimate = await getFullEstimate(payload);
      const hospitals = await getRankedHospitals(parsed);
      
      await new Promise(resolve => setTimeout(resolve, 300));
      
      navigate("/results", { state: { estimate, hospitals, query: payload } });
    } catch (err) {
      setError(err?.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-page">
      <div className="hero">
        <div className="hero-badge">AI-Powered · India-Focused</div>
        <h1 className="hero-title">Find the Right Hospital.<br />Know the Real Cost.</h1>
        <p className="hero-sub">
          Describe your condition in plain language. Get ranked hospitals, itemized cost estimates,
          and confidence-aware guidance — instantly.
        </p>
      </div>

      {clarificationQuestion ? (
        <div className="clarification-box">
          <div className="chat-log">
            {chatLog.map((msg, idx) => (
              <div key={idx} className={`chat-msg ${msg.role}`}>
                <strong>{msg.role === "user" ? "You" : "CareCompass"}:</strong> {msg.content}
              </div>
            ))}
          </div>
          <div className="clarification-input">
            <input 
              ref={clarifyInputRef}
              type="text" 
              placeholder="Type your answer here..."
              disabled={loading || isTransitioning}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  const answer = e.target.value;
                  e.target.value = "";
                  handleClarificationAnswer(answer);
                }
              }}
            />
            <p className="hint">Press Enter to send · Ask another question or provide more details</p>
          </div>
        </div>
      ) : (
        <ChatInterface onSubmit={handleSubmit} loading={loading || isTransitioning} />
      )}

      {error && <div className="error-banner">⚠️ {error}</div>}

      <div className="trust-strip">
        <span>🏥 Real hospital data</span>
        <span>📊 Transparent scoring</span>
        <span>🛡️ Decision support only — not medical advice</span>
        <span>🇮🇳 India city-tier pricing</span>
      </div>
    </div>
  );
}
