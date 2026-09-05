# Fantasy Sidekick

Backend-only Python service: an SMS coach for fantasy football beginners. It sends lineup updates, teaches gradually, and keeps encouragement light—no web UI in this repo.

## Requirements

- Python 3.11+
- `pip` (or another installer that understands `pyproject.toml`)

## Setup

```bash
cd /Users/praneethuppari/Projects/fantasy-sidekick
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Run the CLI:

```bash
python -m fantasy_sidekick
# or: fantasy-sidekick
```

## Tests

```bash
source .venv/bin/activate
pytest
```

## Branching (GitHub Flow)

- **`main`** — always releasable; protected default branch.
- **`feature/*`** — short-lived branches for work (e.g. `feature/sms-webhook`).
- Open a pull request into `main`; merge when green. **No `develop` branch.**

```bash
git checkout main
git pull
git checkout -b feature/my-change
# ... commit ...
git push -u origin HEAD
# open PR → main
```
