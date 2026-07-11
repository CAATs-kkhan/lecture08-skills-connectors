# Task 2 — Connect One App, Read-Only

**App connected:** Gmail (via the built-in `claude.ai Gmail` connector in Claude Code)
**Account:** `khansimpletolearn@gmail.com`
**Also attempted:** Google Drive — *see "What went wrong" below. This is the interesting part.*

---

## The one-sentence permission note (what the task asks for)

> **I granted Claude read-only access to my Gmail — it can search and read my email threads and
> their contents, but it cannot send, delete, or modify anything; I would only need write
> permission if I wanted it to actually draft or send replies on my behalf, which I do not, so
> read-only is the correct scope for what I am doing.**

---

## What I did

1. Connected Gmail with `/mcp` → `claude.ai Gmail` → Authenticate.
2. Asked the AI to find and summarize a recent email thread — **no copy-pasting.**
3. Verified the summary against the real email in Gmail.

The connector reported **201 threads** in the inbox, so it was genuinely reading the live account.

## The data it pulled

**Thread:** "DigiSkills 3.0 – Batch-04 Enrollments Are Now Open – Secure Your Seat Today"
**From:** `noreply@digiskills.pk` · **Received:** 10 July 2026

**The AI's summary:**

> Enrollment for DigiSkills 3.0 – Batch-04 is open, with limited seats. Four new courses are on
> offer: Cloud Computing, Shopify Development & Dropshipping, Mobile Game & App Development, and
> AI with Python. Enrolling takes three steps — register and activate your account by email,
> complete your LMS profile, then enroll in **any two courses** via "Enroll Now (DSTP 3.0 –
> Batch-04)" on your LMS homepage. It is free, funded by **Ignite** and executed by the
> **Virtual University of Pakistan** under the Ministry of IT & Telecom.

## How I verified it (step 3 of the task)

I opened the actual email in Gmail and checked the summary line by line. The detail I checked
hardest was **"any two courses"** — a specific numeric constraint is exactly the sort of thing a
summariser can quietly get wrong, and getting it wrong would matter. The email says *"enroll in
any two courses of your choice."* The summary was accurate. All four course names, the
three-step process, and the funding bodies matched the source exactly.

---

## What went wrong — and the real lesson about connectors

**I originally tried to connect Google Drive, and it never worked. Understanding *why* taught me
more than the successful Gmail connection did.**

I uploaded two files to a Drive folder called `VIDEO GENERATOR`. The connector authorized
successfully — and then reported that **my Drive was completely empty.** Every query came back
with nothing: recent files, all Google Docs, everything I own, a full-text search, even a search
for *folders*. When I fetched the folder by its exact ID, Drive answered
**"Requested entity was not found."**

I worked through the possible causes one at a time:

| Theory | Test | Result |
|---|---|---|
| The file ID was misread from my screenshot | Copied the real URL and compared | ❌ ID was exactly right |
| Search index hadn't caught up after upload | Fetched by file ID, which bypasses search | ❌ Still "not found" |
| Wrong Google account | Re-authorized on the other account, uploaded to *both* | ❌ Empty on both |
| **Connector's permission scope is too narrow** | Everything above ruled out | ✅ **The answer** |

The connector was never broken. It was **faithfully reading a Drive it was only permitted to see
part of** — a scope that only exposes files the app itself created, which makes files I uploaded
by hand permanently invisible to it, on any account.

**This is the whole point of the connector chapter, learned the hard way.** "I connected Google
Drive" felt like it meant "the AI can now see my Drive." It did not. The permission I actually
granted was narrower than the one I assumed I had granted — and the failure mode was *silent*.
Drive did not say "permission denied." It said **"empty"**, which looks exactly like having no
files. If I had been less stubborn, I would have concluded my upload had failed, rather than
that my *permission* was different from what I imagined.

**The takeaway:** a connector does not grant access to "my Google stuff." It grants one specific
app, one specific scope, on one specific account. And when a connector returns nothing, "you
don't have permission to see it" and "there is nothing there" can be **indistinguishable from
the outside** — so verify against the real source before you trust either answer. Which is
exactly what the course's one rule says: *always check the AI's output against the real source.*

---

## Would I ever need write permission?

Not for this. Everything I want here — summarizing threads, pulling notes out of email, feeding
content into my video Skill (Task 3) — is **reading**. Write access would let the AI send email
as me, and the downside of a mistake there (a wrong email sent to a real person, irreversibly)
is far worse than any convenience it would buy.

The only case I would consider it: letting it **draft** replies into my Drafts folder — where I
still press Send myself. Even then I would want that to be a separate, explicit permission, not
something bundled in with reading.

---

## Screenshots

`screenshots/` — the OAuth consent screen showing the permissions granted, and the summarized
thread next to the real email for comparison. Private details are blurred.
