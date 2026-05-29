# Merited

**Turn a GitHub profile into an instant hiring decision.**

Merited analyzes a developer's real GitHub activity and generates a recruiter-ready evaluation — no resumes, no guesswork.

---

## What It Does

Given a GitHub username, Merited:

1. Fetches public repos, commit activity, and language breakdown via the GitHub API
2. Scores the developer on **Consistency** and **Project Complexity**
3. Detects real technical capabilities (auth, database, REST API, Docker, CI/CD)
4. Generates a **recruiter-readable recommendation** (via OpenAI or deterministic fallback)
5. Returns a shareable profile URL at `/p/<username>`

### Sample Output

```json
{
  "username": "gaearon",
  "tech_focus": "Frontend (React)",
  "consistency_score": 8.4,
  "project_complexity": 7.9,
  "top_project": {
    "name": "redux",
    "description": "Predictable state container for JS apps",
    "features": ["REST API", "Tests", "CI/CD"]
  },
  "recommendation": "Frontend-focused developer with consistent contribution history and experience building production-grade libraries. Suitable for mid-level to senior frontend engineering roles."
}
```

---

## Tech Stack

| Layer     | Technology                  |
|-----------|-----------------------------|
| Frontend  | Next.js 14, TypeScript, Tailwind CSS |
| Backend   | FastAPI, Python 3.12        |
| Database  | PostgreSQL (result caching) |
| AI        | OpenAI gpt-4o-mini (optional) |
| External  | GitHub REST API v3          |

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 15+
- A GitHub Personal Access Token (strongly recommended to avoid rate limits)
- OpenAI API key (optional — falls back to deterministic summaries)

---

### 1. Clone & Configure

```bash
git clone https://github.com/yourname/merited.git
cd merited
```

**Backend config:**
```bash
cd backend
cp .env.example .env
# Edit .env:
#   GITHUB_TOKEN=ghp_your_token
#   OPENAI_API_KEY=sk-your_key (optional)
#   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/merited
```

**Frontend config:**
```bash
cd ../frontend
cp .env.local.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

### 2. Run with Docker (recommended)

```bash
# From project root
cp .env.example .env   # add your tokens
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

---

### 3. Run Manually

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Create DB
createdb merited

# Run
python run.py
# or: uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## Project Structure

```
merited/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── profile.py       # REST endpoints
│   │   ├── core/
│   │   │   ├── config.py        # Settings (env vars)
│   │   │   └── database.py      # SQLAlchemy async setup
│   │   ├── models/
│   │   │   ├── profile.py       # DB model (cache)
│   │   │   └── schemas.py       # Pydantic schemas
│   │   ├── services/
│   │   │   ├── github.py        # GitHub API client
│   │   │   ├── scoring.py       # Consistency + complexity engine
│   │   │   ├── ai_summary.py    # OpenAI summary generation
│   │   │   └── profile_builder.py  # Orchestration
│   │   └── main.py              # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── page.tsx          # Home (input + results)
│       │   └── p/[username]/     # Shareable profile page
│       ├── components/
│       │   ├── InputForm.tsx
│       │   ├── ProfileCard.tsx
│       │   ├── ScoreBar.tsx
│       │   └── LoadingSkeleton.tsx
│       ├── lib/api.ts            # API client
│       └── types/index.ts        # TypeScript types
│
└── docker-compose.yml
```

---

## Scoring Methodology

### Consistency Score (0–10)
Analyzes 52 weeks of commit activity from the GitHub participation API.

| Component      | Weight |
|----------------|--------|
| Active week ratio | 40% |
| Total commit volume (log scale) | 35% |
| Recent activity (last 12 weeks) | 25% |

### Project Complexity Score (0–10)
Evaluated per repo, averaged over top 3.

| Component         | Max pts |
|-------------------|---------|
| README quality    | 3.0     |
| Config files      | 2.0     |
| Directory depth   | 2.0     |
| Stars             | 1.0     |
| Feature detection | 2.0     |

### Feature Detection
Detected from repo name, description, README content, and root file names:
- **Authentication** — auth, jwt, oauth, session keywords
- **Database Integration** — sql, mongo, postgres, redis, orm
- **REST API** — routes, controller, api, endpoint
- **Docker** — Dockerfile, docker-compose.yml present
- **CI/CD** — .github directory present
- **Tests** — test files or folders detected

---

## API Reference

### `POST /api/v1/profile`

Analyze a GitHub profile (uses cache if available).

**Request:**
```json
{ "username": "torvalds" }
```

**Response:** Full profile JSON (see sample above)

### `GET /api/v1/profile/{username}`

Fetch cached profile for a username.

### `GET /health`

Health check endpoint.

Full interactive docs at `/docs` when running locally.

---

## Test Usernames

| Username        | Expected Focus              | Notes                        |
|----------------|-----------------------------|------------------------------|
| `torvalds`     | Systems (C)                 | Linux kernel, low public activity |
| `gaearon`      | Frontend (React)            | Dan Abramov — Redux, React   |
| `yyx990803`    | Frontend (Vue)              | Evan You — Vue.js creator    |
| `antirez`      | Backend (C)                 | Redis creator                |
| `sindresorhus` | Frontend (JavaScript)       | Prolific OSS author          |
| `jessfraz`     | DevOps                      | Container/systems work       |

---

## Environment Variables

| Variable         | Required | Description                         |
|-----------------|----------|-------------------------------------|
| `GITHUB_TOKEN`  | Strongly recommended | PAT for 5000 req/hr vs 60 |
| `OPENAI_API_KEY`| Optional  | For AI summaries (falls back to template) |
| `DATABASE_URL`  | Yes       | PostgreSQL async connection string  |

---

## Known Limitations

- Private repos are not accessible — analysis covers public GitHub only
- GitHub API stats endpoints can return 202 (computing) on first call
- Without a GitHub token, rate limit is 60 requests/hour
- Developers with primarily private work will score conservatively

---

## License

MIT
