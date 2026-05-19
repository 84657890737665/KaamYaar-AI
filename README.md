# KaamYaar AI Orchestrator 🇵🇰

**KaamYaar** is an AI-powered service orchestration platform built for the informal economy in Pakistan. It bridges the gap between everyday consumers and informal service providers (plumbers, electricians, carpenters, etc.) by translating multi-lingual, messy natural language requests into structured, transparent, and algorithmic bookings.

---

## Architecture Diagram

The system employs a micro-agent architecture powered by Google Gemini and Google Maps.

```ascii
[Flutter Mobile App] 
       │ (JSON payload via REST)
       ▼
[FastAPI Backend - API Gateway] 
       │
       ├─► [LanguageParser Agent] (Gemini 2.0 Flash) 
       │      └─ Translates Urdu/Roman Urdu/Sindhi to English & extracts intent.
       │
       ├─► [GeoFinder Agent] (Google Maps API) 
       │      └─ Calculates accurate driving distances and filters nearby providers.
       │
       ├─► [RankerEngine] (6-Factor Algorithmic Scoring) 
       │      └─ Scores providers based on Distance, Rating, Price, Cancellation Rate, On-Time Score, and Skills Match.
       │
       ├─► [PricingEngine] 
       │      └─ Dynamically calculates pricing (Base + Urgency + Complexity + Distance - Discount).
       │
       └─► [BookingExecutor] 
              └─ Manages robust Firestore transactions & notification state machines.
       
       ▼
[Firebase / Firestore DB] -> Persistent State (Users, Providers, Bookings, Disputes, Reviews)
```

---

## API Documentation

The backend is built with FastAPI. Complete interactive documentation is available at `/docs` when running locally.

### Key Endpoints

#### 1. Parse Voice/Text Request
- **Method:** `POST /api/v1/parse-request`
- **Description:** Uses Gemini 2.0 to parse multi-lingual service requests into structured parameters.
- **Request Example:**
  ```json
  { "text": "Mujhe phase 5 defence mein ek acha plumber chahiye, paani leak ho raha hai" }
  ```
- **Response Example:**
  ```json
  {
    "service": "Plumber",
    "urgency": "high",
    "location": "Phase 5 Defence",
    "issue_description": "Water pipe leaking"
  }
  ```

#### 2. Find Providers (Geospatial)
- **Method:** `POST /api/v1/find-providers`
- **Description:** Queries Firestore for providers and calculates real driving distances via Google Maps.
- **Request Example:**
  ```json
  {
    "service_type": "Plumber",
    "latitude": 24.86,
    "longitude": 67.00,
    "radius_km": 5.0
  }
  ```

#### 3. Rank Providers (AI Selection)
- **Method:** `POST /api/v1/rank-providers`
- **Description:** Applies a 6-factor algorithm to rank found providers, returning the top match with human-readable reasoning.

#### 4. Book Service
- **Method:** `POST /api/v1/mobile/book-service`
- **Description:** Creates the booking transaction and dispatches the provider.
- **Request Example:**
  ```json
  {
    "provider_id": "prov_123",
    "service_type": "Plumber",
    "location": {"lat": 24.86, "lng": 67.00},
    "urgency": "high"
  }
  ```

---

## Assumptions

During the hackathon development phase, the following assumptions and mocks were used:
- **Mock FCM Notifications:** Push notifications to mobile clients are simulated via log statements instead of actual Firebase Cloud Messaging dispatch.
- **Simulated Real-Time Tracking:** Provider en-route location updates are simulated using fallback logic rather than real GPS device streams.
- **Mock Authentication:** Firebase Auth verification middleware is implemented but allows a bypass (mock user ID) if the `Authorization` header is omitted to simplify testing.
- **Mock Voice-to-Text:** The `/mobile/parse-voice` endpoint expects pre-transcribed text or acts as a mocked placeholder to demonstrate the architecture flow without integrating an active audio-transcription model.

---

## Cost Estimate (Production Scale)

Estimating standard usage for an early-stage startup processing roughly ~10,000 bookings a month:

