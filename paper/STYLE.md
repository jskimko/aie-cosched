# Style guide


## Before any text pass
- **Read every rule first**, Wording lessons and the paper's Per-paper decisions in full, not only the section for
  the current stage; then check the diff mechanically for every banned word and phrase (a script that scans each
  change).
- **Rework in context.** A sentence is fixed together with its paragraph (for the abstract or conclusion, the whole
  section), so that emphasis, repetition, and flow stay right; a local patch can turn a qualifier into the frame or
  repeat what the neighbor says.
- **Restructure, don't drop.** A sentence that reads badly is restructured so every fact stays. List the old
  sentence's facts and check each is in the new one or say where it moved; a cut is offered only as a separate,
  labelled option.
- **Fix the substance, not the wording around it.** For each finding, state in one line what is actually wrong (a
  claim outside the data, a model that disagrees with a measurement) before editing. Prefer wording that every source
  supports, or new data, over a caveat or a narrowed scope; a caveat is never presented as a fix.
- **A caveat needs a wrong claim.** Before adding a caveat, qualifier, or condition, quote the stated sentence the
  finding makes wrong and check that its subject and scope cover the finding. Verifying a number is not showing that
  the text is wrong; a definition is not contradicted by a regime the paper never evaluates.
- **Re-check a reworded claim's scope.** A number can stay correct while the words around it overclaim. Re-derive
  what the number counts from its source, and check every other place the paper states the same result.
- **The paper describes the current implementation.** Check a source-backed claim against the implementation's
  current head, and describe that state only, with no wording that straddles old and new behavior.
- **Value means supporting a main claim.** Before proposing a cut, write the claim the line supports (or "none").
  Lines that support a headline result, the key insight, the model's accuracy, a correctness argument, or a
  contribution are high value: they may be compressed with their meaning kept, never cut. Only "none" lines go.
- **Standard before our own rule.** Where a question is about convention, find the field's practice first (peer
  papers, counted where possible); a rule of our own is offered after it, labelled as a suggestion. Never justify a
  choice by consistency with a default we set ourselves.

## The evaluation interprets; it does not report
The single most important lesson (author, 2026-10-01: "the big breakthrough in perspective").
- The evaluation's prose distills **trends, patterns, and insights** that hold across **every applicable run**, not
  only the latest: what determines the cost, which regimes exist and where the boundary lies, which lever moves which
  term, where crossovers fall, what generalizes, and what is more or less repeatable.
