# Reflection - Cross-Project Contributions

**Assignment 15 | Teboho Mokoni | SentinelPay**

---

## Lessons Learned About Open-Source Collaboration

Contributing to a classmate's repository feels completely different from
working on your own code. When it is your own project, you know every
decision that was made and why. When you open someone else's codebase for
the first time, you are confronted immediately with unfamiliar conventions,
undocumented assumptions, and a mental model you have to reverse-engineer
from the code itself.

The first lesson I learned was to read before touching anything. The
CONTRIBUTING.md tells you the rules, but the actual code tells you the
culture - whether they prefer explicit type annotations or not, whether
they use dataclasses or plain dicts, whether tests live next to the source
or in a separate directory. A PR that ignores these conventions gets
rejected or buried in review comments, no matter how correct the logic is.

The second lesson was about scope. My first instinct was to fix everything
I noticed while reading the code. I stopped myself, because a PR that
changes 15 things is nearly impossible to review - the maintainer cannot
tell which change solves which problem, and the risk of any single change
breaking something multiplies. I picked one thing, fixed it cleanly, and
moved on. Small PRs get merged. Large PRs get comments and then ignored.

---

## Collaboration Challenges

The biggest challenge was communication timing. In a real open-source
project, you comment on an issue, wait for the maintainer to confirm you
can work on it, and then start coding. In a class project with a deadline,
that cycle cannot always complete before you need to submit. I learned to
comment early - even before I was certain I would work on a specific issue
- because claiming an issue publicly prevents duplicate work from two
contributors.

The second challenge was understanding someone else's architecture quickly
enough to contribute without breaking it. SentinelPay has a specific
layered architecture - domain entities, repository interfaces, services,
API routes - and any change needs to fit that structure. Classmates had
different architectures. Contributing to a project with a different design
pattern from what you built yourself requires genuine humility: you adapt
to their patterns, not the other way around.

---

## How Peer Feedback Improved My Own Repository

Having 36 people fork SentinelPay taught me what was unclear in my own
documentation. When contributors fork a repo, they try to run it. The
questions they would have asked - How do I install the dependencies? Which
Python version? How do I run just the API tests? - are exactly the gaps I
found when I wrote the CONTRIBUTING.md.

The CI pipeline fix I shipped in Assignment 14 directly came from this
process. The broken import paths (`../Assignment10` vs `../Assignment 10`)
would only be noticed by someone trying to clone and run the project fresh.
I had been running tests from within the folder where the paths happened to
resolve. A contributor running from the repo root would have hit this
immediately. The 36 forks effectively gave me 32 code reviewers who stress-
tested my setup instructions without saying a word.

---

## What I Would Do Differently

If I were starting this course again, I would treat every assignment as if
a stranger would try to run it. That means: no hardcoded paths, no
assumptions about working directory, a requirements.txt from the start,
and a one-command setup. The assignments that scored lower on peer
engagement were invariably the ones that were harder to run, not the ones
with less functionality.

---

*Word count: ~600 words*
*SentinelPay - Teboho Mokoni | CPUT Postgraduate Diploma in Software Engineering*