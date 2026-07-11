# Task 4 — Make It Portable or Hand It Off

**Path chosen:** *Make it portable* — moved the Skill out of the conversation that created it and
ran it somewhere else.
**Result:** ✅ It works, and **the move exposed a real bug that the original environment was hiding.**

---

## What "portable" actually means here

The Skill was **built** inside this project folder. But a Skill that only works in the folder
where it was written is not an asset — it's a one-time trick. So I installed it to the
**user-level** Skills directory:

```
C:\Users\user\.claude\skills\narration-to-video\
├── SKILL.md
└── scripts\make_video.py
```

From there it is available in **every Claude Code session, in every project, on this machine** —
not just this one. That is the difference between a Skill and a clever prompt.

## Proof 1 — it runs from a completely different directory

I ran the **installed** Skill from a scratch folder with no connection to this project, and
changed things it had never seen before: a **different voice** (`en-US-GuyNeural` instead of
Aria) and a **different accent colour** (green instead of blue).

It produced `portable-proof.mp4` — 9.5 seconds, both scenes rendering correctly. Nothing was
re-explained to it. See `screenshots/`.

## Proof 2 — the handoff bundle

`narration-to-video-skill.zip` is the complete Skill, ready to give to someone else. To use it,
they unzip it into their own Skills folder:

| OS | Where it goes |
|---|---|
| Windows | `C:\Users\<name>\.claude\skills\narration-to-video\` |
| macOS / Linux | `~/.claude/skills/narration-to-video/` |

Then, in any new session, they just say *"make a 30-second video about X"* — with **no
explanation from me**. There is nothing to install: `uv` fetches `edge-tts` and `ffmpeg` on the
first run, and Chrome (already on any normal machine) does the rendering.

---

## The bug the move exposed — this is the real value of Task 4

**Moving the Skill broke it, and that is exactly why the task is worth doing.**

When I ran it from the new folder, it crashed immediately:

```
json.decoder.JSONDecodeError: Unexpected UTF-8 BOM (decode using utf-8-sig)
```

The reason: in the new environment I created the storyboard with **PowerShell**, and PowerShell's
`Out-File -Encoding utf8` writes a **byte-order mark** at the start of the file. Python's
`json.loads` refuses to parse it. In the original environment, every storyboard had been written
by Claude's own file tools, which don't add a BOM — so the bug was **completely invisible**. It
had been there the whole time, waiting for the first person who wrote a storyboard with a normal
Windows tool like PowerShell or Notepad.

**Fixed** by reading the file as `utf-8-sig`, which accepts a BOM if present and works fine
without one. Re-ran from the new folder — it worked.

This is the point of the task, and it is not a trivial one: **a Skill that has only ever run in
the environment that created it has not really been tested.** The environment quietly supplies
assumptions you don't know you're making. The only way to find them is to take the Skill
somewhere else and watch what falls over. If I had handed this zip to a classmate without doing
this, the first thing they'd have seen is a crash.

---

## How to reproduce the portability proof yourself

The Skill is already installed on this machine, so you can prove this in a fresh session:

1. Open a **brand-new Claude Code session in any other folder** (not this project).
2. Type a normal sentence — **do not name the Skill**:
   > `make a 30-second video explaining what a Connector is`
3. The Skill fires on its own, writes a storyboard, and renders the MP4.

Screenshot that session for the submission: the point is that it triggers **from natural
language, in a project it has never seen, with no setup and no re-explanation.**

---

## Files here

| File | What it is |
|---|---|
| `narration-to-video-skill.zip` | The complete Skill, ready to hand to another person |
| `portable-proof.mp4` | Made by the installed Skill from a different directory, different voice/colour |
| `screenshots/` | Frames from that video, proving it rendered correctly outside its original home |
