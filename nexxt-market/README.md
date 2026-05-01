# ⚡ NexxtMarket — AI-Driven Classified Marketplace

> A decision engine built around listings. Not just a marketplace.

![License](https://img.shields.io/badge/license-MIT-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![Docker](https://img.shields.io/badge/Docker-ready-blue)

## 🔥 What Makes This Different

Every listing evolves **every hour**:
- Real price intelligence vs market
- Live competition signals (who else is negotiating)
- Visibility decay warnings
- AI-generated listing improvements
- Gamified boost windows

Users return because **something always changes**.

---

## 🛠️ Stack (100% Free & Open Source)

| Layer | Tech | Why |
|---|---|---|
| Frontend | Next.js 14 + Tailwind CSS | Free, fast, SEO-ready |
| Backend | FastAPI (Python) | Fast async APIs |
| Real-time | Node.js + Socket.IO | Free WebSocket server |
| Database | PostgreSQL + Redis | Free self-hosted |
| Search | Meilisearch | Free open-source Elasticsearch alternative |
| AI/LLM | Groq API (free tier) | Llama-3 free, ultra-fast |
| AI Embeddings | HuggingFace Inference API | Free tier |
| Scheduler | APScheduler | Free Python scheduler |
| Container | Docker + Docker Compose | Free |
| CI/CD | GitHub Actions | Free |

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Docker + Docker Compose
- Git
- Groq API key (free at [console.groq.com](https://console.groq.com))
- HuggingFace token (free at [huggingface.co](https://huggingface.co))

### 1. Clone
```bash
git clone https://github.com/YOUR_USERNAME/nexxt-market.git
cd nexxt-market
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your free API keys
```

### 3. Launch Everything
```bash
docker compose up --build
```

### 4. Access
| Service | URL |
|---|---|
| Frontend (Website) | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Admin Dashboard | http://localhost:8501 |
| Meilisearch | http://localhost:7700 |

---

## 📁 Project Structure

```
nexxt-market/
├── backend/               # FastAPI — core API + AI agents
│   ├── agents/            # AI agent system
│   ├── models/            # SQLAlchemy data models
│   ├── routers/           # API route handlers
│   ├── services/          # Business logic
│   └── scheduler.py       # Hourly engagement engine
├── frontend/              # Next.js website
│   ├── pages/             # Routes
│   └── components/        # Reusable UI
├── realtime/              # Node.js WebSocket server
├── scripts/               # DB init + seed data
└── docker-compose.yml     # One-command deploy
```

---

## 🤖 AI Agent System

| Agent | Model | Purpose |
|---|---|---|
| Listing Optimizer | Groq Llama-3 | Title, desc, tags, pricing |
| Buyer Matcher | HuggingFace embeddings | Personalized feed |
| Trust & Fraud | Rule-based + Groq | Scam detection, seller scoring |
| Hourly Engine | Groq Llama-3 | Micro-events, signals |
| Conversation | Groq Llama-3 | Chat suggestions |

---

## 🔁 Hourly Engagement Engine

The scheduler runs every hour and for each active listing:

1. **Price Intelligence** — compares vs similar listings
2. **Time Pressure** — calculates visibility decay
3. **Social Proof** — real view/save/message counts
4. **Competition Signals** — active buyer count
5. **Content Evolution** — AI enriches listing description
6. **Seller Nudges** — improvement recommendations
7. **Boost Windows** — gamified visibility spikes
8. **Re-engagement Push** — notifications on real signals only

---

## 💰 Monetization (Built-in)

- `/listing/boost` — paid visibility boost (Stripe-ready)
- Featured placement slots
- Premium AI-optimization tier
- Urgency upgrades (extend listing life)

---

## 🧪 Testing

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test

# Load test (k6)
k6 run scripts/load_test.js
```

---

## 📦 Deploy to Production

### Free Tier Options
- **Railway.app** — free PostgreSQL + Redis + deploy
- **Render.com** — free web services
- **Vercel** — free Next.js hosting
- **Fly.io** — free container hosting

### One-click Railway Deploy
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app)

---

## 📄 License

MIT — use it, fork it, build on it.
