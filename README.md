**Question:** How many times more expensive is colour printing per page than black-and-white?

**Answer:**

Colour printing costs eight times as much per page as black-and-white (Source: admin_printing_quota.txt).


**My relevance cutoff:** 0.6

I ran my 5 test questions and the 5 OUT_OF_SCOPE questions through `python app.py retrieve` and recorded the best distance for each. There was a clean gap with no overlap: in-corpus questions topped out at 0.452, out-of-scope questions started at 0.825. The starter's default of 0.6 already sits in that gap, so I kept it.

| Question | In corpus? | Best distance |
|---|---|---|
| Through which week can you drop a course, and what shows up on your transcript if you drop after week two? | Yes | 0.229 |
| How many times more expensive is colour printing per page than black-and-white? | Yes | 0.266 |
| What are the walk-in hours at the health centre? | Yes | 0.216 |
| How often does the campus shuttle run on weekends? | Yes | 0.411 |
| Which floor of the library has outlets at every seat? | Yes | 0.452 |
| What is the capital of Mongolia? | No | 0.825 |
| How do I change the oil in a diesel engine? | No | 0.934 |
| Who won the 1994 World Cup? | No | 0.886 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.844 |
| How do I write a for loop in Rust? | No | 0.896 |

Step 2: Commit

In the VS Code terminal:

git add .
git commit -m "tune retrieval, confirm cutoff, add sample answer to README"
git push

Send me the output. That's Milestone 4 done, and commit 3 of 4. Milestone 5 (finishing the README and submitting) is all that's left for Unit 1.

send mem th e whole read me

markdown
# The Unofficial Guide

Huseyn Tahirli — corpus: campus_life

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.

---

# Unit 1

## What This Does

This system answers questions about student life using the campus_life
corpus, 88 short posts (1-3 paragraphs each) covering admin topics like
housing, dining, add/drop deadlines, and parking, plus course-specific posts
on workload and exams. It retrieves the most relevant post for a question,
answers using only that content, and names the source file. Questions clearly
outside the corpus, like general trivia, get refused instead of answered.

## Chunking Strategy

**Chunk size:** up to 600 characters, split on paragraph breaks
**Overlap:** 50 characters, only applied when a document needs to split

The starter's default (fixed 800-character windows) never split anything on
this corpus, since the longest post is only 549 characters. That's not
useless information, but it means the chunking "decision" was really just an
accident of corpus size. I replaced it with a chunker that splits on
paragraph breaks and merges paragraphs up to a 600-character cap, so a post
with multiple paragraphs would be handled on purpose rather than by luck if
this corpus ever grew longer posts. On campus_life specifically, this
produces the same result as before (88 documents, 88 chunks), because every
post still fits under the cap in one piece. The real payoff of doing this
now is Milestone 4 — if I ever swap corpora or add longer posts, the chunker
won't silently keep everything unsplit.

## Sample Chunks

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window - through the end of week six - but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.


**Chunk 2** — source: `course_biol_160.txt#0` — produced by: `chunker.py::split_documents`

BIOL 160 Cell Biology

I lived here my sophomore year. Format is lecture three times a week with a weekly lab. Assessment: four unit tests and a cumulative final. Not curved.

Expect 9 to 11 hours a week, the heaviest first-year course by reputation.

The one piece of advice: the unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.


**Chunk 3** — source: `course_hist_118_workload.txt#0` — produced by: `chunker.py::split_documents`

Workload for HIST 118 Modern World History

People keep asking so: a lot of reading, about 120 pages a week, but no problem sets. That's real time, not optimistic time.

It's front-loaded - the first month is heavier than the rest, partly because you're learning the format.


**Chunk 4** — source: `dining_pellew_dining_hall_followup.txt#0` — produced by: `chunker.py::split_documents`

Re: Pellew Dining Hall

Adding to what people have said about Pellew Dining Hall. The wait figure of 12 to 18 minutes at peak matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.

Also worth saying: the furthest hall from anywhere, next to the athletics centre. Nobody tells you this at orientation.


**Chunk 5** — source: `housing_innisfree_hall.txt#0` — produced by: `chunker.py::split_documents`

Innisfree Hall - what it's actually like

Transferred in last year, so take this with a grain of salt. Built 1991, renovated 2022. Rooms are doubles arranged as pairs sharing one bathroom between two rooms.

The good: the shared-bathroom-between-two-rooms arrangement is the best compromise on campus.

