# ResearchMind

The Living Literature Review Agent — powered by [Cognee](https://cognee.ai).

Never forgets a paper. Ingest research papers via arXiv ID, PDF upload, or pasted text, and ResearchMind builds a persistent knowledge graph across every paper, every session.

## Features

- **Knowledge Graph Memory** — every paper is structured into a graph of entities (methodology, dataset, findings, limitations, gaps)
- **Multi-Source Ingestion** — arXiv, PDF upload, pasted text, or URL
- **Semantic Querying** — ask research questions and get answers synthesized across the entire graph
- **Literature Review Generation** — auto-generate structured academic reviews with citations
- **Feedback Loop** — rate papers to adjust credibility weights for better synthesis

## Architecture

```
researchmind/
├── backend/           # FastAPI + Cognee + Anthropic Claude
│   ├── app/
│   │   ├── api/       # REST endpoints (papers, query, feedback, generate)
│   │   ├── core/      # Config + Cognee client (remember, recall, improve, forget)
│   │   ├── models/    # Pydantic schemas
│   │   ├── services/  # Business logic (paper ingestion, query, review)
│   │   └── main.py    # FastAPI app entry point
│   └── requirements.txt
└── frontend/          # Vite + React + Tailwind CSS
    ├── src/
    │   ├── components/ # UI components (layout, features, ui)
    │   ├── pages/      # Dashboard, Query, Review
    │   └── lib/api.js  # Axios API client
    └── package.json
```

## Getting Started

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys:
#   ANTHROPIC_API_KEY=sk-...
#   COGNEE_API_KEY=... (optional, for Cognee cloud)

uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install

# Set up environment
cp .env.example .env.local

npm run dev
```

The frontend runs at `http://localhost:5173` and the API at `http://localhost:8000`.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/papers/` | GET | List all papers |
| `/api/papers/` | POST | Add paper (arxiv, text, or pdf) |
| `/api/papers/{id}` | GET | Get paper details |
| `/api/papers/{id}` | DELETE | Remove paper from graph (forget) |
| `/api/papers/upload-pdf` | POST | Upload PDF file |
| `/api/papers/arxiv` | POST | Fetch paper from arXiv |
| `/api/papers/text` | POST | Add paper from pasted text |
| `/api/query/` | POST | Query across all papers |
| `/api/query/chat` | POST | Chat with research memory |
| `/api/feedback/` | POST | Submit rating/feedback |
| `/api/generate/review` | POST | Generate literature review |
| `/health` | GET | Health check |

## Tech Stack

- **Backend**: Python, FastAPI, SQLite (aiosqlite), Anthropic Claude
- **Memory Layer**: Cognee (graph + vector knowledge base)
- **Frontend**: React 18, Vite, Tailwind CSS, React Router, Lucide icons
