# Reflection - Cross-Project Contributions

**Assignment 15 | Teboho Mokoni | SentinelPay**

---

## Lessons Learned About Open-Source Collaboration

Contributing to a classmate's repository feels completely different from working on your own code. When it is your own project, you know every decision that was made and why. When you open someone else's codebase for the first time, you are confronted immediately with unfamiliar conventions, undocumented assumptions, and a mental model you have to reverse-engineer from the code itself.

The first lesson I learned was to read before touching anything. The `CONTRIBUTING.md` tells you the rules, but the actual code tells you the culture: whether they prefer explicit type annotations, whether they use dataclasses or plain dictionaries, whether tests live next to the source or in a separate directory, and how they structure routes, services, repositories, and documentation. A pull request that ignores these conventions can be difficult to review, even when the logic is technically correct.

The second lesson was about scope. My first instinct was to fix everything I noticed while reading the code. I stopped myself because a pull request that changes many unrelated things is nearly impossible to review. The maintainer cannot easily tell which change solves which problem, and the risk of breaking something increases. I learned that small, focused pull requests are easier to understand, easier to test, and easier to merge.

Assignment 15 also taught me that open-source contribution is not only about code. Some of my contributions were documentation-focused, while others improved APIs, validation behaviour, and test coverage. All of them required communication, issue tracking, branching discipline, local testing, and clear pull request descriptions.

---

## Collaboration Challenges

The biggest challenge was communication timing. In a real open-source project, you comment on an issue, wait for the maintainer to confirm that you can work on it, and then start coding. In a class project with a deadline, that cycle cannot always complete before submission. I learned to comment early because claiming an issue publicly helps prevent duplicate work and shows respect for the maintainer.

The second challenge was understanding someone else's architecture quickly enough to contribute without breaking it. SentinelPay has a specific layered architecture with domain entities, repository interfaces, services, API routes, and tests. My classmates' repositories used different structures and technologies, including FastAPI and Spring Boot. Contributing to a project with a different architecture requires humility: you adapt to their patterns instead of forcing your own style onto their project.

Another challenge was environment setup. Some repositories did not include a requirements file, some needed different Java versions, and some had test dependencies that were not immediately installed. I learned that running tests locally is not just a checklist item. It is how you discover hidden assumptions in the project setup before opening a pull request.

---

## How Peer Feedback Improved My Own Repository

Having SentinelPay receive 28 stars and 37 forks taught me what was unclear in my own documentation. When contributors fork a repository, they try to run it. The questions they would have asked — how to install dependencies, which Python version to use, how to run the API tests, and how to start the server — are exactly the gaps I found when improving my own setup documentation.

The CI pipeline fixes I made in earlier assignments also became more important during Assignment 15. Broken import paths, missing dependencies, and unclear working-directory assumptions are the kinds of issues that appear when someone clones a project fresh. I had been running some tests from folders where paths happened to resolve correctly, but a contributor running from the repository root would hit those problems immediately.

The peer contribution process helped me see SentinelPay through the eyes of a new contributor. That made me improve the project as a contribution target, not just as a personal assignment submission.

---

## What I Would Do Differently

If I were starting this course again, I would treat every assignment as if a stranger would try to run it. That means no hardcoded paths, no assumptions about the working directory, a `requirements.txt` from the start, and a one-command setup process.

I would also create clearer issue labels and smaller roadmap tasks earlier. The repositories that were easiest to contribute to were the ones with clear issues, small scopes, and enough documentation for a contributor to get started without asking many setup questions.

Finally, I would capture evidence screenshots as I worked instead of after finishing. Screenshots of issue comments, branches, test results, pull requests, files changed, CI checks, and merge status are easier to collect during the workflow than after the fact.

---

## Final Reflection

Assignment 15 helped me practise the real workflow of collaborative development. I selected issues, commented before coding, created feature branches, made focused changes, ran tests, opened pull requests, responded to project requirements, and tracked evidence professionally.

The biggest takeaway is that open-source contribution is about trust. A maintainer is more likely to merge a pull request when the change is small, the issue is linked, the tests pass, and the explanation is clear. Code matters, but communication and confidence matter just as much.

---

*Word count: ~760 words*  
*SentinelPay - Teboho Mokoni | CPUT Postgraduate Diploma in Software Engineering*