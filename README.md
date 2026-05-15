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

This project is licensed under the MIT License — see the `LICENSE` file for details.

## Ready for GitHub

This repository has been prepared for publishing to GitHub:

- Added a `.gitignore` to exclude build artifacts and large files.
- Included an `LICENSE` (MIT).

Quick push example:

```bash
git init
git add .
git commit -m "chore: initial repository cleanup and license"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

Replace `<your-repo-url>` with your GitHub repository URL.
