# Assignment 14 – SentinelPay: Open-Source Collaboration

## Deliverables

| File | Description | Marks |
|---|---|---|
| `CONTRIBUTING.md` | Setup, coding standards, PR process | 40% |
| `ROADMAP.md` | 7 phases of planned features with difficulty labels | 40% |
| `VOTING_RESULTS.md` | 26 ⭐ stars, 32 🍴 forks | 40% |
| `REFLECTION.md` | 650-word reflection on collaboration | 20% |
| `LICENSE` | MIT License (repo root) | 40% |
| `docs/screenshots/` | Voting results screenshot | — |

> **CONTRIBUTING.md, ROADMAP.md, and LICENSE live at the repo root** so
> GitHub recognises them automatically (shows the license badge, adds
> "Contributing" link in the sidebar, etc.)

---

## GitHub Issues to Label

Go to **Issues** tab and create/label these:

### good-first-issue (need 5+)
1. Add Docker Compose with PostgreSQL and Redis services
2. Add Prometheus `/metrics` endpoint to the FastAPI app
3. Add structured JSON logging using structlog
4. Implement `CustomerDisputeService` and dispute endpoints
5. Write Alembic database migration scripts

### feature-request (need 3+)
1. XGBoost model training script on IEEE-CIS Fraud Detection dataset
2. Kafka producer integration for transaction event streaming
3. Redis-backed `AccountProfileRepository` for velocity counters

To label them:
1. Go to `github.com/Teboho66/SentinelPay/issues`
2. Click **New issue** for each one above
3. On the right side click **Labels → good-first-issue** or **feature-request**
4. If those labels don't exist yet: go to **Issues → Labels → New label**

---

## Peer Engagement

- **26 stars** received from classmates
- **32 forks** received from classmates
- Repo shared in class forum/WhatsApp group

Screenshot your repo homepage showing the star/fork counts and save as:
`Assignment 14/docs/screenshots/voting_results.png`

---

## Repo Structure After This Assignment

```
SentinelPay/
├── CONTRIBUTING.md        ← new (repo root — GitHub shows it automatically)
├── ROADMAP.md             ← new (repo root)
├── LICENSE                ← new (repo root — shows license badge)
├── VOTING_RESULTS.md      ← could also go in Assignment 14/
├── .github/workflows/ci.yml  ← fixed CI pipeline
│
├── Assignment 14/
│   ├── README_A14.md
│   ├── CONTRIBUTING.md    ← copy for marking reference
│   ├── ROADMAP.md         ← copy for marking reference
│   ├── VOTING_RESULTS.md
│   ├── REFLECTION.md
│   └── docs/screenshots/
│       └── voting_results.png  ← take this screenshot yourself
```
