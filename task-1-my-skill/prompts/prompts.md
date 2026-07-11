# Prompts used — Task 1 (`narration-to-video`)

## 1. The initial prompt (building the Skill)

> Is it possible if a user wants to enter or giving the prompt or png or jpeg in a narration form
> in any language then Claude code can work accordingly and make the output on a video in which
> good graphics, voice used, to a maximum 30 seconds video.

## 2. How it was refined

The prompt asked for something the machine could not actually do as stated. Two things changed,
both forced by reality rather than taste:

**"Any language" was not free.**
Claude checked the machine and found only **two English voices** installed (Microsoft David and
Zira, both `en-US`). Windows' built-in speech engine physically could not narrate in Urdu. It
offered `edge-tts` instead — 100+ languages, natural neural voices — and stated the cost plainly:
**the narration text is sent to Microsoft's speech servers.** Images, documents and the finished
video stay local.

> **Decision:** accept `edge-tts`. "Any language" was the whole reason for the Skill; an
> English-only offline voice would have defeated the point. The tradeoff is now documented inside
> `SKILL.md` so anyone using the Skill is told once, up front.

**ffmpeg was not installed.**
Rather than requiring a manual install, the Skill pulls a bundled ffmpeg through `uv` at first
run. The Skill now has **no setup step**.

## 3. Trigger prompts (natural language — the Skill is never named)

These are the sentences that make the Skill fire on its own:

> make a 30 second video explaining what a Skill is

> turn this image into a narrated video

> make me a short explainer video about Skills and Connectors

> اردو میں ایک تیس سیکنڈ کی ویڈیو بنائیں   *(make a 30-second video in Urdu)*

## 4. The Task 3 prompt (Skill + Connector together)

> Make a 30-second video from the DigiSkills email in my inbox.

One sentence. The Connector fetched the live email; the Skill triggered without being named,
wrote the storyboard from the email's real contents, and rendered the MP4.

## 5. The rule I had to write into the Skill

The single most common failure was **narration that was far too long.** Speech runs at roughly 150
words per minute, so **30 seconds is about 75 words total** — much less than it feels like. The
model's instinct is to write two or three times that.

`SKILL.md` now states the 75-word budget in bold, with a per-scene limit of 12–15 words, and the
renderer *enforces* the cap: it measures the narration and speeds the voice up in stages if it
overruns, warning you if even that is not enough.
