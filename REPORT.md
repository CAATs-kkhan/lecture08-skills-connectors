# Lecture 8 Report — Skills & Connectors

**Student:** Khurram Khan
**AI tool used:** Claude Code (Opus 4.8) in VS Code, on Windows 11
**Apps connected:** Gmail (read-only). Google Drive attempted — the failure is written up in Project 2, because it taught me more than the success did.
**Date:** 11 July 2026

---

## Project 1 — `narration-to-video`

### What it does

Turns **a prompt, a pile of notes, an image, or a document** into a **narrated video of 30
seconds or less**, with animated graphics and a neural voiceover **in any language**.

I say one sentence. I never write a storyboard.

> *"make a 30-second video explaining what a Skill is"*

### Why I chose it, and how it helps my daily life

I keep explaining the same things to different people — a concept from class, a summary of a
document, an idea I want to share. Written text gets skimmed and forgotten. A short narrated
video actually gets watched.

But building one by hand is a **40-minute job**: write a script, time it to 30 seconds, design
slides, record a voiceover, edit it together. I was never realistically going to do that on a
regular basis, so I simply never made the videos. **This Skill collapses that 40 minutes into one
sentence.**

The part that makes it genuinely *mine* rather than a generic demo: **it narrates in any
language.** I need to explain things in **Urdu** to some people and **English** to others. Every
consumer tool I looked at is English-first, with Urdu either missing or a poor afterthought. This
Skill treats them as equals — the same sentence, the same format, either language — and it
automatically flips the slide layout to **right-to-left** for Urdu, Arabic and Farsi. That is the
feature I built it for, and it's the reason I'll keep using it after this assignment.

### How it works

| Stage | Tool | Leaves my machine? |
|---|---|---|
| Speak the narration | `edge-tts` — neural voices, 100+ languages | **Yes** — the narration *text* only |
| Render each scene | headless Chrome screenshot of a styled HTML page | No |
| Motion + fades | `ffmpeg` (Ken Burns push, cross-fades) | No |
| Mux into MP4 | `ffmpeg` | No |

Five scene types: `title`, `bullets`, `stat`, `quote`, `image`. `uv` fetches the dependencies on
first run, so the Skill has **no setup step at all**.

### Prompts, and how I refined them

**Initial prompt:**

> *"Is it possible if a user wants to enter or giving the prompt or png or jpeg in a narration form
> in any language then Claude code can work accordingly and make the output on a video in which
> good graphics, voice used, to a maximum 30 seconds video."*

**Two refinements, both forced by reality rather than preference:**

1. **"Any language" was not free.** Claude checked my machine and found only **two English voices**
   installed (David and Zira). Windows' built-in speech engine physically could not do what I
   asked. It proposed `edge-tts` instead — 100+ languages, natural neural voices — and was upfront
   that this **sends the narration text to Microsoft's servers**. I accepted that tradeoff
   knowingly, and the Skill documents it. Being told the honest cost was more useful than being
   told "yes, sure."
2. **ffmpeg wasn't installed.** Rather than telling me to go install it, it wired in a bundled
   copy via `uv`, so the Skill works on a clean machine with zero setup.

**Trigger prompts (it fires without being named):**
> *"make a 30 second video explaining what a Skill is"*
> *"turn this image into a narrated video"*

### How I tested and verified it

Opened a fresh request, used a natural sentence **without naming the Skill**, and confirmed it
triggered on its own and produced the right format. Then I extracted frames from the finished MP4
and looked at them.

### What worked, what didn't

**Worked:** it triggers reliably from plain language; the graphics genuinely look good; the
30-second cap is *enforced* by the script (it measures the narration and speeds the voice up in
stages if it overruns) rather than merely hoped for.

**Didn't work — the bug that matters.** The very first render **exited successfully and produced a
perfectly plausible 1.2 MB MP4** — and **scenes 2 and 3 were solid black.** Only scene 1 was
visible.

The cause was subtle: ffmpeg's `zoompan` filter with `d=N` emits N frames *for every input frame
it receives*, and `-loop 1` was feeding it an endless stream. Scene 1's clip stretched far beyond
its intended length, and since each clip fades to black at the end, the video stayed black forever
after that first fade. **The audio was perfect**, which is precisely why nothing automated caught
it.

**Fixed** by feeding each still at a real frame rate (`-framerate 30`) with `zoompan d=1`, so
exactly one frame comes out per frame in.

**The lesson: "ffmpeg exited 0 and an MP4 appeared" is not verification.** If the output is a
video, you have to look at the pixels.

**Other friction:** the biggest failure mode is writing **too much narration** — 30 seconds is only
about **75 words**, far less than it feels like. I wrote that rule into the Skill in bold, because
the model's instinct is to write far too much.

---

## Project 2 — Connect One App, Read-Only

### What it does

Gives the AI **read-only** access to Gmail, and pulls a real email thread with no copy-pasting.

### The permission I granted (the one-sentence note)

