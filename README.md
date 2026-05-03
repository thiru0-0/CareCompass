# CareCompass - AI Healthcare Navigator for India

<p align="center">
  <a href="https://carecompass.ai">
    <img src="https://img.shields.io/badge/CareCompass-AI%20Healthcare%20Navigator-purple?style=for-the-badge&logo=health&logoColor=white" alt="CareCompass">
  </a>
  <br>
  <a href="https://github.com/anomalyco/opencode">
    <img src="https://img.shields.io/badge/Built%20with-opencode-blue?style=for-the-badge" alt="Built with opencode">
  </a>
</p>

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [What is CareCompass?](#what-is-carecompass)
3. [Problem Statement](#problem-statement)
4. [Solution Overview](#solution-overview)
5. [Features](#features)
6. [Architecture](#architecture)
7. [Tech Stack](#tech-stack)
8. [Project Structure](#project-structure)
9. [Getting Started](#getting-started)
10. [API Documentation](#api-documentation)
11. [Business Model & Insights](#business-model--insights)
12. [Data Sources](#data-sources)
13. [Future Enhancements](#future-enhancements)
14. [Security & Compliance](#security--compliance)
15. [Troubleshooting](#troubleshooting)
16. [Contributing](#contributing)
17. [License](#license)

---

## Executive Summary

**CareCompass** is an AI-powered healthcare navigation platform designed specifically for India. It helps patients:
- Find the right hospital for their medical condition
- Get transparent, itemized treatment cost estimates
- Understand available financial assistance programs
- Make informed healthcare decisions with confidence

The platform addresses a critical gap in Indian healthcare: **the lack of transparent pricing and hospital quality information** that forces patients to make life-altering financial decisions without adequate information.

---

## What is CareCompass?

CareCompass is not just another healthcare directory. It's a comprehensive decision-support platform that combines:

| Component | Description |
|-----------|-------------|
| **AI Query Parser** | Natural language processing to understand patient queries in English, Hinglish, or informal language |
| **Hospital Ranking Engine** | Multi-factor scoring system (clinical capability, cost fit, distance, patient sentiment) |
| **Cost Estimator** | Range-based pricing that accounts for hospital tier, city, comorbidities, and age |
| **Scheme Eligibility Checker** | Automatic detection of government schemes (PMJAY, CGHS, ESI, state programs) |
| **Financing Gap Analyzer** | Calculates loan/financial assistance needs after scheme coverage |

---

## Problem Statement

### The Indian Healthcare Crisis

India's healthcare system faces a unique challenge:

```
┌─────────────────────────────────────────────────────────────┐
│  STATISTICS: India's Healthcare Landscape                │
├─────────────────────────────────────────────────────────────┤
│  • 70% of healthcare expenses are OUT-OF-POCKET          │
│  • 80% of Indians have NO health insurance                 │
│  • 47% of hospitalized Indians BORROW money or sell     │
│    assets to afford treatment                              │
│  • 90% of hospitals in India are UNREGULATED pricing    │
│  • Rural India: 1 doctor per 25,000 patients           │
└─────────────────────────────────────────────────────────────┘
```

### The Information Gap

When a patient needs treatment:
1. **They don't know** which hospital is best for their condition
2. **They don't know** how much it will actually cost
3. **They don't know** what financial assistance they qualify for
4. **They don't know** if they're being overcharged

**CareCompass solves this information asymmetry.**

---

## Solution Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                  USER FLOW                                  │
│                                                          │
│  ┌─────────┐    ┌──────────┐    ┌─────────────┐          │
│  │ User    │───▶│ AI Query │───▶│ Condition  │          │
│  │ Input   │    │ Parser   │    │ Extractor  │          │
│  └─────────┘    └──────────┘    └──────┬──────┘          │
│                                        │                 │
│                                        ▼                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────┐      │
│  │ Hospital   │◀───│ Cost       │◀───│ Scheme  │      │
│  │ Ranking   │    │ Estimator   │    │ Checker │      │
│  └─────┬─────┘    └──────┬──────┘    └─────────┘      │
│        │                 │                 │                 │
│        ▼                 ▼                 ▼                 │
│  ┌──────────────────────────────────────────┐          │
│  │     RESULTS PAGE                        │          │
│  │  • Ranked hospitals with costs        │          │
│  │  • Cost breakdown (itemized)        │          │
│  │  • Applicable schemes             │          │
│  │  • Financing gap analysis         │          │
│  │  • Confidence score              │          │
│  └──────────────────────────────────────────┘          │
└──────────────────────────────────────────────────────────┘
```

---

## Features

### 1. Natural Language Query Parser

Users can describe their condition in plain language:
- "Knee replacement surgery near Chennai under 3 lakh"
- "Angioplasty hospital in Nagpur, I have diabetes"
- "Cataract surgery for my mother, budget friendly"

The parser handles:
- **Multiple languages**: English, Hinglish, informal
- **Implicit references**: "sugar" → diabetes, "BP" → hypertension
- **Budget parsing**: "1 lakh", "3L", "300000" all understood
- **Location extraction**: City names, state names
- **Comorbidity detection**: Automatic identification of health conditions

### 2. Hospital Ranking Engine

Multi-factor scoring system:

| Factor | Max Points | Description |
|--------|------------|-------------|
| Clinical Capability | 40 | NABH accreditation, PMJAY empanelment, specialty match |
| Cost Fit | 30 | How well the hospital fits the patient's budget |
| Distance | 20 | Proximity to patient's location |
| Patient Sentiment | 10 | Ratings and reviews |
| **Total** | **100** | Composite ranking score |

### 3. Cost Estimation Engine

Key principles:
- **Always outputs RANGES** - Never point estimates (e.g., ₹1.8L - ��3.2L)
- **City-tier pricing** - Metro cities have 30-35% premium over Tier 2 cities
- **Comorbidity surcharges** - Diabetes +12%, Cardiac history +18%, CKD +20%
- **Hospital tier multiplier** - Premium 1.4x, Mid 1.0x, Budget 0.6x

### 4. Financial Scheme Eligibility

Automatically checks eligibility for:

| Tier | Schemes | Coverage |
|------|---------|----------|
| 1 | Ayushman Bharat PMJAY | Up to ₹5L/year |
| 2 | State schemes (Tamil Nadu CMCHIS, West Bengal Swasthya Sathi, Telangana Aarogyasri) | Variable |
| 3 | CGHS (govt employees), ESI (private sector) | Fixed rates |
| 4 | NGO/Trust funds (Tata Trusts, Narayana Hrudayalaya) | Sliding scale |

### 5. Confidence Scoring

Every estimate includes a confidence score:
- **High (70%+)**: Procedure well-documented, location available
- **Moderate (50-69%)**: Some uncertainty in location or procedure
- **Low (<50%)**: Significant unknowns, clarification needed

### 6. Emergency Detection

Automatically detects emergency situations:
- Keywords: "chest pain", "breathlessness", "stroke", "unconscious"
- Shows nearest hospitals with 24/7 emergency departments
- Prompts immediate action (call 112)

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)              │
│  ┌─────────┐  ┌─────────┐  ┌───────────┐  ┌────────────┐  │
│  │ Home    │  │ Results │  │ Loan      │  │ Components │  │
│  │ Page    │  │ Page    │  │ Eligibility│  │            │  │
│  └────────┘  └─────────┘  └───────────┘  └────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI + Python)                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                      API ROUTERS                           │ │
│  │  ┌──────────┐ ┌─────────────┐ ┌────────────────────┐   │ │
│  │  │ /query    │ │ /hospitals  │ │ /estimate (all-in-1) │   │ │
│  │  └─────┬────┘ └──────┬──────┘ └─────────┬──────────┘   │ │
│  └────────┼─────────────┼──────────────────┼──────────────┘ │
│           │             │                    │                   │
│           ▼             ▼                    ▼                   │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                   SERVICES                             │ │
│  │  ┌────────────┐ ┌────────────┐ ┌──────��─��─────────┐ │ │
│  │  │ NLP Service│ │ Ranking    │ │ Cost Service     │ │ │
│  │  │ (Gemini AI) │ │ Service    │ │                  │ │ │
│  │  └────────────┘ └────────────┘ └──────────────────┘ │ │
│  │  ┌────────────┐ ┌────────────┐ ┌──────────────────┐ │ │
│  │  │ Scheme     │ │ LLM        │ │ Research         │ │ │
│  │  │ Service    │ │ Service    │ │ Agent            │ │ │
│  │  └────────────┘ └────────────┘ └──────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                            │                                   │
│                            ▼                                   │
│  ┌───────────────────────────────────────────────────────���──┐ │
│  │                      DATA LAYER                          │ │
│  │  ┌────────────────────┐ ┌─────────────────────────┐ │ │
│  │  │ PMJAY Hospital List  │ │ Procedure Cost Database │ │ │
│  │  │ (JSON, ~1000+ hosp) │ │                         │ │ │
│  │  └────────────────────┘ └─────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

### System Design Principles

1. **Fallback-first architecture**: All services work without API keys using local keyword parsing
2. **Range outputs**: Never give false precision - always show uncertainty
3. **Graceful degradation**: If one component fails, others continue to work
4. **Decision support framing**: Never claim to provide medical advice

### API-First Design

The backend is completely decoupled from the frontend:

```
Frontend can be replaced with:
• Mobile app (React Native / Flutter)
• WhatsApp bot
• IVR system
• Voice assistant
```

---

## Tech Stack

### Backend

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Modern, high-performance Python web framework |
| **Pydantic** | Data validation using Python type annotations |
| **httpx** | Async HTTP client for external API calls |
| **Python 3.10+** | Modern Python with pattern matching |

### Frontend

| Technology | Purpose |
|------------|---------|
| **React 18** | UI library with hooks |
| **Vite** | Next-gen build tool |
| **React Router** | Client-side routing |
| **Axios** | HTTP client |

### Data

| Source | Description |
|--------|-------------|
| **PMJAY Hospital List** | Official Ayushman Bharat empanelled hospitals |
| **Procedure Cost Database** | Procedure-specific base costs |

---

## Project Structure

```
CareCompass/
├── README.md                 # This file
├── .env                      # Environment variables (local)
├── .env.example              # Environment template
├── start_backend.bat          # Windows startup script
│
├── backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI app entry point
│   │   │
│   │   ├── models/           # Pydantic data models
│   │   │   ├── __init__.py
│   │   │   ├── query.py      # User query schemas
│   │   │   ├── hospital.py  # Hospital schemas
│   │   │   └── estimate.py  # Estimate response schemas
│   │   │
│   │   ├── routers/          # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── query.py      # POST /api/query/
│   │   │   ├── hospitals.py # POST /api/hospitals/
│   │   │   └── estimate.py   # POST /api/estimate/
│   │   │
│   │   ├── services/         # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── nlp_service.py       # Query parsing (Gemini AI + fallback)
│   │   │   ├── ranking_service.py   # Hospital ranking algorithm
│   │   │   ├── cost_service.py    # Cost estimation engine
│   │   │   ├── scheme_service.py   # Government scheme eligibility
│   │   │   ├── llm_service.py    # Explanation generation
│   │   │   └── research_agent.py  # Research capabilities
│   │   │
│   │   └── utils/           # Utility functions
│   │       ├── __init__.py
│   │       └── geo.py       # Geocoding utilities
│   │
│   ├── requirements.txt    # Python dependencies
│   └── tests/             # Unit tests
│       ├── __init__.py
│       ├── test_cost_engine.py
│       └── test_ranking.py
│
├── frontend/               # React + Vite frontend
│   ├── public/
│   │   └── favicon.svg   # App favicon
│   ├── src/
│   │   ├── main.jsx     # React entry point
│   │   ├── App.jsx       # Main app component
│   │   ├── index.css    # Global styles
│   │   │
│   │   ├── components/  # Reusable UI components
│   │   │   ├── ChatInterface/
│   │   │   │   └── index.jsx
│   │   │   ├── HospitalCard/
│   │   │   │   └── index.jsx
│   │   │   ├── ConfidenceBar/
│   │   │   │   └── index.jsx
│   │   │   └── CostBreakdown/
│   │   │       └── index.jsx
│   │   │
│   │   ├── pages/       # Page views
│   │   │   ├── Home.jsx      # Main search page
│   │   │   ├── Results.jsx  # Results display page
│   │   │   └── LoanEligibility.jsx  # Financial options page
│   │   │
│   │   └── services/   # API client
│   │       └── api.js
│   │
│   ├── index.html      # HTML entry point
│   ├── vite.config.js # Vite configuration
│   └── package.json  # Node dependencies
│
├── data/              # Data files
│   ├── pmjay_hospitals.json      # Hospital data (~1000+ hospitals)
│   └── pmjay_hospitals_source.pdf  # Original data source
│
└── tests/            # Integration tests (optional)
```

---

## Getting Started

### Prerequisites

| Requirement | Version |
|-------------|----------|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |

### Installation

#### 1. Clone and Set Up

```bash
# Navigate to project directory
cd CareCompass

# Copy environment template
cp .env.example .env
```

#### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or on Windows, simply run:
```bash
start_backend.bat
```

#### 3. Frontend Setup

```bash
# Navigate to frontend (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### Running the Application

```
Backend:  http://localhost:8000
Frontend: http://localhost:5173
Health:   http://localhost:8000/health
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | No | Google Gemini API key for AI-powered query parsing. Falls back to local keyword parser if not set. |

Get your free API key from: https://aistudio.google.com/app/apikey

---

## API Documentation

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/query/` | Parse a natural language query |
| POST | `/api/hospitals/` | Get ranked hospitals for a parsed query |
| POST | `/api/estimate/` | Full end-to-end estimation |
| GET | `/health` | Health check |

### 1. POST /api/query/

Parse a user's free-text query into structured data.

**Request:**
```json
{
  "text": "Knee replacement surgery near Chennai under 3 lakh",
  "location": "Chennai",
  "age": 65,
  "comorbidities": ["diabetes"],
  "budget": 300000
}
```

**Response:**
```json
{
  "original_text": "Knee replacement surgery near Chennai under 3 lakh",
  "condition": "Osteoarthritis of Knee",
  "procedure": "Knee Replacement",
  "location": "Chennai",
  "budget": 300000,
  "age": 65,
  "comorbidities": ["diabetes"],
  "urgency": "medium",
  "flags": {
    "needs_clarification": false
  },
  "financial_signals": {
    "budget_sentiment": "constrained"
  }
}
```

### 2. POST /api/hospitals/

Get ranked hospitals for a specific procedure and location.

**Request:**
```json
{
  "condition": "Osteoarthritis of Knee",
  "procedure": "Knee Replacement",
  "location": "Chennai",
  "budget": 300000,
  "comorbidities": ["diabetes"]
}
```

**Response:**
```json
[
  {
    "id": "HOSP123456",
    "name": "Apollo Speciality Hospital",
    "city": "Chennai",
    "tier": "premium",
    "rating": 4.5,
    "nabh_accredited": true,
    "score": 78,
    "estimated_cost_range": [180000, 320000],
    "strengths": ["NABH Accredited", "PMJAY Eligible"],
    "warnings": ["Diabetes increases surgical risk"]
  }
]
```

### 3. POST /api/estimate/

Full end-to-end estimation in one call.

**Request:**
```json
{
  "text": "Knee replacement in Chennai, have diabetes, budget 3 lakh",
  "location": "Chennai",
  "age": 65,
  "comorbidities": ["diabetes"],
  "budget": 300000
}
```

**Response:**
```json
{
  "condition": "Osteoarthritis of Knee",
  "procedure": "Knee Replacement",
  "hospital_name": "Apollo Speciality Hospital",
  "hospital_tier": "premium",
  "city": "Chennai",
  "total_range": [180000, 320000],
  "breakdown": {
    "procedure": [81000, 144000],
    "consultation": [9000, 16000],
    "hospital_stay": [36000, 64000],
    "diagnostics": [18000, 32000],
    "medicines": [14400, 25600],
    "contingency": [21600, 38400]
  },
  "confidence_score": 0.72,
  "key_drivers": ["Procedure: knee replacement", "Metro city pricing premium (Chennai)"],
  "risk_flags": [
    "Diabetes may extend recovery time and increase costs"
  ],
  "notes": [
    "The estimate covers procedure fees, hospital stay, diagnostics, medicines, and contingency.",
    "Your reported conditions (diabetes) may affect recovery time and costs."
  ],
  "disclaimer": "This is AI-powered decision support only — not medical advice.",
  "applicable_schemes": [
    {
      "tier": 1,
      "name": "Ayushman Bharat PM-JAY",
      "description": "Provides up to ₹5 lakhs per family per year..."
    }
  ]
}
```

### 4. GET /health

Simple health check.

**Response:**
```json
{
  "status": "ok",
  "service": "healthcare-navigator"
}
```

---

## Business Model & Insights

### Revenue Streams (Future)

| Model | Description | Timeline |
|-------|-------------|-----------|
| **Hospital Premium Listings** | Hospitals pay for featured placement | Phase 2 |
| **Insurance Referral** | Commission on insurance sales | Phase 2 |
| **Loan Partner Revenue** | Commission on medical loans | Phase 3 |
| **Enterprise API** | B2B hospital analytics | Phase 3 |

### Market Opportunity

```
┌──────────────────────────────────────────────��─��────────────┐
│                 Indian Healthcare Market                      │
├─────────────────────────────────────────────────────────────┤
│  Total Market Size:     $372 Billion (2024)                  │
│  Healthcare IT:       $12 Billion                        │
│  Addressable Market:   $2-5 Billion                     │
│  Growing at:         25% YoY                                 │
└─────────────────────────────────────────────────────────────┘
```

### Target Segments

1. **Self-pay patients** (60% of population)
2. **PMJAY beneficiaries** (500M+ lives)
3. **Senior citizens** (140M+)
4. **NRIs sending money for family care**

### Competitive Advantage

| Competitor | CareCompass Advantage |
|-----------|---------------------|
| JustDial | **Cost estimates + confidence scores** |
| Practo | **Price transparency + financial schemes** |
| Insurance agents | **Self-service, no commission** |
| Hospital websites | **Compare across hospitals** |

---

## Data Sources

### PMJAY Hospital Data

- **Source**: Official Ayushman Bharat PMJAY hospital list
- **Coverage**: 29 states, 1500+ hospitals
- **Data points**: Hospital name, location, specialty, ownership, PMJAY empanelment

### Cost Data

- **Base costs**: Derived from government price catalogs
- **Adjustments**: City tier, hospital tier, comorbidities, age
- **Ranges**: Always output low-high ranges to reflect uncertainty

---

## Future Enhancements

### Phase 2 (Short-term)

| Feature | Description |
|---------|-------------|
| **WhatsApp Bot** | Conversational interface via WhatsApp |
| **Voice Support** | IVR system for rural users |
| **More Hospital Data** | Include non-PMJAY hospitals |
| **Insurance Integration** | Real-time premium quotes |

### Phase 3 (Medium-term)

| Feature | Description |
|---------|-------------|
| **Doctor Matching** | AI-powered doctor recommendations |
| **Appointment Booking** | Direct hospital appointments |
| **Medical Records** | Personal health record storage |
| **Loan Pre-approval** | Instant loan eligibility |

### Phase 4 (Long-term)

| Feature | Description |
|---------|-------------|
| **Multi-language** | Hindi, Telugu, Tamil, Bengali |
| **Teleconsultation** | Doctor video consultations |
| **Pharmacy Delivery** | Medicine ordering |
| **Insurance Claims** | Cashless claim processing |

---

## Security & Compliance

### Data Privacy

- **No PII storage**: We don't store patient health information
- **Encrypted connections**: All API calls use HTTPS
- **No medical advice**: Always frame as "decision support"

### Responsible AI Practices

1. **Confidence scores**: Always show uncertainty
2. **Disclaimer**: Always advise consulting professionals
3. **No diagnosis**: Never claim to diagnose conditions
4. **Range outputs**: Never give false precision

---

## Troubleshooting

### Common Issues

#### Backend won't start

```bash
# Check port availability
netstat -ano | findstr :8000

# Kill existing process
taskkill /F /PID <process_id>
```

#### Frontend shows blank page

```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### API returns 500 error

- Check backend logs for details
- Ensure hospital data file exists: `data/pmjay_hospitals.json`
- Verify Python dependencies installed

#### No hospitals returned

- Check hospital data file is valid JSON
- Verify location is spelled correctly

---

## Contributing

We welcome contributions! Please see our contributing guidelines.

### Running Tests

```bash
# Backend tests
cd backend
python tests/test_cost_engine.py
python tests/test_ranking.py
```

---

## License

MIT License - see LICENSE file for details.

---

## Acknowledgments

- [Ayushman Bharat PMJAY](https://pmjay.gov.in) for hospital data
- [Google AI Studio](https://aistudio.google.com) for Gemini API
- All open source libraries used in this project

---

<p align="center">
  <strong>CareCompass - Making Indian Healthcare Transparent</strong>
  <br>
  <a href="https://carecompass.ai">carecompass.ai</a>
</p>