The bad: no air conditioning, which matters for the first three weeks of September.

Laundry costs $1.75 wash, $1.75 dry, app-based. On noise: moderate; the building is L-shaped and the short wing is much quieter.


## Sample Answer

**Question:** How many times more expensive is colour printing per page than black-and-white?

**Answer:**

Colour printing costs eight times as much per page as black-and-white (Source: admin_printing_quota.txt).


**My relevance cutoff:** 0.6

I ran my 5 test questions and the 5 OUT_OF_SCOPE questions through `python app.py retrieve` and recorded the best distance for each. There was a clean gap with no overlap: in-corpus questions topped out at 0.452, out-of-scope questions started at 0.825. The starter's default of 0.6 already sits in that gap, so I kept it.

| Question | In corpus? | Best distance |
|---|---|---|
| Through which week can you drop a course, and what shows up on your transcript if you drop after week two? | Yes | 0.229 |
| How many times more expensive is colour printing per page than black-and-white? | Yes | 0.266 |
| What are the walk-in hours at the health centre? | Yes | 0.216 |
| How often does the campus shuttle run on weekends? | Yes | 0.411 |
| Which floor of the library has outlets at every seat? | Yes | 0.452 |
| What is the capital of Mongolia? | No | 0.825 |
| How do I change the oil in a diesel engine? | No | 0.934 |
| Who won the 1994 World Cup? | No | 0.886 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.844 |
| How do I write a for loop in Rust? | No | 0.896 |

## How I Used AI
**1.**

I had Claude Code write the chunker from scratch. Split on paragraphs, cap
at 600 characters, add a 50-char overlap if something actually splits, and
leave the old function in but unused. It got it right first try. Since every
post in my corpus is under 600 chars, nothing actually changed output wise,
still 88 docs and 88 chunks, but now that's on purpose instead of a fluke of
the starter's 800-char default.

**2.**

Claude Code wrote my five test questions by reading through files and
pulling out one checkable fact each. One of the expects phrases it gave me
was just "W" which basically any answer would match by accident, so it
wasn't actually testing anything. I told it to fix that one and double check
all five phrases actually show up word for word in their source files. It
tightened the bad one to "W on your transcript" and confirmed the rest were
already fine.

---

# Unit 2

## Run Log — Before

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks stand on their own | 4 of 5 | 5/5 | — | — | MET |
| 5. Answers cite the correct file | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

Produced by run_eval.py::main, full output in results/run_2026-09-30_2013_before.md. Criterion 4 isn't re-run here since it's a static check on the 5 chunks sampled back in Milestone 3, chunking doesn't change between eval runs.

Real output, "through which week can you drop a course, and what shows up on your transcript if you drop after week two?", run 1:

You can drop a course through the end of week six. If you drop a course after week two, it shows as a W on your transcript.

Source: admin_add_drop_deadline.txt


Real output, "which floor of the library has outlets at every seat?", run 1:

The basement is the only floor that has outlets at every seat, according to study_library_hours.txt.


## Verdicts

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | MET | Ran all 5 questions 3 times. Every single run pulled back the chunk with the answer, 5/5 every time, well past the 4/5 bar I set. |
| 2 | Every answer names a source | MET | All 15 answers (5 questions times 3 runs) named a source file. 5/5 every run. |
| 3 | Gate stops out-of-corpus questions | MET | run_eval.py checks this in one pass since it's deterministic. All 5 OUT_OF_SCOPE questions got refused. |
| 4 | Chunks stand on their own | MET | From Milestone 3, all 5 chunks I sampled read as complete thoughts on their own. |
| 5 | Answers cite the correct file | MET | Went through every answer across all 3 runs and checked it against the actual source doc. All 15 cited the right file, no mix-ups. |

## Diagnoses

I didn't miss anything. Every criterion hit 5/5 on every run, even though most of my targets only asked for 4/5. Honestly that's more a sign my targets were too easy than my system being great, my corpus is only 88 short posts and each one covers one clean topic, so my test questions all had an obvious answer sitting in exactly one file.

If I had to tighten one, it'd be #1 (retrieved chunk contains the answer). I'd bump it from 4 of 5 to 5 of 5 since it's never actually missed once. That would also push me to write harder test questions next time, ones where the answer is split across two posts or two files talk about similar things, since that's probably where this system would actually start to struggle.

## The Improvement

**What I changed:**

**Why I picked it:**

### Run Log — After

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

## What's Still Broken

## What I'd Do Differently