> **I granted Claude read-only access to my Gmail — it can search and read my email threads and
> their contents, but it cannot send, delete, or modify anything; I would only need write
> permission if I wanted it to draft or send replies on my behalf, which I do not.**

### What it pulled, and how I verified it

The connector reported **201 threads**, so it was genuinely reading the live account. It found and
summarized:

**"DigiSkills 3.0 – Batch-04 Enrollments Are Now Open"** — `noreply@digiskills.pk`, 10 July 2026.
Enrollment is open with limited seats; four new courses (Cloud Computing, Shopify Development &
Dropshipping, Mobile Game & App Development, AI with Python); three steps to enroll — register,
complete your LMS profile, then enroll in **any two courses**; free, funded by **Ignite** and run
by the **Virtual University of Pakistan**.

**Verification:** I opened the real email and checked it line by line. I checked hardest on **"any
two courses"** — a specific numeric constraint is exactly what a summarizer can quietly get wrong,
and it would matter. The email says *"enroll in any two courses of your choice."* Correct. Course
names and funders also matched exactly.

### What did not work — and why it's the most valuable thing in this report

**I originally tried Google Drive. It never worked, and understanding why taught me more than the
successful Gmail connection did.**

I uploaded files to a Drive folder called `VIDEO GENERATOR`. The connector authorized fine — and
then reported that my Drive was **completely empty.** Recent files: nothing. All Google Docs:
nothing. Everything I own: nothing. Even a search for *folders*: nothing. Fetching the folder by
its exact ID returned **"Requested entity was not found."**

I ruled the causes out one at a time:

| Theory | How I tested it | Result |
|---|---|---|
| I misread the file ID from a screenshot | Compared against the real copied URL | ❌ ID was exactly right |
| Search index hadn't caught up | Fetched by ID (bypasses search entirely) | ❌ Still "not found" |
| Wrong Google account | Re-authorized on the other account; uploaded to **both** | ❌ Empty on both |
| **The permission scope is narrower than I assumed** | Everything else eliminated | ✅ **This was it** |

The connector was never broken. It was **faithfully reading a Drive it was only permitted to see
part of** — a scope exposing only files the app itself created, making my hand-uploaded files
permanently invisible on *any* account.

**This is the entire point of the connector chapter, learned the hard way.** "I connected Google
Drive" *felt* like it meant "the AI can see my Drive." It did not. And the failure was **silent**:
Drive never said *permission denied*. It said **empty** — which looks exactly like having no
files. A less stubborn version of me would have concluded the upload had failed, and never
learned that my *permission* was different from what I'd imagined.

**The takeaway:** a connector doesn't grant access to "my Google stuff." It grants **one app, one
scope, one account**. And when it returns nothing, *"you're not allowed to see it"* and *"there's
nothing there"* can be **indistinguishable from the outside.** Which is exactly why the course's
one rule is: always check the AI's output against the real source.

---

## Project 3 — Wire Skill + Connector Together

### What it does

One plain-English sentence → live email fetched from Gmail → a finished, narrated, 27.4-second
video. **No copy-paste anywhere.**

### The sentence I used

> **"Make a 30-second video from the DigiSkills email in my inbox."**

I did not name the Skill. I did not write a storyboard. I never opened the email myself.

### What happened automatically

The **Connector** searched Gmail and pulled the thread's full body. The **Skill** triggered on its
own from the phrase "make a 30-second video," wrote a 5-scene storyboard from the email's real
contents (57 words of narration, inside its own 75-word budget), and rendered it.

**Output: 27.4 seconds — inside the 30-second cap.** → `digiskills-from-gmail.mp4`

### How I spot-checked it

I checked the claim most likely to be wrong: scene 3's **"enroll in any two courses."** A number
like that is exactly what an AI can fumble — "two" could easily have become "all." I opened the
original email: *"enroll in any two courses of your choice."* Correct. The four course names and
the funders also matched the source.

### What worked, what didn't

**Worked.** This is where the lecture clicked. The Skill and the Connector **composed without
knowing about each other** — the Skill just says "read the source material," and the Connector is
what makes reading possible. Neither was written with the other in mind.

**Didn't work — the same black-scenes bug, again.** The first render of *this* video came out with
**only scene 1 visible and scenes 2–5 black.** I had already fixed that bug in Project 1, so this
was a nasty surprise.

The cause wasn't the original bug — it was a **Windows `Copy-Item` trap.** Copying a directory
onto an *existing* directory with `-Recurse` **nests** it instead of replacing it:

```
narration-to-video/scripts/make_video.py                     ← the OLD, buggy script (what actually ran)
narration-to-video/narration-to-video/scripts/make_video.py  ← my fix, buried where nothing loads it
```

I had verified the fix, then silently un-deployed it with a careless copy, and never re-checked.
**Verifying a fix and verifying that the fix is what's actually running are two different things.**
Caught again only by pulling frames and looking at them.

---

## Project 4 — Make It Portable

### What it does

Proves the Skill is a real asset, not a trick that only works in the chat that made it. I
installed it **user-wide** (`~/.claude/skills/narration-to-video/`), so it's available in every
Claude Code session on this machine, then ran it from an unrelated folder with a **different
voice** and a **different accent colour**. It worked: `portable-proof.mp4`.

