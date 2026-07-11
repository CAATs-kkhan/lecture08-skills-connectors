# Task 1 — Build Your First Real Skill

**Skill name:** `narration-to-video`
**Built with:** Claude Code (Opus 4.8) in VS Code
**Skill file:** [`skill/narration-to-video/SKILL.md`](skill/narration-to-video/SKILL.md)
**Renderer:** [`skill/narration-to-video/scripts/make_video.py`](skill/narration-to-video/scripts/make_video.py)

---

## The daily-life task it solves

I keep needing to explain the same thing to different people — a concept from class, a summary
of a document, an idea I want to share. Text gets skimmed and forgotten. A short narrated video
with clean graphics actually gets watched.

But making one by hand is a 40-minute job: write a script, time it, design slides, record a
voiceover, edit it together in some video tool. I was never going to do that regularly. So I
never made the videos.

**This Skill turns that 40-minute job into one sentence.** I say *"make a 30-second video about X"*
and I get a finished, narrated MP4.

The part that makes it genuinely mine: **it narrates in any language.** I need to explain things
in Urdu and in English to different audiences. Every consumer tool I found is English-first,
and Urdu support is either missing or an afterthought. This Skill treats them equally — the same
sentence, in the same format, in either language, with the slides automatically flipping to
right-to-left for Urdu, Arabic and Farsi.

---

## What it does

Give it **any** of these:

- a plain topic or a rough idea (*"make a video explaining what a Skill is"*)
- a PNG or JPEG (it looks at the image and narrates what is actually in it)
- a document, or notes, or a file from a connected app (see Task 3)

...and it produces a **≤30 second MP4** with animated graphics and a neural voiceover.

I never write a storyboard. The AI writes it from my request. I just say what I want.

## How it works

Four stages, and only one of them leaves the machine:

| Stage | Tool | Local? |
|---|---|---|
| 1. Speak the narration | `edge-tts` — neural voices, 100+ languages | ❌ text is sent to Microsoft's speech service |
| 2. Render each scene to a still | headless Chrome screenshot of a styled HTML page | ✅ local |
| 3. Ken Burns push + fades | `ffmpeg` | ✅ local |
| 4. Mux voice + visuals into MP4 | `ffmpeg` | ✅ local |

Five scene types — `title`, `bullets`, `stat` (one big number), `quote`, and `image`
(a full-bleed photo). Dependencies are fetched by `uv` on first run: no venv, no install step.

### Privacy — stated honestly

The narration **text** is sent to Microsoft's Edge speech service to be spoken. That is the
price of supporting 100+ languages, and the Skill says so in its own instructions. **Images,
documents, and the finished video never leave the machine.** The alternative — the Windows
built-in voice — is fully offline but English-only and robotic, which would have killed the
whole point of the Skill for me.

---

## Prompts I used

**Initial prompt (to build the Skill):**

> Is it possible if a user wants to enter or giving the prompt or png or jpeg in a narration
> form in any language then Claude code can work accordingly and make the output on a video in
> which good graphics, voice used, to a maximum 30 seconds video.

**How I refined it.** Claude pushed back usefully on two points, and the Skill is better for it:

1. **"Any language" was not free.** It checked my machine and found only two English voices
   (David and Zira) installed, so Windows' built-in speech engine could not deliver what I
   asked for. It offered `edge-tts` instead — 100+ languages, natural neural voices — and was
   upfront that this sends the narration text over the internet. I chose that tradeoff knowingly.
2. **It could not find ffmpeg.** Rather than telling me to go install it, it wired in a bundled
   copy via `uv`, so the Skill has no setup step at all.

**Trigger prompts (natural language — the Skill fires without being named):**

> make a 30 second video explaining what a Skill is
> turn this image into a narrated video
> make me a short explainer video about Skills and Connectors

---

## How I verified it worked

This is the part I would flag to anyone building a Skill like this.

The first render **exited successfully and produced a perfectly plausible 1.2 MB MP4.** Every
automated check said pass. But when I extracted frames from the finished video and *looked* at
them, **scene 1 was fine and scenes 2 and 3 were solid black.**

The cause was a subtle ffmpeg bug: `zoompan` with `d=N` emits N frames *for every input frame it
receives*, and `-loop 1` was feeding it an endless stream. Scene 1's clip stretched far past its
intended length, and because each clip fades to black at the end, the video stayed black forever
after that first fade-out. The audio was completely fine, which is exactly why it was invisible
to a naive check.

**Fix:** feed each still at a real frame rate (`-framerate 30`) and set `zoompan d=1`, so exactly
one output frame is emitted per input frame. Re-rendered, re-extracted the frames, confirmed all
three scenes were live.

**The lesson: "ffmpeg exited 0 and an MP4 appeared" is not verification.** For anything that
produces a video, you have to look at the pixels. See `screenshots/` for the extracted frames
and `demo-pipeline-test.mp4` for the working output.

---

## Files here

| File | What it is |
|---|---|
| `skill/narration-to-video/SKILL.md` | The Skill itself — name, description, instructions |
| `skill/narration-to-video/scripts/make_video.py` | The renderer (TTS → slides → ffmpeg) |
| `demo-pipeline-test.mp4` | Working output: 3 scenes, 16.6s, all scenes rendering |
| `screenshots/scene1-3.png` | Frames pulled from the finished video as proof |
| `prompts/` | The prompts used, and how they were refined |

---

## What worked, what didn't

**Worked.** The Skill triggers from a normal sentence without being named. The graphics look
genuinely good — gradient backgrounds, a radial accent wash, large clean typography, burned-in
captions that double as subtitles. The 30-second cap is enforced by the script, not by hope:
it measures the narration and speeds the voice up in stages if it overruns.

**Didn't work at first.**
- The black-scenes bug above — the real one, caught only by looking at frames.
- **Long narration is the #1 failure mode.** 30 seconds is about **75 words total**, which is far
  less than it feels like. I wrote the 75-word rule into the Skill in bold, because the model's
  instinct is to write far too much.
- Downloading ffmpeg the first time took ~15 minutes on a slow connection. It is cached after that.
