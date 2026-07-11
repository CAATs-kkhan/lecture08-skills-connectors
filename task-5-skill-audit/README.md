# Task 5 — Audit a Skill Before Trusting It

**Skill audited:** `pdf`
**Source:** the official Anthropic skills directory — https://github.com/anthropics/skills (`skills/pdf`)
**Audited in:** Claude Code (VS Code), 11 July 2026
**Verdict: SAFE TO ENABLE.** ✅

---

## Why I picked this Skill

I deliberately picked a Skill that is *worth* being nervous about. `pdf` is exactly the kind
of thing people install without a second thought — and it ticks every box that should make you
pause before you do:

- It **ships real executable code** — 8 Python scripts, not just instructions.
- It **reads and writes your actual documents**, which are often the most sensitive files you own
  (contracts, bank statements, ID scans, tax forms).
- It is explicitly built to **fill in forms** — so by design it handles the personal details
  you type into forms.

If a Skill were going to quietly siphon off your data, this is the shape it would have. So
"is it safe?" is a real question here, not a formality.

---

## What the Skill actually does — in plain English

It teaches the AI to work with PDF files. That's it. Concretely, it can:

- **Read a PDF** — pull out the text and the page structure.
- **Turn pages into images** so the AI can visually *look* at a page.
- **Reshape files** — merge several PDFs, split one apart, rotate or delete pages.
- **Fill in forms.** This is the bulk of it. It finds the form fields in a PDF, works out where
  each one sits on the page, types your values in, and then renders the filled page back to an
  image so it can *check its own work* and confirm the text actually landed inside the right box.

Everything it does is a local file-in, file-out operation: a PDF goes in from your disk, a
modified PDF or a PNG comes back out to your disk.

---

## The three questions the task asks

I did not take the Skill's word for any of this. I read every script and searched all 8 of them
for the specific things that would indicate a problem.

### 1. Does it contact any external server? **No.**

This is the one that matters most, and the answer is unambiguous.

I listed every single `import` in all 8 scripts. Every one is either part of Python itself
(`json`, `sys`, `os`, `dataclasses`) or a well-known library that works on local files:

| Library | What it's for |
|---|---|
| `pypdf` | reading and writing PDF files |
| `pdfplumber` | pulling text and layout out of a PDF |
| `pdf2image` | turning PDF pages into pictures |
| `PIL` (Pillow) | drawing on those pictures |

**There is no networking library anywhere in the Skill** — no `requests`, no `urllib`, no `httpx`,
no `socket`. This is not a judgement call or a "looks fine to me". A Python program simply
*cannot* send your data over the internet without importing something that can talk to the
network. None of them are there. It is not possible for this code to phone home.

The only URLs in the entire Skill are two links to Anthropic's legal terms, sitting in the
licence file. They are text in a document. Nothing ever visits them.

### 2. Does it handle credentials? **No.**

Searching for `api_key`, `token`, `secret`, `password`, `os.environ` and `getenv` turned up
**zero hits in any of the executable code.**

The word "password" *does* appear — which looked alarming until I read where. Every hit is in
the **documentation**, explaining PDF's own built-in encryption feature: how to put a password
*on* a PDF you're creating, or how to open a PDF that's already locked (using a password
*you* supply, at the moment you run it). That is a feature of the PDF format, not credential
harvesting. It never reads a stored password, never touches environment variables, and never
goes looking for keys on your machine.

### 3. Does it send your data anywhere unexpected? **No.**

It cannot — see question 1. Your PDF is read from your disk, changed in memory, and written
back to your disk. There is also no `subprocess`, no `eval`, and no `exec` anywhere, so it
never shells out to run some other program and never executes code that was smuggled in at
runtime. What you read in the scripts is all that will ever run.

---

## What it *does* touch, and the one thing to actually keep in mind

Being safe is not the same as being harmless, and I want to be precise about the difference.

**This Skill writes files.** That is the whole point of it — it is not a read-only Skill, and it
cannot be. If you ask it to fill a form, it produces a new PDF.

So the realistic risk here is not theft, it's **accidents**: a badly-worded request could have it
overwrite a PDF you cared about. That is a mistake, not an attack, and the fix is mundane —
work on a copy, or make sure the original is backed up. It is worth being aware of, but it is
a completely different category of concern from "this thing is stealing my documents."

---

## Verdict — would I enable it?

**Yes. I would enable this Skill, and I would trust it with a real document.**

My reasoning, in one line: **it has no way to send my data anywhere, so the worst case is that
it does its job badly — not that it betrays me.**

The stronger point is *how* I know that. I did not trust it because it came from Anthropic's
official repository, and I did not trust it because it says nice things about itself in its
own README — a malicious Skill would say nice things too. I trusted it because I checked the
one thing that cannot be faked: **code without a networking library cannot exfiltrate data.**
The imports are the proof, and the imports are clean.

---

## The lesson I'm taking from this

The audit that mattered took about five minutes and needed no deep code literacy. I did not
have to understand *how* `pypdf` fills a form field. I only had to ask three concrete questions
and check them against the code rather than against the Skill's own description:

1. **What does it import?** — networking libraries are how data leaves. No network library, no exfiltration.
2. **Does it read secrets?** — search for `token`, `password`, `os.environ`. And when you get a hit, *read where it is* — my "password" hits were documentation, not theft.
3. **Does it run other code?** — `subprocess`, `eval`, `exec` are how a Skill does something other than what it claims.

The habit worth keeping: **a Skill's description tells you what it wants you to think it does;
its imports tell you what it is actually capable of.** When those two agree, you can trust it.
Here, they agreed.

An honest caveat on scope: this audit covers the Skill's own code. The libraries it depends on
(`pypdf`, `pdfplumber`, `pdf2image`, `PIL`) are separate, widely-used open-source packages that
I did not read line by line — I'm relying on their reputation and broad usage, which is a
reasonable but real assumption, and worth naming rather than hiding.