- Write those patterns down first, in the paper's `STYLE.md`, as the evaluation's message. Look for **one unifying
  insight** that every method and every step is read through (ctrl-pkt: reconfiguration time is the command
  processor's critical path), with the patterns as its consequences: what each method pays for; why the kinds of
  method are limited by different things; what each step removes; which regime decides which lever matters; where a
  crossover falls by size.
- Each evaluation subsection supports one pattern; numbers appear only as support, rounded.
- **Results vary between runs; prose does not churn with them.** A value that moves is a matter for finalizing the
  numbers, never a reason to rewrite a sentence. Per-run values and replication status live in `% SOURCE:` comments
  and the vault.
- The patterns also **explain the limits**: state where and why the method misses (short times where the
  measurement's resolution is a large share; quantities that move between runs) rather than defending individual
  errors. A model's claim is its structure (the right ordering and regime, errors small against the scale of the
  results), not any one constant.
- Do not chase effects near the measurement's resolution; state the resolution once, against the scale of the
  results. An effect that changes no claim and stays within the resolution is left out of the text; the record keeps
  it. Platform timing the method cannot attribute is disclosed generally (size and scope, no invented cause).
- **Relative numbers from the start** (below, § Numbers): they keep the prose on patterns rather than on a benchmark
  dump.

## Conveying information
How a passage conveys its information, not its word choice. The measure is information density, reached losslessly
while keeping flow and clarity.

Every section:
- **Lossless, judged by job.** A phrase goes only when the rest of the text truly implies it. Before cutting a
  sentence as a repeat, name its job: a contrast with existing work, a motivation, the emphasis of a key insight or
  claim, or the other side of a trade-off. If it has one, it stays.
- **Cause, then response.** A mechanism comes with the property or problem that requires it. The reason must be the
  real cause, not a consequence of the mechanism.
- **The verb claims exactly what holds.** A step that shortens waiting does not "cut the count" of waits if every one
  still happens; name the actor that actually does it. A name for a mechanism is not its reason.
- **One causal unit per sentence, by default.** An argument and its evidence get two sentences; a clause that answers
  a different property does not hang off a "so" it does not follow from. It is a default, not a cap: two closely
  linked units may share a sentence that reads in one breath. Split a sentence that stacks several turns ("…, so …,
  and …, so …"); a short sentence is fine, a run of choppy ones is not. Vary the form ("Because X, Y", "X, so Y",
  subject first, "where …"); no device three times in a row unless the content is parallel.
- **Core terms fixed, structure varied.** A core term keeps one name across sections; up to two semantically adjacent
  words are acceptable case by case where clarity is not lost. No new undefined term. Where context makes the
  meaning obvious, the short form gives variety ("configuration" for "configuration data").
- **Ownership explicit.** The reader can tell what exists from what this work adds ("the existing path", "our
  teardown protocol"), with strong active verbs for our actions ("we time-share", not "we let").
- **Scope and referents.** Evidence states its scope ("every evaluated dispatch, on both paths"). A claim that holds
  only in a regime puts the general claim first and the bounded exception last ("…, except at large payloads").
  "This", "it", and "that" refer within the same or the previous sentence.
- **Sources scoped.** Say only what the cited works show, scoped to them ("the CGRAs in §2.3"), never a field-wide
  claim from a few papers or one paper's detail as the group's; an inference of ours is not their guarantee.
- **Model wording once per context** (papers with a model). Say "by the model" (or "estimated", "predicted") where the
  text turns from measurements to the model, and again only once that context has worn off.
- **A setup choice gets one plain reason**, in one clause, that holds everywhere it claims and invites no weakness;
  the mechanism behind it lives in the section that owns it.

Abstract:
- High level. A reason stays only where a core concept is not understandable without it and nothing later in the
  abstract supplies it. Its core concepts stay together in one sentence.
- *Guideline:* one link from a finding back to our work, on the key insight, with the finding's own "why".

Introduction:
- The only place that sells the work, in a measured way, through contrasts and reasons: why the work matters and why
  it is hard. Each mechanism says what is ours and why.
- A discovery is stated plainly with its reason, not as "we find"; the contribution leads its sentence and its reason
  follows.
- Link findings back to our work sparingly; once shown, it is not repeated.
- *Guideline (systems and hardware papers):* name the capabilities the existing approach leaves unused and this work
  uses; it shows nothing is left on the table and lets adjacent work recognize the same problem.

Background:
- A sequence of facts, each once, in the order later sections need them, with a brief contrast with our work where it
  matters ("…, whereas we … (§3.3)").

## Deduplication and compression
The goal is no redundancy and no verbosity, with nothing lost (the pass itself: [[paper-writing-process]]).
- **Deduplicate meaning, not words.** A meaning is conveyed once, however it is worded. A repeat is placed only on
  purpose, for a high-value meaning (a key concept, insight, or result); any other repeat becomes a reference
  ("(§4.2)"). Statements of one meaning form a family; within it, a repeat becomes a reference only where its home's
  scope, condition, and evidence cover it. A repeat is removed without a reference only with the author's approval,
  where a pointer would add nothing and its scope matches its home's. Where a repeat is the premise of a local
  argument, the shortest phrase that carries it stays.
- *Guideline:* a key meaning is stated once where it is argued, once where each new kind of evidence is shown, and in
  the summaries; a further statement that adds no support is repetitive.
- **Summaries by design.** The abstract, the introduction, and the conclusion recap the paper; a recap there is not a
  repeat to remove. Each is judged by its purpose, and within each a meaning is stated once (the contribution list may
  restate the introduction's paragraphs).
  - The **abstract** is a self-contained, high-level overview that states the problem and sells the work through its
    high-impact facts, without overclaiming. It names no toolchain repository and no benchmark labels.
  - The **introduction** grounds the context, motivates the problem and names the gap in prior work, covers our
    contributions as its solutions, and highlights the key results and insights, concretely where that serves it.
  - The **conclusion** summarizes the insights and takeaways at a high level and states what remains and what it
    implies. It stands alone: no benchmark or design-point labels, only the headline numbers and what justifies each
    key claim ("a dispatch of our full-array microbenchmark"); a workload is named only where its headline needs it.
- **Captions** stay self-contained: no pointers.
- **Compress losslessly, in intent, meaning, and clarity.** Value every sentence at four scopes: its neighbors (what
  it takes and hands on), its paragraph (topic, support, evidence, consequence, handoff), its section (which claim it
  carries), and the paper (which key claim, insight, definition, or headline number it carries). Then consolidate
  sentences of similar meaning and merge paragraphs that continue one topic. Merge rather than drop; never drop a
  condition, a scope, a cause, or the evidence a claim rests on ("nearly", "in our evaluation").
- **Numbers are not redundant by default.** A number goes only if another number states the same measure; a
  conventional metric and our qualified version of it are different measures, and so are a size and its reason.
- **Check every change both ways.** Before the change, list the passage's meanings (claims, numbers with what they
  compare against, definitions, conditions, causes, links between sentences). After it, extract the meanings from the
  new text alone and compare both ways: each old meaning is kept with the same strength and scope (or is implied by
  the new text, written out and confirmed by an independent check), each link survives, each defined term names the
  same thing, and nothing new is added. Restore anything lost before the change stands. Numbers, references, and
  citations are diffed mechanically. A merged sentence still has one structure.
- **Comments are part of every pass.** Each `% VALUE:` is rewritten to the paragraph as it now stands, `% SOURCE:`
  comments move with their numbers, and stale comments go (§ Intent comments).

## Paper structure
*Guideline:* the FCCM26 shape, below; the paper's content may change it, with the reason recorded in its `STYLE.md`.
- **Abstract:** high information density. The setting and the problem, the existing approach, the mechanisms, the
  insight, the model and its accuracy, the key results against the best prior or shipped approach, and the closing
  insight. Keep the mechanism terms; product names live in the introduction.
- **Introduction**, five paragraphs:
  1. *Context.* Cited platform and workload; why the problem arises (keep the cause, e.g. "because the array is
     small"); cited evidence that it costs; end on the gap: "However, while prior work …, … has received far less
     attention."
  2. *Existing approaches* and why they fall short, pointing to Figure 1.
  3. *This work.* "In this work, we …"; one sentence per mechanism ("First, …", "Second, …"), what it is and why it
     is needed, not how, with its headline number in the same or the next sentence; the combined result last
     ("Together, these make …").
  4. *Insight and model.* What bounds the cost, at a high level; the model as "a model that takes X and returns Y",
     and its accuracy.
  5. *Contributions:* "In summary, the primary contributions of this work are as follows:", then 3-4 one-sentence
     noun-phrase items ("A systematic quantification of …", "The design and implementation of …", "A … model that
     …", "An architectural analysis of …"), naming constraints plainly. No numbers, section references, or
     sub-clauses beyond one "that …" or "by …" inside an item. Engineering contributions (toolchain integration,
     availability) follow as one plain sentence.

  Rules within this shape: the introduction never reuses an abstract sentence, covering the same points in new words
  and more depth; it states takeaways, not their derivation; it mentions a result in retrospect at most once; it has
  no bold run-ins and at most one or two section references; labels defined only in the evaluation appear neither in
  it nor in its figures.
- **Background:** platform subsection with run-ins per component; each term defined in the prose where first used,
  no glossary; states only what later sections use; Related Work as its last subsection.
- **Design:** opens with one paragraph of the overall scheme, then one subsection per component. *Guideline:* build
  the opening as the system's properties, each followed by the mechanism that answers it, with one subsection per
  property; steps that answer one property together are run-ins within it.
- **Model** (if any): "In this section, we present …"; the processes, the form, the constants.
- **Evaluation:** one setup paragraph (tools, versions, board, how measured, the defaults), then one subsection per
  topic, titled by a noun.
- **Discussion** (optional): implications beyond this platform and a conditional outlook, transferable insights only,
  each tied to a measured result and every sentence serving one. It does not recap the work. Each insight is a
  possibility under its condition ("where …", "may", "could"), never an absolute ("any", "wherever … would"). Each
  limit still sits in the section that owns its topic, and the conclusion then keeps no outlook.
- **Conclusion:** one paragraph: the insights and takeaways at a high level, what remains, and (hardware papers) what
  future hardware should add. *Guideline:* 6-8 sentences.

## Paragraphs
- A paragraph makes one point: the first sentence states it, the rest support it, the last draws the consequence or
  hands off. *Guideline:* 4-8 sentences.
- **Takeaways.** An evaluation subsection states its insight in its opening sentence, and only where the insight is
  high-impact. A closing paragraph that only restates is a repeat. *Guideline:* where no insight opens it, an
  evaluation paragraph runs purpose ("To quantify …, we …"), what is shown ("Figure~X shows …"), the result with
  its supporting numbers, and the interpretation.
- **Run-ins** mark one item of a complete set of parallel items that the reader looks up, compares, or reaches from a
  table (paths, groups of related work, a table's steps or process groups). Every item of the set is labelled, and no
  unlabelled paragraph sits among them. A step too small for its own paragraph joins the step it enables under one
  label naming both. Paragraphs that are steps of one argument get no label: a subsection or the first sentence
  carries the shift, with the defined term in italics where introduced. A label names a thing or concept, as a Title
  Case noun phrase (`\textbf{CGRA Configuration.}`), never a situation; no "Takeaway" run-ins. *Guideline:* none in
  the introduction, setup, or evaluation. Calibration (2026-10-05, arXiv LaTeX, live labels, paragraphs of 25+
  words): FCCM26 15 of ~61 paragraphs, six peer papers 4-25%, mostly in related work and component lists. Count live
  labels only; commented-out ones once inflated a count to "21 of 21".

## Intent comments
Every paragraph opens with `% VALUE: …`, a terse line (fragments fine) stating what it must convey, not how; e.g.
`% VALUE: CP path = out of band, reset + serial; in band fits (local, parallel); existing = delivery demo only`.
After editing, re-read each paragraph against its comment; a paragraph that no longer matches is rewritten, or its
comment is changed deliberately and the commit says so. Figures, tables, and lists carry one on their first line, plus
at most one per section or subsection. It describes the current paragraph only: no session or author tags, no
history.

The source keeps five kinds of comment:
- `% VALUE:` as above.
- `% SOURCE:` where a number or checked fact comes from (a run's results, a file and line, a PR or commit, a count or
  derivation, a cited page, the raw value behind a relative number), after the sentence, inside the figure or table,
  or once per paragraph. It is updated with its number, goes when the number leaves the text, and a wrong value is
  corrected against its run. It may name reproducer scripts and labels; the text may not.
- `% DECISION:` a choice the text must keep or a claim it must not make, present tense, on the paragraph it governs,
  no session tag. A decision the current text contradicts goes to the author.
- `% COMMENT:` the author's review lines, until answered in the text and removed.
- Build lines: `%%` template comments, `%TC:` TeXCount directives, a commented-out build switch, and macro or
  hyphenation notes, without history.

Everything else is removed from the source and copied verbatim to the vault: dropped or replaced text (commented-out
prose included), earlier methods, review notes, session or author tags. A line that mixes kinds is split by kind;
removing commented-out prose also removes any `refs.bib` entry only it cited. An open check in a comment
("[inference …; verify]") is listed for the author, never removed silently.

## Sentences
- One sentence per source line.
- Declarative, the actor first; no fragments and no one-clause punchlines. *Guideline:* mostly 15-30 words, varied.
- **Calculated phrasing.** Vary openers (FCCM26 mixes "This …", "To …", "By …", "While …", and signposts); never the
  same device twice in close succession, and a signpost repeats only after a few paragraphs.
- "i.e.," and "e.g.," are never in adjacent sentences. *Guideline:* about once per subsection, inside parentheses
  (an AMD internal review's house style; "That is," and "For example," may open a sentence instead).
- First person plural: "we", "our", "this work".
- Signposts: *However*, *In particular*, *To mitigate this*, *By leveraging*, *Furthermore*, *Additionally*,
  *Despite this gain*, *Consequently*, *Lastly*, *In summary*. Verbs: *identify*, *quantify*, *characterize*,
  *demonstrate*, *reveal*, *establish*, *leverage*, *offload*, *mitigate*. Mark an inference with *suggests* or
  *indicates*, never a measurement.
- Punctuation: no appositive chains; no colon "reveals"; no em-dash asides; parentheses only for abbreviations,
  "(i.e., …)" and "(e.g., …)" asides, figure panels, and section references; Oxford comma always. *Guideline:* at
  most one semicolon per paragraph.
- Properties referenced across sections get short names in words, italicized where defined (a *clean state*, a
  *global order*), never coded labels (G1-G3).
- A named concept is introduced once, capitalized, in quotes on first use (FCCM26: the "Systolic Tax"), defined in
  Background, and unquoted afterwards.
- Abbreviations are expanded on first use in the abstract and again in the body.

## Wording lessons
- **Density over brevity.** Shorten by merging sentences, never by dropping facts; a sentence that loses its cause or
  its mechanism terms is worse.
- **One structure per sentence.** Split a sentence with several commas and turns into two clean ones. Avoid abstract
  subjects ("every change of design reconfigures the array"); put the actor first.
- **Say exactly what holds.** No extreme or universal phrasing, the right modality ("can be shared", not "is shared",
  when optional), no trend words without evidence ("increasingly"). Keep claims that differ apart.
- **Observed properties, not intent.** State what the system does, never what it was or was not designed for.
- **Term variants.** The defined form where defined and where a section first uses it, one form per object within a
  paragraph. Elsewhere, close variants that keep the head noun read less mechanically; a variant that changes the
  head noun or could name another mechanism is a new term.
- **Mirrored structure is a judgment call.** Parallel openers suit parallel content; vary the opener where a sentence
  does a different job. Actor first outranks a varied opener.
- **No bare appositives.** Never set off a noun phrase with commas without a connecting word ("designs, each a single
  configuration"). Connect it (", where each …", ", which is …", "namely", "which we call"), give it its own clause,
  or attach a symbol or short name directly ("the \emph{in-band cost} $\delta$"). The same holds for absolute
  phrases and trailing participle clauses (", keeping …"): give them a finite verb or their own sentence, unless the
  clause reads smoothly ("…in one transfer, shrinking the payload that the host holds").
- **Clear referents.** No ambiguous "its" or "this way"; no stacked relative clauses ("whose … and whose …").
- **Phrase limitations as limitations** ("it can hold only", "must be partitioned").
- **No superlatives** ("fastest", "best"), not even once; let the results speak.
- **Plain titles.** Every section and subsection title is a noun naming its topic ("Related Work", "Model
  Accuracy"), never a claim, question, or phrase. Prefer a new paragraph to a thin subsection.
- **Who does what.** The existing toolchain ("the compiler", "the toolchain" referring back to a named, cited tool)
  names the existing state only; what this work adds is attributed to us. The paper presents an approach, so vary
  the subject: "we" for key steps, "our passes" for an automatic check or transformation, or the mechanism itself.
  Never "our compiler passes [verb]" (a garden path). No unnamed "the toolchain": name the cited tool or say nothing.
- **Current state only, also for open work.** Planned work changes the wording only once it is done.
- **Name what the result enables, not an agent we imagine** ("the model can estimate, before a program runs, …", not
  "a partitioner can …").
- **Banned words**, in text and comments: "provenance", "held-out" / "hold-out" / "held out", "hedge" (internal or
  AI-sounding; say "where a number comes from", "configurations not used to build the model"); "set the time" (vary:
  "govern", "determine", "account for little of", "become the limiting factor") and "dominate" except in the author's
  own text; "knee" (AI-coded). Also avoid a term that means something else in a neighboring field (ctrl-pkt: "epoch",
  from AI training).

## Numbers
- **Relative numbers, from the first draft** (author, 2026-10-14: reads better than a raw benchmark dump). Choose the
  reference units when the setup is fixed and draft every time in them: the baseline's time on the headline
  configuration ($\tau$) for microbenchmarks, the baseline's time per output unit (per token) for a real workload, a
  model's base constant for its tables. Figures plot normalized time, which keeps shape, additivity, and slopes, and
  are labelled as normalized time, not speedup. The text gives ratios and shares, and the unit itself only for a
  magnitude with no partner. Raw values live only in `% SOURCE:` comments and the record; flag them before any
  release of the reproducer. A draft that already carries raw values gets a conversion pass before the evaluation's
  prose is refined (ctrl-pkt converted on 2026-10-06, for a co-author's employer, and the conversion meant rewriting
  §3-§5).
- A number always names what it compares against.
- Ratios as `$1.28\times$`; percentages to one decimal where measured; units with a thin space (`312~MHz`); one
  convention for significant figures, chosen by the field's practice.
- **Which numbers the text carries.** A number appears only as a headline, a comparison that supports a claim, a
  reference (a unit, the resolution), an attribution (why a result happens: "272 commands against 2,304"), a
  boundary (where a regime or winner changes), or a bound that shows a cost is negligible. Values the figure already
  shows stay in the figure. An outlook beyond the device is a suggestion or open question ("may", "would"), never a
  result.
- Rounded everywhere; an interval only where a claim reads it. *Guideline:* the introduction carries 2-4 headline
  numbers.

## Presenting results
- **Final state only.** No development history: no "campaign", "registered", "frozen", "fresh test", "post hoc",
  "miss", model or method versions (software versions in the setup are facts), "we predicted", "we expected", "would
  have refuted". State each result directly, with its reason where known; history lives in the vault.
- **Most important results only.** Each result is a claim plus the numbers that prove it (a model: correct ordering
  and its median error on data it was not fitted on, against the measurement's uncertainty). Limitations and unknown
  causes are stated concisely where their topic lives, each with its size and scope.
- **Every term the reader meets is defined in the paper, once, in plain words.** No internal jargon (arm, campaign,
  rung, probe or flag names, coined labels). Prefer showing the measurement directly; a needed derived quantity is
  defined in one sentence and then used by its plain name.
- **Defaults stated once** in the setup and named elsewhere only where they vary.
- **Existing vs added, for every mechanism:** the full requirement, what existing tools or hardware provide, then
  what this work adds.
- **Tables list only what the text introduces**, every entry traceable to a record; no "not tested" placeholders.
- Only claims that reproduce across runs are stated as results; single-run ones are marked in comments.
- One measurement per quantity in any figure or comparison; report both relative and absolute error; avoid
  thresholds a reviewer could read as convenient.
- **No reproducer details in the text.** Script names, folder paths, and run labels belong in the reproducer's docs;
  the paper states every method itself and never defers content to the artifact.

## Figures and tables
- Figures use the paper's own font via matplotlib usetex (for ACM: `\usepackage[tt=false]{libertine}
  \usepackage[libertine]{newtxmath}`), set once in the figure script; labels are LaTeX (`\textmu s`, no bare `%`,
  `&`, `_`). No font files in the repo.
- Every figure is generated by a script from result files, never typed in.
- Classic print style: thin closed frame, short inward ticks on all four sides, no grid, thin lines, small markers,
  frameless legends. Each series keeps one line style, marker (open or filled), and color in every figure, defined
  once in the figure script, so a figure reads in grayscale.
- Color: a color-blind-safe palette with no stock Office or matplotlib hues and no colors outside the set; the
  medium step for lines and markers, the pastel step of the same hue for areas; close pairs never share a figure,
  and any new pairing is checked with a CVD validator. *Guideline:* baselines near-black, our variants in IBM's
  palette shifted and softened in OKLCH, neutral grays for non-method segments.
- Figure text in sentence case; codes keep their form.
- Refer to them as `Figure~\ref{}`, `Table~\ref{}`, `\S\ref{}` (ACM).
- *Guideline:* Figure 1 shows the existing approaches with ours beside them, labelled "(ours)" there only; one figure
  serving two sections beats a second figure; two or three numbers go in a sentence.
- Render candidates in the real medium before choosing a figure's form, in a scratch copy while the author is still
  choosing; render and ask before dropping a meaningful element.

Refining figures (each bracket says how the rule applies to tables):
- **Every caption phrase earns its place.** Self-contained (no pointers), opening with what is shown ("Median time per
  dispatch for (a) … and (b) …"), panels named first, plain grammar. State only what the reader cannot decode from
  the figure: never repeat an axis title, legend entry, tick-visible value, or drawn label. A reference mark gets its
  "so what", not just its definition. Never the claim. [Tables: a short noun phrase or Title Case caption; headers
  carry names and units; a note states only what a header or label cannot.]
- **Statistics live on the plot.** The caption names the estimator ("Median"); a key in empty space explains the
  error bars ("95% CI"). Show bars only where visible and meaningful. A key's glyph matches its marks and is
  recognizable alone. Nothing floats over data. [Tables: one estimator stated once; intervals only where a claim
  reads them.]
- **Labels are unambiguous and consistent across the paper.** Panel letters only when the text cites a panel; a
  label never names two things; one counting convention; axis titles say what is measured; a subplot title replaces
  a repeated axis word. [Tables: same conventions as figures and text.]
- **Order by the reader's intuition.** Existing approaches in a fixed order; legends row by row in stacking order;
  groups in the order the text discusses them. [Tables: rows likewise.]
- **Show the quantity that isolates the claim, measured, from one stated configuration.** Measure a missing baseline
  instead of labelling it; a label stays true under the paper's own definitions; a workload has one size, stated
  once; an ordering a schematic claims is backed by current data. [Tables: every entry traceable to one record at the
  configuration the caption names.]
- **Account for every outlier where the figure is introduced**, each named where its topic lives. [Tables: an entry
  that departs from the stated pattern is explained beside it or in the note.]
- **Legible at print size.** Solid fills, not hatches, for thin segments; white separators on slivers; adjacent fills
  CVD-checked; no crowded tick labels at panel boundaries.
- **Consistent across figures and checked against the text.** A convention applied to one figure applies to all;
  every change re-checks the text, the alt text, and the source comments about it.
- **Alt text (`\Description`) gives the content, not the encoding:** what happens, key values, the outcome, in caption
  voice and plain words ("percent", "microseconds"); never "colored blocks are", "Top:"; no repeat of the caption.
  Re-check its values whenever the figure changes.
- **Decide on the merits for the reader**, not on consistency with a default we set; consistency decides only where
  the paper states a convention for a reason.
- **Re-QA every change.** After a figure passes QA, every later change goes back through a reviewer that measures (a
  vector trace, e.g. `mutool draw -F trace`, and a 1200 dpi render) before it is called done; the author's choices
  are marked as decisions so the reviewer checks their execution.

Tables:
- Span the column width (`tabular*` with `\extracolsep{\fill}`); notes wrap at the table width.
- **A label names the quantity; the text states the condition.** A condition in a label reads as per-unit or invites
  a contradiction with a footnote. An index the value ranges over is named ("Reset, *W* columns").
- **Labels are concise and exact:** cut words the reader does not need, one word per meaning in a table, spell out a
  term the text no longer defines.
- **A who-column is exact:** name every member in the table's order, not a description the reader must resolve.
- **A count states its scope** ("3 per column" against "3 in total"); a column holds one quantity.
- **Units in a header row**, not in cells or notes.
- **Notes short and exact**, ideally one line each, the general note first; a note says where a value comes from when
  a header cannot, explains a departing entry, and drops what another table already says. Watch "and" vs "or".
- **Symbols intuitive and unambiguous:** upper-case subscripts name a kind, lower-case a per-unit cost matching the
  equation's variables; one letter never names two things.
- **Investigate a surprising entry before wording around it**; the table then states the general rule, and a
  toolchain finding goes to the backlog, not the paper.

## Citations
- Place a citation right after what it references: after a work's or tool's name when the sentence names it,
  otherwise after the claim. Name works where the sentence refers to them.
- Every citation supports exactly its sentence: read the cited PDF, not a summary, use the source's own terms, and
  reword to what it says or drop the claim.
- Cite only what the text uses; no uncited `refs.bib` entries, no `note` fields. Prefer the official published
  version; a longer preprint only for content found only there.
- Re-citing follows the field's convention: re-cite a tool in the evaluation setup, re-cite per section for a new
  claim, never twice within a paragraph.
- Architecture facts cite vendor sources (manuals, register references, the vendor's kernel docs); a fact no manual
  states may cite the defining source code, with file and value in a `% SOURCE:` comment.
- Software as `@software` with the repository's own name and description as the title; living docs as `@misc` with
  `lastaccessed`; proceedings carry `publisher` and `address`.
- Cite research works; cite the toolchain once as software. PR numbers, flags, commits, and code identifiers stay in
  `% SOURCE:` comments.
- Double-blind: the authors' prior work is cited in the third person.
- *Guideline:* each cited work gets a vault source note (`5-sources/`) with the passages the paper relies on.

## Related work
- Lives in its own Background subsection; the design refers to it rather than citing inline.
- One run-in paragraph per group of works; each work or group gets one sentence with its high-level takeaway (a
  second must be justified); do not explain how they operate.
- Each paragraph ends with one sentence contrasting the group with this setting: how the setting differs, never a
  finding or design consequence a later section derives. No separate "what is new" paragraph.

## Mechanics
- Self-contained for Overleaf: `main.tex` at the root, no `../`, one `refs.bib`, `build/` the only ignored path.
- The author's LaTeX watcher owns `paper/build`; an agent builds only into a scratch directory of its workspace (to
  check fit, layout, or a figure) and reads the log there.
- Once co-authors edit in Overleaf, Overleaf is the official copy and the local repo its commented mirror; the
  editing loop is in [[paper-writing-process]] § *The Overleaf loop*.
- Dropped text leaves the source (§ Intent comments) and goes verbatim to the vault, with the pass's sheet.
- No AI trailers in paper commits.

## Per-paper decisions
Copied from the portable guide (vault `0-notes/ai-instructions/paper-writing-style.md`, regenerated 2026-10-14) on
2026-10-14; how the paper is written phase by phase is the vault note `paper-writing-process`. Reference papers:
FCCM'26 (`~/docs/FCCM26__When_Systolic_Arrays_Meet_AI_Engines/`, the IEEE template) and FPGA'27
(`~/docs/FPGA27__Control_Packet_Reconfiguration.pdf`, FCPR). Entries marked *proposal* wait for the author.

- **Stage, structure, framing and baseline (2026-10-24; supersede the entries below where they differ):** the spine
  is the vault's `paper-cosched-spine-v18` (the author chose the lead on 2026-10-24: the system leads, and a condition
  is the finding). Structure: 1 Introduction; 2 Background; 3 Motivation; 4 When a False Order Costs Time (the
  condition; exposure, the cut and the shape; where the stacks meet it); 5 Scheduling a Compiled Design (analysis and
  legality, closed binaries read and bounded); 6 Pricing Schedules (formulation, bound, the event model in its rebuilt
  form, the guarantee on the difference between candidates, the tie-break measurement); 7 OPCORD (composer, stream
  pass, loop pass, choosing the order and the split per prompt length, checkers); 8 Evaluation; 9 Related Work;
  10 Conclusion. Contributions: four items (the analysis method, the condition, the event model and bound, OPCORD).
  The baseline is the existing program on the shipped split that minimizes its TTFT, run on the faster of its own
  host code and our runner; the hand-alternated baseline is retired. FastFlowLM, taken as released, is an
  observation for the condition only, never a speedup reference and never "hand-tuned" or "expert". Appends and agent
  turns are an extension and stay out of the body. The text before this rewrite is archived verbatim in the vault
  (`archive-tex-2026-10-24`).
- **Contribution list** (author, 2026-10-24; supersedes the noun-phrase item form and the contribution items above
  where they differ): three items, in MLSys form ("We + verb" clauses), with the characterization first. (1) We identify
  that fused designs serialize independent work through their compiled command order, and characterize when removing
  it pays (the cut, between modular and fused, and the prompt length; predicts where gains arise and where they cannot).
  (2) We develop the analysis (dependence graphs over every agent, legality from the artifact, a bound per false
  order). (3) We design and implement OPCORD (rewrites; order and split per prompt length with the event model).
  Evaluation is never a contribution. The field's practice, counted on 18 MLSys papers from 2024-2026 (vault
  assets/contrib-review/mlsys-tally.md): a characterization item in 7-8 of 18 papers, always first, "We identify ...";
  lists of 3-4 items. The section plan is the vault's `paper-cosched-narrative-plan-v1`.
- **Venue** (author, 2026-10-15): **MLSys'27** research track; FCCM'27 is the fallback only if the audit kills a
  headline. Call (mlsys.org/Conferences/2027/CallForResearchPapers, read 2026-10-15): OpenReview, submissions open Oct
  19, deadline **Oct 30, 2026, 19:00 UTC** (12:00 PM PDT on the home page; the call says 20:00 UTC; plan for the
  earlier, planner's ruling), no separate abstract deadline; the MLSys 2025 style files; two columns, at most 10 pages before the
  references, appendix uploaded separately and unlimited; double-blind (no explicit or implicit self-identification, e.g. through
  self-references; the template's own instructions, not the call, add that an unpublished manuscript may be cited
  anonymously with an anonymized copy as supplementary material); every
  reference lists all of its authors; a mandatory "AI Usage Disclosure" section after the references (outside the
  page limit); an authorship quota per author.
- **Stage** (2026-10-21): the spine is the vault's `paper-cosched-outline-v9` (revision 31, 2026-10-21: T-rec withdrawn, the ML
  Timeline adopted as a figure, D13; revision 27 accepted after 27 independent review rounds, D4 option A). The draft at fe3e74e was written on the earlier composer framing and is being restructured to
  v9; replaced text goes verbatim to the vault.
- **Structure** (2026-10-21, outline v9 §4): 1 Introduction; 2 Background; 3 The Order Is in the Program (measured command
  semantics, the execution model, reading a stream and its attribution, closed binaries); 4 What Reading the Binaries Shows
  (the idle array per stack, the textbook classes and the grid, the census); 5 Bounding and Pricing Removals (the bound,
  joint pricing, the tests); 6 Removing Them (the passes and their legality checkers, as the implementation); 7 Evaluation;
  8 Discussion (compiler-owned concurrency; where static-order hardware sits); 9 Related Work; 10 Conclusion. The earlier
  §2.3 grid paragraph becomes §4's seed, with "We call such a wait a false dependence" replaced by a citation of the
  textbook classes.
- **The evaluation's message** (*proposal*, from the vault's `paper-ch3-outline`; decided after the results): on a
  spatial array, concurrency is free in the hardware but rationed by one in-order command processor, whose instruction
  order is the schedule. Patterns to test across every run: (1) queued commands never overlap, so concurrency lives
  inside a command; (2) the gain grows with attention's share, i.e. with prompt length; (3) the instruction order
  matters as much as co-residence; (4) host-boundary handling (queue depth, packing) trades overlap against readiness,
  and its best setting moves with length; (5) the event model ranks and prices schedules, with its error growing
  where attention is extrapolated.
- **Reference units** (*proposal*): prefill time normalized to the existing prefill's TTFT at the same model and prompt
  length; per-command model constants in units of the dispatch floor $F$; decode in the existing time per token.
  Table `params` still carries raw units (`% DECISION:` on it).
- **Names and labels:** the existing approach is "the existing prefill" or "the existing host program" (MLIR-AIR's
  fused prefill, cited); ours is "the composer" and its schedules "composed schedules". No method-family name or
  design-space labels yet (*proposal*: none until the evaluation needs them).
- **"Model" is reserved for the predictor** (author, 2026-10-21). The event model is always named as such and never appears as a bare "the model"; where the thing meant is a network being run, write "the LLM" or name it (Llama-3.2-1B, Qwen3-4B). Never use both senses in one sentence.
- **Core terms:** command, hardware context, instruction stream, issue instruction, synchronization, address patch,
  argument slot, dispatch floor $F$, append (§2.1-2.2); false dependence (§2.3); column group, segment, boundary cost
  $\epsilon$, commands in flight $D$, event model (§3.1-3.2); predicted completion order, buffer rings, renaming, split,
  arenas (§3.3-3.7). Avoid: arm names (edf, naive, Ar, q2, g4, b4), composer versions, "lag" (say "commands in
  flight"), "planner", "projection" for the model (it is a layer operator here), "the ladder", workstream labels (W1-W7).
- **Framing** (author, 2026-10-21; supersedes the earlier framing where they differ): false dependences are textbook
  (Bernstein's conditions; anti and output dependences; renaming; Tomasulo; modulo variable expansion) and are cited where
  defined, never presented as ours. The lead (C1) is static dependence analysis on a static-order NPU: each engine runs its
  program in order and nothing schedules across engines, so the dependence structure is read from the program (host
  dispatch sequence, runtime sequences and PDIs) without a timing trace, and each removal is bounded before it is built.
  The verb the title and abstract use for C1 (recovers / bounds / predicts / attributes) is set by outline v9 §3's rows, never
  chosen by the writer. C2 is what the analysis finds (the census, the production stream, the grid's instances); C3 is
  end-to-end worth. The passes and checkers are the implementation, not a contribution. *Superseded 2026-10-23 for the
  contribution list* (author): three items, namely the method (scheduling from the emitted streams, waits classed,
  legality from the streams alone), the event model and bound, and the design and implementation of OPCORD as the system
  carrying them (MLSys practice, vault paper-cosched-contributions-review); no evaluation item, no finding item. ReGate, Daydream, GPA, LATTICE and
  SDF critical-cycle analysis are argued by name.
- **Framing** (author's brief, 2026-10-14; thesis re-cut 2026-10-15): method-first; the composer works on unchanged
  kernels, and the one change inside a design (decode attention's double buffer) is the same rule applied by hand and
  stated as such; never "N× over AMD's code". Packing several operators per
  command (batching) is cited as standard practice. FCPR is cited in the third person, for the command-processor
  primitive only, in one background sentence; no text or figures are reused from it. The essential decisions
  (spatial assignment, CP instruction order) are reported apart from the host-boundary handling (queue depth,
  packing).
- **The baseline:** each design's own host program on its default split (attention on columns 0 and 7), with the same
  configuration, kernels, and weights; the stronger baseline is the same program with its attention columns
  alternated, and the honest headline compares each side on its own faster split. FastFlowLM appears only as an
  absolute reference on the same weights.
- **Figure palette** (`figs/make_figs.py`): GEMMs blue, LM head purple, attention orange, host and dispatch gray
  (busy); the existing schedules near-black (open square queued, filled triangle in sequence), ours magenta circles
  (pairs); reference lines black dashed (sum) and dotted (longer alone).
- **Defaults** (setup): median of timed runs after one warm run (3 today, 2 in the split and Qwen3-4B append
  comparisons; fixed at the freeze); bit-identical logits, appends also against a full prefill; one batch per comparison.
- **Not mentioned:** speedups framed against AMD's code; turn-level numbers until the results freeze (then stated
  plainly, the median step's small gain included); decode placement as a gain (it is a cap-bounded estimate);
  NP-hardness (until a reduction exists); the exactness of the predicted-completion order as a theorem (a remark until
  proven); out-of-order issue as a claim (an analogy at most; the CP stays in order); FCPR-scoped partitions
  (deferred); internal labels and history.
- **Deliberate differences from the guide (structure):** Related Work is its own section after the Discussion, as
  MLSys papers place it, instead of the Background's last subsection, because it carries the GPU phase-partitioning
  contrast the plan asks for.
- **Deliberate differences from the guide:** the MLSys template (natbib author-year through `mlsys2025.bst`) instead
  of ACM, so software entries are `@misc` (no `@software`), `lastaccessed` is not printed, and there is no
  `\Description`; figures are 3.25 in wide (the MLSys column) with Times through `newtxtext`/`newtxmath`, while the
  template sets text in Times and math in Computer Modern; `main.tex` sits in `paper/` because the repository root
  holds the artifact. The template itself logs duplicate `figure.N` anchors and an empty anchor from
  `\printAffiliationsAndNotice`; its own example does the same, so they are not fixed.
- **Headline** (planner's ruling, 2026-10-15): the introduction quotes Qwen3-4B's 3.0x and the split's own 1.9x under
  the composer; the 1B's 4.3x appears only in the evaluation, with the existing order's mid-range slowdown named.
- **Scope:** contexts up to the 32k window (edge models), not the frontier agents' ~120k prefixes; the NPU's prefill
  share of a turn answers the GPU result that prefill is under 10% of agent LLM time.
- **Open for the author:** whether to cite FCPR at all; the AI usage disclosure; the working title; the authorship
  quota; bib entries marked VERIFY need their sources read and a vault source
  note each; the reference units (Table `params` is still raw).

## Links
paper-writing-process · repo-workflow · ai-instructions · pref-documentation-and-record
