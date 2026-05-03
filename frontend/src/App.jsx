import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Results from "./pages/Results";
import LoanEligibility from "./pages/LoanEligibility";
import "./index.css";

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="app-shell">
        <header className="app-header">
          <a href="/" className="logo">🏥 CareCompass</a>
          <span className="header-tagline">AI Healthcare Navigator · India</span>
        </header>
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/results" element={<Results />} />
            <Route path="/loan" element={<LoanEligibility />} />
          </Routes>
        </main>
        <footer className="app-footer">
          <p>For decision support only. Always consult a qualified medical professional.</p>
        </footer>
      </div>
    </BrowserRouter>
  );
}
