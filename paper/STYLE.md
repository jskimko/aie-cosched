# Style guide

Started 2026-10-14 from the portable guide (vault `0-notes/ai-instructions/paper-writing-style.md`, dated 2026-10-01),
which every section of this paper follows. This paper's own terms and standing decisions are at the end; general
lessons learned here go back to the portable guide. Reference papers: FCCM'26 (`~/docs/FCCM26__When_Systolic_Arrays_Meet_AI_Engines/`,
IEEE, the template for this paper) and FPGA'27 (`~/docs/FPGA27__Control_Packet_Reconfiguration.pdf`, the FCPR paper).

## Stages
1. **First draft.** Self-contained and complete: all information is present, so only refinement follows. Numbers can
   be finalized later, but the current ones must be satisfactory. Bold run-in headings give at-a-glance structure.
2. **Restructuring.** Move topics to suit the narrative; trim details that hold little value or confuse, figures and
   tables included, without being dishonest.
3. **Compacting.** Every sentence earns its place; each piece of information is conveyed once, except to highlight key
   points and takeaways. Merge what the run-ins separated.
4. **Final refinements.**

## The evaluation interprets; it does not report
The single most important lesson (author, 2026-10-01, "the big breakthrough in perspective").
- The point of evaluation prose is to **distill trends, patterns, and insights**, i.e., to interpret the results. Look
  across **every applicable run**, not only the latest, and ask what holds in all of them: what sets the cost, which
  regimes exist and where the boundary lies, which lever moves which term, where crossovers fall, what generalizes, and
  what is more or less repeatable.