`narration-to-video-skill.zip` is the handoff bundle — someone else unzips it into their own
`~/.claude/skills/` and says *"make a 30-second video about X"*, with no explanation from me.

### What didn't work — and why this task earns its place

**Moving the Skill broke it immediately:**

```
json.decoder.JSONDecodeError: Unexpected UTF-8 BOM (decode using utf-8-sig)
```

In the new environment I wrote the storyboard with **PowerShell**, whose `Out-File -Encoding utf8`
adds a **byte-order mark**. Python's `json.loads` rejects it. In the original environment, every
storyboard had been written by Claude's own file tools, which don't add a BOM — so this bug was
**completely invisible**, sitting there waiting for the first person to use Notepad or PowerShell.

**Fixed** by reading as `utf-8-sig` (accepts a BOM, works fine without one).

**The lesson: a Skill that has only ever run where it was born has not really been tested.** The
home environment quietly supplies assumptions you don't know you're making. The only way to find
them is to take it somewhere else and see what falls over. Had I shipped that zip to a classmate,
the first thing they'd have seen was a crash.

---

## Project 5 — Audit a Skill Before Trusting It

**Skill audited:** `pdf`, from the official [anthropics/skills](https://github.com/anthropics/skills) directory.
**Verdict: SAFE TO ENABLE.** ✅

### Why this one

I deliberately picked a Skill worth being nervous about. `pdf` **ships 8 executable Python
scripts**, it **reads and writes your documents** (often the most sensitive files you own), and
it's **built to fill in forms** — so by design it touches personal details. If a Skill were going
to quietly siphon off data, this is the shape it would have.

### What it does, in plain English

Works with PDF files: reads them, turns pages into images so the AI can *look* at them, merges /
splits / rotates them, and fills in forms — finding each field, typing values in, then rendering
the page back to an image to check its own work. Everything is local file-in, file-out.

### The safety assessment

**Does it contact an external server? No.** I listed every `import` across all 8 scripts. Every one
is either Python's standard library (`json`, `sys`, `os`, `dataclasses`) or a local document
library (`pypdf`, `pdfplumber`, `pdf2image`, `PIL`). **There is no networking library anywhere** —
no `requests`, no `urllib`, no `httpx`, no `socket`. This isn't a judgement call: a Python program
**cannot** send data over the internet without importing something that can talk to the network.
None of them are present. It is *structurally incapable* of phoning home. The only URLs in the
whole Skill are two links to Anthropic's legal terms, sitting inertly in a licence file.

**Does it handle credentials? No.** Searching for `api_key`, `token`, `secret`, `os.environ` and
`getenv` returned **zero hits in the executable code.** The word "password" *does* appear — which
looked alarming until I read *where*. Every hit is in the **documentation**, explaining PDF's own
encryption feature (putting a password on a PDF, or opening a locked one with a password *you*
supply at runtime). That's a feature of the PDF format, not credential harvesting.

**Does it send data anywhere unexpected? No** — it cannot, per the above. There's also no
`subprocess`, `eval`, or `exec`, so it never shells out or runs smuggled-in code. **What you read
is all that will ever run.**

### The one honest caveat

Being *safe* isn't the same as being *harmless*. **This Skill writes files** — that's its job. So
the realistic risk isn't theft, it's **accidents**: a badly-worded request could overwrite a PDF
you cared about. That's a mistake, not an attack, and the fix is mundane (work on a copy). Worth
knowing, but a completely different category from "this thing is stealing my documents."

### Verdict and reasoning

**Yes, I'd enable it, and trust it with a real document.** In one line: **it has no way to send my
data anywhere, so the worst case is that it does its job badly — not that it betrays me.**

The stronger point is *how* I know. I did **not** trust it because it came from Anthropic's
official repo, and **not** because its README says nice things — a malicious Skill would say nice
things too. I trusted it because I checked the one thing that **cannot be faked**: *code without a
networking library cannot exfiltrate data.*

**The habit worth keeping: a Skill's description tells you what it wants you to think it does; its
imports tell you what it is actually capable of.** When those two agree, you can trust it.

*(Scope caveat, stated honestly: this audit covers the Skill's own code. The libraries it depends
on are separate widely-used open-source packages I did not read line by line — I'm relying on
their reputation, which is reasonable but is a real assumption worth naming rather than hiding.)*

---

## Summary — what I'd take into the next project

1. **A connector grants one app, one scope, one account** — never "my data" in the abstract. And a
   permission failure can look **exactly** like an empty folder, so always check against the real
   source.
2. **Exit code 0 is not verification.** Two of the three real bugs in this assignment produced
   *successful* runs and *valid-looking* output files. Both were caught only by inspecting the
   actual artifact.
3. **Nothing is portable until you've moved it.** The environment that built a thing is the worst
   place to test it.
4. **You can audit a Skill's safety without deep code literacy** — you just need to know which
   three questions to ask, and to check the answers against the code rather than the description.
