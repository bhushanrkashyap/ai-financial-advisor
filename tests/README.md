# Tests

Layout:

- `backend/` — FastAPI tests (pytest); uses repository `pytest.ini` for paths.
- `ml/` — ML package/unit tests.
- `java-engine/` — Java tests live under `java-engine/src/test/java` (Maven).
- `integration/` — cross-service checks (compose, API contracts).
- `e2e/` — browser or end-to-end automation (add tooling when ready).
