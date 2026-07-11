# Lecture 8 — Skills & Connectors

**Student:** Khurram Khan
**Course:** Panaversity — *The AI Agent Factory*, Skills & Connectors crash course
**Built with:** Claude Code (Opus 4.8) in VS Code, on Windows 11

---

## The five projects

| # | Project | What it is | Result |
|---|---|---|---|
| 1 | [**My Skill**](task-1-my-skill/) | `narration-to-video` — turns a prompt, notes, or an image into a ≤30s narrated video with graphics, in any language | ✅ Works, triggers from natural language |
| 2 | [**Connect an app**](task-2-connect-app/) | Gmail, read-only. Summarized a real inbox thread | ✅ Real data pulled + a genuine permissions lesson |
| 3 | [**Skill + Connector**](task-3-skill-plus-connector/) | One sentence → live email → finished 27.4s narrated video | ✅ [`digiskills-from-gmail.mp4`](task-3-skill-plus-connector/digiskills-from-gmail.mp4) |
| 4 | [**Portable**](task-4-portable-handoff/) | Installed the Skill user-wide, ran it from a different folder | ✅ Works — and the move exposed a hidden bug |
| 5 | [**Audit**](task-5-skill-audit/) | Safety review of the official `pdf` Skill | ✅ Verdict: safe to enable |

**Full write-up: [REPORT.md](REPORT.md)**

---

## The Skill I built

`narration-to-video` — because the task I keep repeating is *explaining the same thing to
different people*, and text gets skimmed. Making a narrated video by hand is a 40-minute job, so
I never did it. **Now it's one sentence.**

> *"make a 30-second video explaining what a Connector is"*

It handles a plain topic, a PNG/JPEG, notes, or a document pulled from a connected app. It
narrates in **any language** — Urdu, Hindi, Arabic and Farsi automatically flip the slides to
right-to-left — which is the part that makes it genuinely mine: I need to explain things in Urdu
*and* English, and every tool I found treats Urdu as an afterthought.

**How it works:** `edge-tts` speaks the narration → headless Chrome renders each scene to a still
→ `ffmpeg` adds Ken Burns motion, fades, and lays down the voice track. `uv` fetches the
dependencies on first run, so there's no setup step.

**Privacy, stated plainly:** the narration **text** is sent to Microsoft's speech service — that's
the price of 100+ languages, and the Skill says so in its own instructions. **Images, documents
and the finished video never leave the machine.**

---

## Tools and apps used

| | |
|---|---|
| **AI tool** | Claude Code (Opus 4.8), in VS Code |
| **Connector** | Gmail — read-only *(Google Drive attempted; see Task 2)* |
| **Skill audited** | `pdf`, from [anthropics/skills](https://github.com/anthropics/skills) |
| **Under the hood** | `edge-tts` (voice), headless Chrome (graphics), `ffmpeg` (video), `uv` (deps) |

---

## The three things I actually learned

**1. A connector's permission is narrower than it feels.** I connected Google Drive, and it
reported my Drive was **empty** — not "access denied", just *empty*. It took ruling out the file
ID, the search index, and two different Google accounts before the real answer emerged: the scope
I'd granted only let it see files the app itself created. My uploads were invisible, permanently.
**"Permission denied" and "there's nothing there" look identical from the outside** — which is
exactly why the course's one rule is to check the AI's output against the real source.

**2. "The command exited 0" is not verification.** My video renderer twice produced a perfectly
valid MP4 in which **only the first scene was visible and the rest were solid black.** ffmpeg
succeeded. The file size was plausible. Every automated check passed. It was only caught by
pulling frames out of the finished video and *looking at them*. If the output is a video, you
have to look at the pixels.

**3. A Skill isn't portable until you've moved it.** Task 4 felt like a formality — until moving
the Skill to another folder crashed it instantly on a UTF-8 BOM bug that the original environment
had been silently hiding the whole time. The environment supplies assumptions you don't know
you're making, and the only way to find them is to leave.

---

## Repository layout

```
task-1-my-skill/              SKILL.md, the renderer, prompts, demo video, frames
task-2-connect-app/           Gmail connector, permission note, the Drive scope investigation
task-3-skill-plus-connector/  live email → 27.4s video, storyboard, frames
task-4-portable-handoff/      installable zip, proof it runs elsewhere
task-5-skill-audit/           safety assessment of the pdf Skill
REPORT.md                     the full report covering all five
```

**No secrets are committed.** No tokens, passwords, or OAuth credentials are in this repository.
Connector access was granted interactively through the browser and lives only in the local Claude
Code config, which is not part of this repo.