| Service | Monthly Estimated Cost | Note |
|---------|-----------------------|------|
| **Google Cloud Run** | ~$20 | Autoscale to zero, based on 512MB RAM instances |
| **Firestore** | ~$15 | Document reads/writes + storage (highly optimized via indexing) |
| **Gemini API** | ~$30 | Using Gemini 2.0 Flash (extremely low latency and low cost per token) |
| **Google Maps API** | ~$25 | Distance Matrix API & Geocoding |
| **Firebase Auth/Storage**| Free Tier | Usually free for early stage |
| **Total Estimated** | **~$90 / month** | |

---

## Baseline Comparison

How KaamYaar's AI approach differs from traditional service discovery in Pakistan:

| Feature | Traditional Approach (e.g. WhatsApp / Facebook Groups) | KaamYaar AI Orchestrator |
|---------|--------------------------------------------------------|--------------------------|
| **Matching Speed** | Hours (waiting for replies and manual negotiation) | **Milliseconds** (Algorithmic exact-match) |
| **Language Barrier** | High (Often requires English or formal text) | **None** (Accepts Roman Urdu, Sindhi, Punjabi, voice notes) |
| **Pricing** | Opaque, purely negotiation-based | **Transparent**, algorithmic (Base + distance + urgency) |
| **Quality Control** | Word of mouth, high risk of fraud | **Data-driven**, tracking on-time %, cancellation rates, & verified ratings |
| **Dispute Resolution** | Non-existent or manual argument | **AI-Mediated**, automatic refund suggestions based on historical data |

---

## Setup Instructions

### Local Development

1. **Clone the repository and enter directory:**
   ```bash
   git clone <repo_url>
   cd kaamyaar-backend
   ```

2. **Set up Python Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Environment Variables:**
   Copy `.env.example` to `.env` and fill in your keys:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   GOOGLE_MAPS_API_KEY=your_maps_api_key
   # Ensure firebase-credentials.json is in the root directory
   ```

4. **Run the Application:**
   ```bash
   uvicorn app.main:app --reload
   ```
   *Dashboard is available at: `http://localhost:8000/dashboard/index.html`*

### Stress Testing

To validate system limits and algorithmic complexity:
```bash
# Run the Locust load test suite
./scripts/run_stress_tests.sh
```

---

## Team Roles

This project was built collaboratively by:

- **Tanzeela** — Focus: Generative AI Prompts (Gemini integration), Natural Language Parsing logic, Multi-lingual support strategies.
- **Rukhsar** — Focus: Mobile API integration, Frontend (Flutter) consumption layer alignment, UI/UX workflow logic.
- **Moattar** — Focus: Backend Architecture (FastAPI), Database Design (Firestore), Algorithmic Ranking Engine, Stress Testing & Performance Optimization.

---

## 5. Backend Team Contribution

**Moattar**
- FastAPI architecture & micro-agent design
- Implementation of the 7 AI Agents
- Highly optimized Firestore schema
- Google Cloud Run secure deployment
- System Security & Rate Limiting
- Core Performance optimization

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>

---

## API Endpoint Summary Table

Here is a quick overview of the key endpoints exposed by the KaamYaar orchestration API.

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/api/v1/parse-request` | POST | Language parsing |
| `/api/v1/find-providers` | POST | Provider discovery |
| `/api/v1/rank-providers` | POST | Ranking engine |
| `/api/v1/calculate-price` | POST | Pricing engine |
| `/api/v1/create-booking` | POST | Booking executor |
| `/api/v1/update-status` | POST | Status update |
| `/api/v1/submit-feedback` | POST | Feedback collection |
| `/api/v1/file-dispute` | POST | Dispute filing |
| `/dashboard` | GET | Visualization |

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>

---

## Performance Metrics

Our recent stress tests across the deployed infrastructure yielded the following metrics:

- **Avg response time:** 188ms
- **Success rate:** 99.1%
- **Active bookings:** 141
- **Ecosystem:** 50 providers, 8 languages supported

<br>

*Built with ❤️ for Pakistan.*