- Write those patterns down first (in the paper's `STYLE.md`) as the evaluation's message. Each evaluation subsection
  opens with the pattern it supports and ends with it as the takeaway; numbers appear only as support, rounded.
- **Results vary between runs; prose does not churn with them.** A value that moves is a matter for finalizing the
  numbers, never a reason to rewrite a sentence. Per-run values, provenance, and replication status live in `%` comments
  and the vault.
- The patterns also **explain the limits**: state where and why the method misses (e.g., short times where the
  measurement resolution is a large share; quantities that move between runs) rather than defending individual errors.
  This buys room against critique.
- Do not chase effects near the measurement's resolution; state the resolution once, against the scale of the results.

## Presenting results
- **Final state only.** No development history: no "campaign", "registered", "frozen", "post hoc", versions, "we
  predicted", "we expected". State each result directly with its reason where known.
- **Most important results only:** each result is a claim plus the numbers that prove it.
- **Every term the reader meets is defined in the paper, once, in plain words.** No internal jargon (arm, rung, probe
  or flag names, coined labels).
- **Defaults stated once** in the setup; named elsewhere only where they vary.
- **Existing vs added, for every mechanism:** the full requirement, what existing tools or hardware provide, then what
  this work adds.
- **Tables list only what the text introduces**, every entry traceable to a record; no "not tested" placeholders.
- Only claims that reproduce across runs are stated as results; single-run ones are marked in comments.
- One measurement per quantity in any figure or comparison.
- Report both relative and absolute error; avoid thresholds a reviewer could read as convenient.

## Paper structure (FCCM26 shape)
- **Abstract:** high information density; ground in two sentences (setting; the problem), then the thesis, one sentence
  per mechanism with its enabling condition, the key results, and the closing insight. Product names live in the intro.
- **Introduction**, five paragraphs: (1) context, cited platform and workload, the gap ("However, while prior work ...,
  ... has received far less attention."); (2) existing approaches and why they fall short, pointing to Figure 1; (3)
  "In this work, we ...", one sentence per mechanism (what it is, not how) with its headline number; (4) the insight in
  one sentence and the model as "a model that takes X and returns Y"; (5) then "In summary, the primary contributions of
  this work are as follows:" with 3-4 one-sentence noun-phrase items ("A systematic quantification of ...", "The design
  and implementation of ..."), no numbers or section references inside items; engineering contributions as one plain
  sentence after the list. The introduction never reuses an abstract sentence, states takeaways not derivations, and
  has at most one or two section references.
- **Background:** bold run-in paragraphs per component; each term defined in the prose where first used; states only
  what later sections use; Related Work as its own subsection.
- **Design:** opens with one paragraph of the overall scheme; subsections per component.
- **Evaluation:** one setup paragraph (tools, versions, board, how measured), then one subsection per topic, titled by a
  noun; every subsection ends with a takeaway.
- **Conclusion:** one paragraph, 6-8 sentences: what was characterized, what the design recovers, what remains, what
  future hardware should add.

## Paragraphs and intent comments
- A paragraph makes one point: the first sentence states it, the rest support it, the last draws the consequence.
  Body paragraphs run 4-8 sentences.
- Evaluation paragraphs: purpose ("To quantify ..., we ..."), what is shown ("Figure~X shows ..."), the result with
  numbers, the interpretation ("This demonstrates that ..."), and at a subsection's end the takeaway.
- **Intent comments:** every paragraph opens with `% VALUE: ...`, a terse statement of what it must convey. After
  editing, re-read each paragraph against its comment; change a comment only deliberately. Figures, tables, and lists
  carry one too.
- **Review loop:** the author leaves `% COMMENT:` lines in the source; each is answered in the text and the line removed.

## Sentences
- One sentence per source line. Mostly 15-30 words, declarative, subject (the actor) first. No fragments or one-clause
  punchlines.
- Vary openers ("This ...", "To ...", "By ...", "While ...", signposts); never the same device twice in a row.
  "i.e.," / "e.g.," about once per subsection, never in adjacent sentences.
- First person plural: "we", "our", "this work".
- Signposts: *However*, *In particular*, *To mitigate this*, *By leveraging*, *Furthermore*, *Additionally*,
  *Consequently*, *Lastly*, *In summary*. Verbs: *identify*, *quantify*, *characterize*, *demonstrate*, *reveal*,
  *establish*, *leverage*, *mitigate*. Hedge an inference with *suggests* / *indicates*, never a measurement.
- At most one semicolon per paragraph; no appositive chains; no colon "reveals"; no em-dash asides; parentheses only for
  abbreviations, short examples, and figure panels. Oxford comma always.
- Properties referenced across sections get short names in words, italicized where defined, never coded labels.
- A named concept is introduced once, capitalized, in quotes on first use, and unquoted afterwards.
- Abbreviations are expanded on first use in the abstract and again in the body.

## Wording lessons
- **Density over brevity:** shorten by merging sentences, never by dropping facts or causes.
- **One structure per sentence:** split a sentence with several turns into two clean ones.
- **Say exactly what holds:** no extreme or universal phrasing, right modality ("can be", not "is", when optional), no
  trend words without evidence. Keep claims that differ apart.
- **Observed properties, not intent:** state what the system does, never what it was or was not designed for.
- **Term variants:** the defined form where defined and where a section first uses it; close variants that keep the
  head noun are fine elsewhere; a variant that changes the head noun is a new term.
- **Clear referents:** no ambiguous "its"/"this"; no stacked relative clauses.
- **Phrase limitations as limitations** ("it can hold only").
- **No superlatives**, not even once.
- **Plain titles:** nouns naming the topic, never a claim, question, or phrase. Prefer a bold run-in paragraph to a
  thin subsection.
- No unnamed "the toolchain": name the cited tool or say nothing.

## Numbers
- The introduction carries 2-4 headline numbers, rounded; the evaluation gives exact values with CIs.
- Ratios as `$1.28\times$`; percentages to one decimal where measured; units with a thin space.
- A number always names what it compares against.
- Outside the evaluation, prefer relative numbers to raw values.

## Figures and tables
- Figures use the paper's own font via matplotlib usetex (IEEEtran sets Times: `\usepackage{newtxtext}\usepackage{newtxmath}`,
  as in `figs/make_figs.py`); labels are LaTeX. No font files in the repo.
- Classic print style: thin closed frame, short inward ticks on all four sides, no grid, thin lines, small markers,
  frameless legends. Each series keeps one line style, marker, and color in every figure, so a figure reads in grayscale.
- A color-blind-safe palette (e.g., IBM's, shifted and softened), medium step for lines, pastel step for areas; close
  pairs never share a figure; check new pairings with a CVD validator.
- Figure text in sentence case; codes keep their form.
- Captions state what is shown, panels as "(a) ...; (b) ..."; they state what the error bars are, not the claim.
  Table captions in Title Case or a short noun phrase.
- Tables span the column width (`tabular*` with `\extracolsep{\fill}`), notes wrap at the table width.
- Prefer one figure serving two sections over a second figure; two or three numbers go in a sentence.
- Render candidates in the real medium before choosing a figure's form.

## Citations
- Place a citation right after what it references: after a work's name when the sentence names it, otherwise after the
  claim. Every citation supports exactly its sentence: read the cited PDF, not a summary, and use the source's own terms.
- Cite only what the text uses; no uncited bib entries, no `note` fields. Prefer the official published version.
- Architecture facts cite vendor sources; a fact no manual states may cite the defining source code, file and value in
  a `%` comment. Software as `@software` with the repository's name and description; living docs as `@misc` with
  `lastaccessed`.
- Cite research works; cite the toolchain once as software. PR numbers, flags, commits, and code identifiers stay in
  `%` comments.
- Each cited work gets a vault source note (`5-sources/`) with the passages the paper relies on.
- Double-blind: the authors' prior work is cited in the third person.

## Related work
- One bold run-in paragraph per group of works; each work or group gets one sentence with its takeaway; do not explain
  how they operate. Each paragraph ends with one sentence contrasting the group with this setting (how the setting
  differs, not a finding). No separate "what is new" paragraph.

## Mechanics
- Self-contained for Overleaf: `main.tex` at the root, no `../`, one `refs.bib`, `build/` the only ignored path.
- The agent never runs the LaTeX build; the author's watcher does. Read `build/main.log` for errors.
- Dropped content is commented out with a `% DROPPED (<date>): <why>` line, not deleted.
- No AI trailers in paper commits.


## This paper

**Venue.** IEEEtran conference, double-blind: FCCM'27 (~early Jan 2027, inferred) or ISPASS'27 (~mid-Dec 2026,
inferred). Preamble follows the author's FCCM'26 paper. `main.tex` lives in `paper/`, and a public release of the repo
excludes `paper/`.

**Stage.** Stage 1 (first draft) of the scope-independent parts: background, the command-processor model and
formulation, the method, and the experimental setup. The title, abstract, introduction, evaluation results, and
conclusion are placeholders (`\E{...}`) until the decode-half and agent-step results land and the headline numbers
pass an independent audit.

**Framing (standing decisions, 2026-10-14).**
- Method-first. The contribution is the model, the formulation, legality, and the automatic composition. Never phrase
  a result as "N× over AMD's code"; the existing design is "the existing prefill" or "the baseline", described
  neutrally, and a later hand fix by its authors becomes a hand-optimal reference, not a refutation.
- Packing several operators into one command (batching) is standard practice and is cited as such (CUDA Graphs, XRT
  run lists, MLIR-AIR's stitched programs). Our part is the joint choice of what shares a command and the CP's order.
- FCPR (the author's FPGA'27 submission) is cited in the third person, for the command-processor primitive only, in
  one background sentence. No text or figures are reused from it.
- Report the essential decisions (spatial assignment, CP instruction order) separately from the host-boundary
  handling (queue depth, packing), which would vanish if host work moved onto the array.

**Terms (defined once in the paper; use these words).**
- *command*: one submission to a hardware context, carrying one instruction stream.
- *issue* instruction, *synchronization*, *address patch*, *argument slot*, *dispatch floor*, *hardware context*
  (Section 2).
- *column group*: the columns one operator drives (GEMMs: columns 1-6; attention: columns 0 and 7, one group each).
- *segment*: synchronizations followed by the issue instructions they gate.
- *predicted completion* order (Section 4.4); *arenas* (Section 4.3); *boundary cost* epsilon (Section 3.2).
- Not in the paper: arm names (edf, naive, Ar, q2, g4, b4), "composer v1/v1.1", "pre-registered", "frozen",
  "projection", "planner", "lag" (say "commands in flight" / "D positions earlier").

**Numbers.** Every number has a `%` comment with its source (`repo@hash:path` or the lab entry). Figure data is copied
into `figs/data/` with provenance in `figs/README.md`; table rows that come from data are generated
(`paper/fig/params-rows.tex`).

**Open items for the author.**
- How to cite FCPR while it is under review (`refs.bib`, `fcpr2027`).
- Entries marked VERIFY in `refs.bib` need their sources read and a vault source note each.
- NP-hardness of the formulation is not claimed until a reduction is written (`3-model.tex`, TODO(hardness)).
