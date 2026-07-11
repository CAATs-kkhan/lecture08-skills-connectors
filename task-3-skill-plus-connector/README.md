# Task 3 — Wire Skill + Connector Together

**Skill:** `narration-to-video` (from Task 1)
**Connector:** Gmail (from Task 2)
**Result:** [`digiskills-from-gmail.mp4`](digiskills-from-gmail.mp4) — **27.4 seconds**, built entirely from a live email. No copy-paste.

---

## The one sentence I used

> **"Make a 30-second video from the DigiSkills email in my inbox."**

That's it. One plain-English sentence. I did not name the Skill, I did not write a storyboard,
and I never opened the email myself.

## What happened automatically

1. **The Connector fired** — Gmail was searched, the DigiSkills thread was found, and its full
   body was pulled live from the inbox.
2. **The Skill fired** — `narration-to-video` triggered on its own from the phrase "make a
   30-second video," without being named.
3. **The Skill wrote the storyboard** from the email's real contents — 5 scenes, 57 words of
   narration (under its own 75-word / 30-second budget).
4. **The renderer ran** — neural voiceover, slides rendered in headless Chrome, Ken Burns motion
   and fades applied, all muxed into an MP4 by ffmpeg.

**Output: 27.4 seconds — inside the 30-second cap, enforced by the Skill, not by luck.**

## The video, scene by scene

| # | Scene | Narration (spoken + burned in as caption) |
|---|---|---|
| 1 | **DigiSkills 3.0** — *Batch 04 · Now Open* | "DigiSkills three point oh, Batch four, is now open for enrollment." |
| 2 | **Four New Courses** — Cloud Computing · AI with Python · Shopify & Dropshipping | "Four new courses this batch, including cloud computing, and A I with Python." |
| 3 | **Three Steps** — Register & activate · Complete profile · Enroll in any two | "Register, complete your profile, then pick any two courses you like." |
| 4 | **FREE** — Funded by Ignite | "It is completely free, funded by Ignite, and run by Virtual University." |
| 5 | *"Seats are limited. Enroll now."* | "Seats are limited, so log in and secure yours today." |

Every fact in those five scenes came out of the live email. Nothing was invented.

## Spot-check against the source (step 3 of the task)

The task says to spot-check one part of the result before trusting the whole thing. I checked
the claim that carried the most risk of being wrong: **scene 3's "enroll in any two courses."**

A number like that is precisely what an AI can quietly fumble — "two" could easily have become
"any" or "all." I opened the original email and confirmed it reads *"enroll in any two courses
of your choice."* Correct.

I also verified the four course names and the funders (Ignite / Virtual University of Pakistan)
against the email body. All accurate.

---

## What worked, what didn't

**Worked.** This is the moment the whole lecture clicked. One sentence, and live data came out of
a real app, went through instructions I had written earlier, and came back as a finished,
narrated video. No copy-paste at any point. The Skill and the Connector genuinely composed —
neither knew about the other, and it still worked, because the Skill just says "read the source
material" and the Connector is what makes reading possible.

**Didn't work — the same bug, twice.** The first render of this video came out with **only scene 1
visible and scenes 2 through 5 solid black.** I had already found and fixed that bug in Task 1,
so seeing it again was a nasty surprise.

The cause was not the original bug — it was a **Windows `Copy-Item` trap.** When I "synced" the
fixed script into the installed Skill folder, `Copy-Item -Recurse` onto an *existing* directory
**nests** the source inside it instead of replacing it. So I ended up with:

```
narration-to-video/scripts/make_video.py                    ← the OLD, buggy script (what actually ran)
narration-to-video/narration-to-video/scripts/make_video.py ← my fix, buried where nothing would load it
```

I had verified the fix worked, then silently un-deployed it with a bad copy command, and never
re-checked. **The lesson: verifying a fix and verifying the fix is what's actually running are
two different things.** I caught it only because I pulled frames out of the finished video and
looked at them — the same check that caught the original bug. `ffmpeg` exited 0 and produced a
perfectly plausible MP4 both times.

Fixed by deleting the install directory and copying cleanly, then re-rendering and re-checking
every scene's frames. All five scenes now render (see `screenshots/`).

---

## Files here

| File | What it is |
|---|---|
| `digiskills-from-gmail.mp4` | The finished 27.4s video, built from live Gmail data |
| `storyboard.json` | The storyboard the Skill wrote from the email (not written by hand) |
| `screenshots/scene1-5.png` | Frames pulled from the finished video — proof all 5 scenes render |
