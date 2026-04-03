# Audit Findings — 2026-04-03

Review of all task lists and documentation for accuracy and completeness.

## Task Lists Reviewed

### next_actions.md (original)
All items implemented:
- Carriers running in same process — done via `scripts/start.py`
- Initial FastAPI implementation — done (`server.py`)
- Clear setup instructions with uv — done (`README_PREP.md`, `README.md`)
- pytest installed with stub test — done (`test_setup.py`, `test_stub.py`)
- User intent + technical spec + implementation plan — done (all in `docs/internal/`)

### next_actions_new.txt
All items implemented:
- Carrier B error message made generic ("Invalid data") — done
- Interviewer convenience scripts — done (`scripts/start.py`, `scripts/run_tests.sh`)
- Scripts documented — done

### next_actions_new_2.md
All items implemented:
- Documentation says single codebase is best — done (README.md, INTERVIEWER_GUIDE.md)
- Working solution with tests covering everything — done (`solutions/`, `tests/interviewer/test_candidate_results.py`)
- Test file to give candidates after interview — done (`test_candidate_results.py`, 19 tests)

### implementation_plan.md
Status of each planned phase:

| Phase | Status | Notes |
|-------|--------|-------|
| 1. Project scaffolding | Done | pyproject.toml, src/sayata/ structure |
| 2. Carrier simulators | Done | All 4 simulators, compiled to .pyc wheel |
| 3. Candidate's server | Done | server.py with planted bugs in carrier_a/b |
| 4. Test infrastructure | Done | conftest.py, test_stub.py, test_candidate_results.py |
| 5. Infrastructure | Partially done | See below |
| 6. Documentation | Done | business-rules.md, glossary.md, etc. |
| 7. Validation | Done | test_delivery.sh, test_exercise_setup.py |

### Phase 5 (Infrastructure) — not fully implemented

**Planned but not done:**
- `Dockerfile` — never created. The plan called for a Docker-based setup as an alternative.
- `docker-compose.yml` — never created.

**Assessment:** Docker was listed as an optional convenience in the plan. The exercise works without it (candidates use uv directly). The current setup with individual start scripts is simpler and avoids Docker compatibility issues during interviews. **Not a gap — intentional simplification.**

### planning_summary.md

One outdated detail:
- Task 2 references `GET /options` endpoint — actual endpoint is `/quoting_options` (renamed to be harder to guess).

Everything else matches the implementation.

## Documentation Issues Fixed in This Session

1. **INTERVIEWER_GUIDE.md** — Candidate copy-paste instructions referenced `start.py` which is not shipped in exercise.zip. Fixed to use `start_server.py` + `start_carrier.py`.
2. **INTERVIEWER_GUIDE.md** — Contradictory test timing (~90s vs ~35s). Fixed to ~35s.
3. **setup.sh** — Printed "start the servers with: start.py". Fixed to list individual scripts.
4. **INTERVIEWER_GUIDE.md** — Test name table was out of date (referenced old test_verification.py names). Fixed.
5. **CLAUDE.md** — Missing `solutions/` in project structure tree. Added.
6. **test_candidate_results.py** — Moved from `tests/` to `tests/interviewer/` (it's an interviewer test, not candidate-facing).
7. **Consolidated test suites** — Removed redundant `test_verification.py`, kept `test_candidate_results.py` as single source of truth.
