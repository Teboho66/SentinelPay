# Reflection — Open-Source Collaboration and Peer Review

**Assignment 14 | SentinelPay | Teboho Mokoni**

---

## Improving the Repository Based on Peer Feedback

Before preparing SentinelPay for peer review, I looked at it through the eyes of
someone encountering it for the first time. The code worked — 288 tests passed,
the REST API had 21 documented endpoints, and the CI/CD pipeline ran automatically.
But none of that matters if a new contributor cannot figure out how to run it in
under ten minutes.

The first thing I added was a `CONTRIBUTING.md` that answers the questions a new
contributor actually asks: what do I need installed, how do I run the tests, how
do I pick something to work on, and what does a good PR look like? Writing this
forced me to walk through the setup from scratch myself, and I immediately found
a real problem — the `conftest.py` files in Assignment 11 and 12 referenced
`../Assignment10` without a space, while the actual folder name is `Assignment 10`.
This was the root cause of the CI pipeline not running. I only noticed it when I
tried to follow my own setup instructions. Writing documentation is a debugging
tool.

I also added a `ROADMAP.md` because one of the hardest things for a new contributor
is knowing where to start. The SentinelPay architecture (from Assignment 3) always
had Kafka, Redis, and ML model integration as planned components — they were in the
C4 diagrams and the SRD from day one. The roadmap makes those intentions visible and
organises them into phases with difficulty labels. A contributor with Redis experience
can immediately see where they would add value. One without it can still pick up a
`good-first-issue` like adding Prometheus metrics or writing database migration scripts.

The `good-first-issue` labels on GitHub Issues were another deliberate choice. I
labelled the five simplest tasks: adding Docker Compose with PostgreSQL and Redis,
adding structured JSON logging, writing database migration scripts, adding the
Prometheus metrics endpoint, and implementing the OTP validation logic for
StepUpChallenge. These are all self-contained — a contributor can complete one
without needing to understand the entire fraud detection pipeline.

---

## Challenges in Onboarding Contributors

The hardest challenge was that SentinelPay spans four separate Python packages across
three assignment folders, each with its own `sys.path` configuration. When I ran the
tests locally from inside each folder, everything worked. When the CI pipeline ran
them from the repo root, the paths broke because folder names contain spaces and the
path strings in the service files did not.

For a real open-source project, this kind of setup is a significant barrier to
contribution. A new contributor should be able to clone the repo, run one command,
and have everything working. I addressed this by rewriting the CI workflow to patch
the paths automatically before running tests, and by creating a `run.py` entry point
that sets `PYTHONPATH` correctly before starting uvicorn. But the deeper lesson is
that project structure decisions made early — like whether to use spaces in folder
names, or whether to have a monorepo versus separate packages — have long-term
consequences for contributor experience.

---

## Lessons Learned About Open-Source Collaboration

The most important lesson was that documentation is not separate from the code — it
is part of the product. A feature that is not documented might as well not exist for
a new contributor. The README, CONTRIBUTING.md, and ROADMAP.md are the first things
a contributor reads. If those are unclear or out of date, no amount of clean code
underneath will compensate.

The second lesson is that branch protection and CI are not bureaucratic overhead —
they are confidence builders. When a contributor opens a PR and sees all 288 tests
run automatically and come back green, they have evidence that their change did not
break anything. When the merge is blocked until tests pass, every contributor knows
that `main` is always in a deployable state. This is the kind of reliability that
makes people trust a project enough to contribute to it.

The third lesson is about scope. Open-source collaboration works best when tasks are
small and self-contained. The `good-first-issue` labels I added are not just
convenience labels — they represent a deliberate decision to decompose the roadmap
into units that can be completed by one person in one sitting. A task that requires
understanding the entire system is a task that almost no one will start.

Building SentinelPay across thirteen assignments taught me software engineering
principles in isolation. Assignment 14 taught me that software engineering is also
a social practice — code is written by people, for people, and the quality of the
collaboration infrastructure is just as important as the quality of the code itself.

---

*Word count: ~650 words*
*SentinelPay — Teboho Mokoni | CPUT Postgraduate Diploma in Software Engineering*
