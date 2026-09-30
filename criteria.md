# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written before
any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, a sentence or two on why that target and not a stricter or
looser one.

---

## 1. Retrieved chunks contain the answer

**Given:** my 5 test questions in `questions.py`
**When:** each one is run through retrieval
**Then:** at least 4 of 5 return a chunk that contains the answer

**Why this target:**
One of my questions is about a topic that only shows up in one document
(admin_add_drop_deadline.txt), so retrieval might miss it even if the system
works fine for the others.

---

## 2. Every answer names a source

**Given:** any question the system answers, in-scope or not
**When:** the system produces an answer
**Then:** the answer names at least one source document

**Why this target:**
The prompt requires every answer to name a source, and campus_life posts are
short and single-topic, so there's little room for the model to drift away
from citing one. I'm not giving myself slack here.

---

## 3. The relevance gate stops out-of-corpus questions

**Given:** the 5 questions in `OUT_OF_SCOPE` in `questions.py`
**When:** each one is run through the system
**Then:** the relevance gate stops it and returns "I don't have enough
information about that" in at least 4 of 5 tries

**Why this target:**
I expect a clean gap between my in-scope and out-of-scope distances since my
OUT_OF_SCOPE questions are about totally unrelated topics like oil changes
and World Cup history. I left room for 1 miss in case a question happens to
share a stray word with my corpus.

---

## 4. Chunks stand on their own

**Given:** 5 chunks sampled and printed from my indexed corpus
**When:** I read each one on its own, with no surrounding text
**Then:** at least 4 of 5 can answer a question without needing the text
before or after them

**Why this target:**
campus_life posts are short (avg 317 characters) and usually cover one topic,
so most chunks should already stand alone. I left room for 1 that might get
cut awkwardly.

---

## 5. Answers cite the correct file

**Given:** my 5 test questions in `questions.py`
**When:** each one is run through the system
**Then:** at least 4 of 5 answers name the correct source file, not just any
source

**Why this target:**
Some topics overlap across files (like admin_housing_lottery.txt and
admin_parking_permits.txt both mentioning housing), so the system might cite
a related-but-wrong file even when the answer itself is right.