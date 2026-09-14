# Merge Tool Comparison — Presentation Plan

**Thesis:** Simple heuristic-based merge tools outperform complex algorithmic approaches in practice.
**Audience:** Lab/research group (SE-literate peers)
**Duration:** 10–15 minutes (~10–12 slides)
**Narrative arc:** Set up the intuition that "smarter = better" → show how the paper dismantles it → confirm with your own results → draw the lesson

---

## Slide 1: Title Slide
**Title:** Do Smarter Merge Tools Actually Work Better?
**Subtitle:** Evaluating Version Control Merge Tools — Schesch et al. (ASE '24) & Replication
**Author:** Ali Karimli

**Speaker notes:** Open with the provocative question. The research community has spent years building increasingly sophisticated merge algorithms (AST-based, graph-based, refactoring-aware). The assumption is that understanding code structure leads to better merges. This talk shows that assumption is largely wrong.

---

## Slide 2: The Intuition — More Sophistication Should Help
**Key points:**
- Merging = integrating concurrent changes from two branches against a common ancestor
- Line-based tools (Git Merge) are "dumb" — they see code as text, not structure
- Paper's Fig 1: Git Merge reports a conflict where a smarter tool could resolve it (rename + value change on same line)
- Paper's Fig 2: Git Merge merges cleanly but *incorrectly* (function rename + call addition on different lines)
- **The promise of structured tools:** if we understand ASTs, PEGs, refactorings, we can do better... right?

**Visual:** Reproduce the paper's Fig 1 and Fig 2 side by side — one showing a false conflict, the other a silent incorrect merge. Label them: "Where simple tools fail."

**Speaker notes:** Set up the expectation. The audience should be nodding along — of course AST-aware tools should fix these problems. Then you'll pull the rug.

---

## Slide 3: The Contenders — Simple vs. Complex
**Key points — frame as a spectrum from simple to complex:**

| Approach | Tool | How it works |
|----------|------|-------------|
| **Line-based** | Git Merge (ort) | Text diff + 3-way merge on lines |
| **Character-level** | Hires-Merge | Like Git Merge but at character granularity |
| **Simple heuristics** | Adjacent, Imports, Version Numbers, IVn | Small targeted fixes on top of Git Merge output |
| **AST/Tree-based** | Spork, JDime | Parse into ASTs, match via GumTree, merge trees |
| **Graph-based** | IntelliMerge | Build Program Element Graphs, refactoring-aware merge |

**The hypothesis from the literature:** tools further down this list should perform better.

**Visual:** Horizontal spectrum arrow: Simple → Complex, with tools placed along it.

**Speaker notes:** Emphasize the intellectual investment — Spork uses GumTree (from your previous talk!), IntelliMerge builds full program graphs. These are years of research effort. The question is: does that effort pay off?

---

## Slide 4: How Do You Even Measure "Better"? (Schesch et al. Methodology)
**Key points:**
- **Previous evaluations were flawed:** they assumed clean merge = correct merge
- Schesch et al.'s key innovation: run the project's *test suite* on the merged output
- Three outcomes: **correct** (tests pass), **incorrect** (tests fail silently!), **unhandled** (conflict reported)
- Dataset: 6,045 real merges from 1,120 Java repos (including non-main branches)
- **This matters for our thesis:** without measuring correctness, complex tools *look* better (fewer conflicts) while hiding their mistakes

**Visual:** Pipeline: 42K repos → filter → 6,045 merges → run tool → run tests → classify as correct/incorrect/unhandled

**Speaker notes:** This is the crucial methodological point. If you only count conflicts, Spork looks great. If you measure correctness, the picture inverts. The evaluation methodology is what reveals the truth about simple vs. complex.

---

## Slide 5: The Paper's Verdict — Simple Wins (Usually)
**Key points:**
- **The results table tells the story (Fig 8 from paper):**
  - Git Merge: 46% correct, 51% unhandled, **3% incorrect**
  - Spork: 54% correct, 35% unhandled, **11% incorrect** (!!!)
  - IntelliMerge: 24% correct, 26% unhandled, **50% incorrect** (!!!)
  - IVn (simple heuristics on Git Merge): 50% correct, 47% unhandled, **3% incorrect**
- **The k-factor:** Spork only wins if an incorrect merge costs ≤ 1x an unhandled merge. At k > 2, it's the *worst* tool.
- **The killer finding:** Imports (a trivial heuristic) alone outperforms IntelliMerge
- Previous claims by IntelliMerge and Spork papers were dramatically overstated

**Visual:** The effort-reduction chart (Fig 9) showing how the lines cross — Spork rises fast but crashes as k increases, while Git Merge and IVn stay steady. Highlight the crossover point.

**Speaker notes:** THIS is the slide. Spend time here. The audience needs to see that 11% incorrect rate means 1 in 9 of Spork's "clean" merges silently breaks the code. IntelliMerge is even worse — half its merges are wrong. Meanwhile, simple Git Merge with a few targeted heuristics (IVn) matches or beats them with almost no incorrect merges.

---

## Slide 6: Why Do Complex Tools Fail?
**Key points — draw from Section 7 of the paper:**
- **Spork:** produces uncompilable code, gratuitous formatting changes, omitted method bodies. Maintainers acknowledged bugs but haven't fixed them.
- **IntelliMerge:** its refactoring detection (rename operations) fires incorrectly on non-refactoring scenarios, causing cascading errors
- **JDime:** crashes on modern Java, discards comments, arbitrarily reorders methods
- **The pattern:** complex tools have larger attack surface for bugs. Every abstraction layer is a place where things can go wrong.
- **Meanwhile, simple heuristics work because they're conservative:** they only touch what they're confident about (imports, version numbers, adjacent lines)

**Visual:** Two columns — "Complex tool failure modes" (long list) vs. "Simple heuristic scope" (narrow, safe). Or concrete code examples from Section 7.

**Speaker notes:** This is the *why* behind the numbers. Structured tools aren't bad ideas in theory — they just have so many moving parts that implementation bugs dominate. The Schesch team spent a person-month trying to fix Spork's bugs and couldn't.

---

## Slide 7: Our Replication Framework
**Key points:**
- Built a Python framework to independently verify these findings
- 4 tools: git-merge-file (simple baseline), JDime, Spork, Mastery (all Dockerized)
- Classification: compare tool output against developer's actual resolution
  - TP (correct), FP (incorrect!), TN (real conflict), FN (unnecessary conflict), CRASH, TIMEOUT
- Extensible: new tool = one adapter + config entry

**Visual:** Simple architecture diagram. Emphasize the comparison logic: "Does the tool's output match what the developer actually committed?"

**Speaker notes:** Keep this slide brief — it's setup for the results. The key point is that you can independently verify the paper's claims.

---

## Slide 8: Our Results — Simple Wins Again
**Key points — present as a scoreboard:**

| Tool | Correct | Incorrect | Conflicts | Crashes | Verdict |
|------|---------|-----------|-----------|---------|---------|
| **git-merge-file** | 39/50 | **0** | 10 | 0 | Safe & effective |
| Spork | 1/50 | **42** | 6 | 0 | Dangerous |
| Mastery | 0/50 | **44** | 6 | 0 | Dangerous |
| JDime | 0/50 | 2 | 0 | **48** | Broken |

- **git-merge-file: 0 incorrect merges.** Perfect precision. The simplest tool is the safest.
- Spork: 97.7% of its "clean" merges were wrong. It's confidently wrong almost every time.
- Mastery: 100% incorrect rate on merges it attempted
- JDime: crashed on 96% of scenarios

**Visual:** Bar chart with red/green coloring — make the incorrect (FP) bars visually alarming for Spork/Mastery. Or a simple table with git-merge-file row highlighted in green.

**Speaker notes:** The thesis lands here. The simplest tool in our evaluation — Git's built-in line-based merge — produced zero incorrect merges. Every complex tool either crashed or flooded the results with silent errors. Simple doesn't just compete with complex — it dominates.

---

## Slide 9: Why Simple Works — The Deeper Lesson
**Key points:**
- **Conservative > Ambitious:** It's better to report a conflict (let the human decide) than to silently introduce a bug
- **Targeted heuristics > General algorithms:** Imports, Version Numbers fix specific known patterns with near-zero risk. They don't try to "understand" code — they just handle common cases.
- **The cost asymmetry:** An unhandled merge costs you 10 minutes of manual resolution. An incorrect merge can cost hours of debugging, or worse, a production bug.
- **Implication for research:** the community should invest in finding and automating *safe* patterns rather than building ever-more-complex general-purpose mergers

**Visual:** A scale/balance metaphor — "Ambition" (complex tools) vs. "Safety" (simple tools), tipping toward safety. Or a simple cost comparison: "10 min to resolve a conflict" vs. "hours to debug a silent merge bug."

**Speaker notes:** This is the takeaway the audience should remember. The research incentive structure rewards novelty and sophistication, but practitioners need safety and predictability.

---

## Slide 10: Future Work
**Key points:**
- Scale to full 6,045-scenario dataset
- Add IntelliMerge, Hires-Merge, IVn to the framework
- Categorize scenarios (refactoring, imports, formatting) to identify *where* complex tools might still help
- Integrate test-suite execution for true correctness validation
- Empirically measure k (the real cost ratio) from developer surveys or time-tracking data

**Visual:** Short roadmap or checklist

**Speaker notes:** Brief — 30 seconds. The framework is ready to scale; the methodology is proven.

---

## Slide 11: Conclusion
**Three takeaways (one per line, bold):**

1. **Measuring correctness changes everything** — without it, complex tools appear to win
2. **Simple heuristic tools outperform complex algorithms** — both in the paper (6K merges) and our replication (50 merges)
3. **The safest merge is a conservative one** — reporting a conflict is almost always better than guessing wrong

**Visual:** Minimal. Three lines of bold text on a clean background.

**Speaker notes:** Restate the thesis. End strong.

---

## Slide 12: Questions?
**Include:** Repo link, paper citation, your email

---

## Preparation Notes

### The Argument Structure (for rehearsal)
1. **Setup** (Slides 1–3): "Complex tools *should* be better — here's why everyone thought so"
2. **The evidence** (Slides 4–6): "But when you actually measure correctness, they're worse — and here's why"
3. **Our confirmation** (Slides 7–8): "We replicated this independently — same result, even more dramatic"
4. **The lesson** (Slides 9–11): "Simple + conservative > complex + ambitious"

### Key Rhetorical Moments
- **The rug pull (Slide 5):** After setting up the expectation that complex = better, show the data. The 50% incorrect rate for IntelliMerge should get a reaction.
- **The punchline (Slide 8):** "Zero incorrect merges" for git-merge-file vs 97.7% for Spork. Let the numbers speak.
- **The lesson (Slide 9):** Generalize beyond merge tools — this is a cautionary tale about complexity in software engineering research.

### Timing Guide (12 min target)
| Slides | Topic | Time |
|--------|-------|------|
| 1 | Title / hook | 0:30 |
| 2 | Setup: the intuition | 1:30 |
| 3 | Tool landscape | 1:00 |
| 4 | Methodology | 1:30 |
| 5 | Paper results (KEY SLIDE) | 2:00 |
| 6 | Why complex tools fail | 1:30 |
| 7 | Your framework | 1:00 |
| 8 | Your results (KEY SLIDE) | 1:30 |
| 9 | The deeper lesson | 1:00 |
| 10–11 | Future work + conclusion | 1:00 |

### Anticipated Questions
- **"Isn't 50 scenarios too few?"** → Yes, it's a proof of concept. But the direction matches the 6K-merge paper exactly, which strengthens confidence in both.
- **"Maybe Spork/Mastery just need bug fixes?"** → Schesch et al. spent a person-month on Spork bugs and couldn't fix them. Complexity breeds bugs — that's part of the argument.
- **"Aren't there cases where structured tools genuinely help?"** → Yes — Spork handles overlapping method additions well (Section 7.4.1). But the failure modes overwhelm the successes.
- **"What about AI-based merge tools?"** → DeepMerge and MergeBERT exist but aren't publicly available. Interesting future direction.

### Connection to Your Previous Presentation
Your last talk: textual diff → ASTs → ChangeDistiller → GumTree → HyperAST (the evolution toward structural understanding).
This talk's twist: all that structural understanding, when applied to *merging*, doesn't pay off the way you'd expect. The diff side benefits from structure; the merge side is hurt by its implementation complexity.
