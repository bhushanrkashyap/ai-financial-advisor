# AI Financial Advisor

Monorepo for an AI-assisted financial advisory platform.

## Repository layout

| Path | Description |
|------|-------------|
| `frontend/` | React web application |
| `backend/` | FastAPI HTTP API and application services |
| `ml/` | Notebooks, preprocessing pipelines, and model artifacts |
| `java-engine/` | Finance recommendation engine (JVM service) |
| `datasets/` | Curated and versioned dataset staging area |
| `docs/` | Architecture and operational documentation |
| `scripts/` | DevOps, data, and maintenance scripts |
| `tests/` | Cross-package and integration tests |

## Prerequisites

- Node.js 20+ (frontend)
- Python 3.11+ (backend, ML)
- Java 17+ and Maven (java-engine)
- PostgreSQL 15+

## Quick start (placeholders)

Backend and ML dependencies are declared in their respective `requirements.txt` files. The frontend uses npm (see `frontend/package.json`). The Java engine builds with Maven from `java-engine/`.

Copy `.env.example` to `.env` at the repository root and adjust values before running services.

## License

Specify your license here.
