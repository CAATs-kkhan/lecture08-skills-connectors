---
name: narration-to-video
description: Turn a rough idea, some notes, or an image into a narrated explainer video of 30 seconds or less, with animated graphics and a voiceover in any language. Use this whenever the user asks to "make a video", "turn this into a video", "make a reel/short/explainer", "narrate this", "add a voiceover", or wants a spoken video summary of a document, an image, or a topic — including when the source material is in Urdu, Hindi, Arabic, or any other non-English language.
---

# Narration to Video

Turn anything the user gives you — a sentence, a pile of notes, a document, a PNG/JPEG —
into a narrated MP4 of **30 seconds or less**, with clean animated graphics and a neural
voiceover in whatever language they want.

The user never writes a storyboard. **You** write it. They just say what they want a video about.

## How it works

You produce one `storyboard.json`. A script does everything else:

1. `edge-tts` speaks each scene's narration (neural voice, 100+ languages)
2. Chrome renders each scene to a still image (headless screenshot)
3. `ffmpeg` adds a slow Ken Burns push on each still, fades between scenes, and lays the voice track over it

## Steps

### 1. Get the source material

- **Plain prompt / topic** — use it as the brief directly.
- **An image (PNG/JPEG)** — read it first, describe what is actually in it, and build the
  narration around what you see. Pass its absolute path as a scene's `image`.
- **A document, or "my latest Drive doc"** — read it via the relevant tool/connector,
  then summarize it down to the script below.

Do not ask a pile of questions. Infer, build a draft, show it, and offer to revise.
Only ask if the **language** or the **subject** is genuinely ambiguous.

### 2. Pick the voice

Match the user's requested language, or the language of their source material.
Ask only if you truly cannot tell.

| Language | Voice |
|---|---|
| English (US) | `en-US-AriaNeural` (f), `en-US-GuyNeural` (m) |
| English (UK) | `en-GB-SoniaNeural` (f) |
| Urdu | `ur-PK-UzmaNeural` (f), `ur-PK-AsadNeural` (m) |
| Hindi | `hi-IN-SwaraNeural` (f), `hi-IN-MadhurNeural` (m) |
| Arabic | `ar-SA-ZariyahNeural` (f), `ar-SA-HamedNeural` (m) |
| Spanish | `es-ES-ElviraNeural` (f) |
| French | `fr-FR-DeniseNeural` (f) |
| German | `de-DE-KatjaNeural` (f) |
| Chinese | `zh-CN-XiaoxiaoNeural` (f) |

Any other language: run `uv run --with edge-tts edge-tts --list-voices` and pick one whose
locale matches. Urdu, Arabic, Farsi and Hebrew switch the slides to right-to-left automatically.

### 3. Write the storyboard — THE 75-WORD RULE

**The single thing that breaks this skill is writing too much narration.**
Speech runs about 150 words per minute, so 30 seconds is **~75 words TOTAL across all scenes.**

- 4 to 6 scenes
- **12–15 words of narration per scene, and no more**
- Count the words before you run the script. If you are over 75, cut. Do not "trim later".
- Narration is what gets *spoken*; it is also burned in as an on-screen caption.
- Headings are what gets *read*. Keep them under ~28 characters or they shrink.
- Never make the narration a verbatim reading of the bullets — the bullets are the beat,
  the narration is the voice. They should complement, not echo.

Write the narration the way a person talks, not the way a slide reads.
Spell out things TTS mangles: "AI" → "A I", "30s" → "thirty seconds", "%" → "percent".

Save as `storyboard.json`:

```json
{
  "title": "Short name for the video",
  "voice": "en-US-AriaNeural",
  "theme": { "accent": "#38bdf8" },
  "scenes": [
    {
      "kind": "title",
      "kicker": "OPTIONAL EYEBROW",
      "heading": "The Big Idea",
      "narration": "Twelve to fifteen spoken words that open the video with a hook."
    },
    {
      "kind": "bullets",
      "heading": "How It Works",
      "bullets": ["First beat", "Second beat", "Third beat"],
      "narration": "Twelve to fifteen words that add colour the bullets do not state."
    },
    {
      "kind": "stat",
      "stat": "30s",
      "heading": "What it costs you",
      "narration": "A punchy line that lands the number."
    },
    {
      "kind": "image",
      "image": "C:/absolute/path/to/photo.jpg",
      "heading": "Optional overlay",
      "narration": "What the viewer should notice in this picture."
    },
    {
      "kind": "quote",
      "heading": "The line worth remembering",
      "narration": "Close on the takeaway."
    }
  ]
}
```

**Scene kinds:** `title` (opener, adds a rule), `bullets` (max 3, short), `stat` (one big
number — `stat` is the number, `heading` is what it means), `quote` (one strong line, set big
and italic), `image` (a full-bleed photo, dimmed, with optional text over it).

**Theme:** set `accent` to fit the mood — `#38bdf8` tech blue, `#34d399` green,
`#f472b6` pink, `#fbbf24` amber, `#a78bfa` violet. Any scene can override it with its own
`accent`. Optionally set `theme.bg` to a CSS gradient.

### 4. Render

```bash
uv run --with edge-tts --with imageio-ffmpeg python <skill>/scripts/make_video.py storyboard.json out.mp4
```

`uv` fetches the dependencies on first run — no venv, no install step, nothing to set up.
The script prints the narration length. If it overruns 30 seconds it speeds the voice up
in stages, and warns you if even that is not enough — **that warning means your script was
too long; go cut words, do not ship the sped-up version.**

### 5. Hand it back

Tell the user where the MP4 is, how long it actually came out, and what voice you used.
Offer one concrete revision (a different voice, a tighter script, a new accent colour).

## Privacy — say this once, the first time in a session

The narration **text** is sent to Microsoft's Edge speech service to be spoken —
that is how `edge-tts` works, and it needs an internet connection.
**Images, documents, and the finished video never leave the machine.**
If the user needs the text to stay local too, say so and stop: use a local
Windows SAPI voice instead (English only, and it sounds robotic).

## Gotchas

- **Chrome/Edge must be installed** — it is the renderer. The script finds it automatically.
- **`image` paths must be absolute**, with forward slashes.
- Long headings shrink automatically, but 3+ bullets of 10+ words each will still overflow. Be brief.
- If a voice name is wrong, `edge-tts` fails loudly. Check the locale spelling.
