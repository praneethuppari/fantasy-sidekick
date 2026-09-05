# Fantasy Sidekick

SMS coach for fantasy football beginners: lineup updates, gradual concept teaching, encouragement, and (later) weekly stats. **Backend-only Python** — no web frontend.

## Why this exists

Friends in a league who are new to fantasy (and football) need simple, timely texts — not another dashboard to learn.

## Stack

| Choice | Why |
|--------|-----|
| Python 3.11+ | Matches your background; great for jobs, SMS APIs, and data |
| `src/` layout | Packaged install; keeps imports clean |
| Env-based config | Secrets stay out of git |
| pytest | Lightweight verification from day one |

**Not chosen (for now):** FastAPI/web UI (you asked for no frontend), serverless (extra ops for a personal coach).

## Project layout

```
fantasy-sidekick/
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── src/fantasy_sidekick/   # application package
├── tests/                  # pytest
└── scripts/                # local helper scripts
```

## Local setup

**Prerequisites:** Python 3.11+, git

```bash
cd ~/Projects/fantasy-sidekick

# If git isn't initialized yet (sandbox may have blocked it):
./scripts/init_repo.sh

python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env
fantasy-sidekick          # or: python -m fantasy_sidekick
pytest
```

## Branching structure

We use a light **Git Flow–inspired** model suited to a personal backend:

| Branch | Role |
|--------|------|
| `main` | Stable / releasable |
| `develop` | Integration branch for ongoing work |
| `feature/<short-name>` | One feature or fix; branch from `develop`, merge back to `develop` |

**Day-to-day:**

```bash
git checkout develop
git pull   # when you have a remote
git checkout -b feature/sms-lineup-reminder
# ... work, commit ...
git checkout develop
git merge feature/sms-lineup-reminder
```

Promote to `main` when a slice is solid enough to “ship” (e.g. first SMS to yourself).

**Do not commit** `.env` or API keys. Use `.env.example` as the template.

## Roadmap (high level)

1. League/roster data model + local storage  
2. SMS outbound (Twilio or similar)  
3. Scheduled lineup reminders  
4. Concept-of-the-week teaching messages  
5. Encouragement + weekly stats  

## License

Personal project — no license set yet.
