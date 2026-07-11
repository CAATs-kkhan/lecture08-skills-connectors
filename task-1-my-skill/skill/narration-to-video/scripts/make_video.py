#!/usr/bin/env python
"""Render a storyboard JSON into a narrated MP4 (<= 30s by default).

Pipeline, all local except the TTS call:
  1. edge-tts  -> one mp3 per scene (neural voice, 100+ languages)
  2. ffmpeg    -> normalise each mp3 to wav, pad with a short tail of silence
  3. Chrome    -> render each scene's HTML to a 2x PNG (headless screenshot)
  4. ffmpeg    -> Ken Burns each still, fade between scenes, mux the voice track

Run with uv so no venv setup is needed:
  uv run --with edge-tts --with imageio-ffmpeg make_video.py storyboard.json out.mp4
"""

from __future__ import annotations

import asyncio
import contextlib
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

MAX_SECONDS = 30.0
FPS = 30
W, H = 1920, 1080
TAIL_SILENCE = 0.35  # breathing room between scenes; fades happen over it
FADE = 0.3
# Tried in order until the narration fits inside MAX_SECONDS.
RATES = ["+0%", "+8%", "+16%", "+25%", "+35%"]

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/usr/bin/google-chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]


def find_chrome() -> str:
    for c in CHROME_CANDIDATES:
        if c and Path(c).exists():
            return c
    found = shutil.which("chrome") or shutil.which("google-chrome") or shutil.which("msedge")
    if found:
        return found
    sys.exit("Could not find Chrome or Edge to render the slides.")


def find_ffmpeg() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("No ffmpeg. Re-run with: uv run --with imageio-ffmpeg ...")


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"Command failed: {' '.join(cmd[:3])}...\n{proc.stderr[-2500:]}")


# --------------------------------------------------------------------------
# 1-2. voice
# --------------------------------------------------------------------------


async def _speak(text: str, voice: str, rate: str, out: Path) -> None:
    import edge_tts

    await edge_tts.Communicate(text, voice, rate=rate).save(str(out))


def synth_scene_audio(ffmpeg: str, text: str, voice: str, rate: str, work: Path, i: int) -> tuple[Path, float]:
    """Speak one scene, return its padded wav and that wav's duration."""
    mp3 = work / f"voice{i}.mp3"
    wav = work / f"voice{i}.wav"
    asyncio.run(_speak(text, voice, rate, mp3))
    run([ffmpeg, "-y", "-i", str(mp3), "-ar", "44100", "-ac", "2",
         "-af", f"apad=pad_dur={TAIL_SILENCE}", str(wav)])
    with contextlib.closing(wave.open(str(wav), "rb")) as w:
        dur = w.getnframes() / float(w.getframerate())
    return wav, dur


def synth_all(ffmpeg: str, scenes: list[dict], voice: str, work: Path) -> tuple[list[Path], list[float]]:
    """Speak every scene, speeding the voice up if the total overruns MAX_SECONDS."""
    for rate in RATES:
        wavs, durs = [], []
        for i, sc in enumerate(scenes):
            wav, dur = synth_scene_audio(ffmpeg, sc["narration"], voice, rate, work, i)
            wavs.append(wav)
            durs.append(dur)
        total = sum(durs)
        print(f"  narration at rate {rate}: {total:.1f}s")
        if total <= MAX_SECONDS:
            return wavs, durs
        print(f"  over the {MAX_SECONDS:.0f}s budget, retrying faster")
    print(f"  WARNING: still {total:.1f}s at the fastest rate; the video will be hard-cut at {MAX_SECONDS:.0f}s.")
    print("  Shorten the narration in the storyboard for a clean result.")
    return wavs, durs


# --------------------------------------------------------------------------
# 3. slides
# --------------------------------------------------------------------------

PAGE = """<!doctype html><html lang="{lang}" dir="{dir}"><meta charset="utf-8"><style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html,body {{ width:{W}px; height:{H}px; overflow:hidden; }}
  body {{
    font-family:"Segoe UI","Noto Nastaliq Urdu","Noto Sans Arabic","Noto Sans Devanagari",
                "Yu Gothic","Malgun Gothic","Microsoft YaHei",system-ui,sans-serif;
    background:{bg}; color:#f8fafc; position:relative;
    display:flex; flex-direction:column; justify-content:center;
    padding:120px 140px 190px; gap:34px;
  }}
  /* accent wash + vignette so flat colour never looks flat */
  body::before {{ content:""; position:absolute; inset:0;
    background:radial-gradient(120% 90% at {gx} 0%, {accent}44 0%, transparent 62%); }}
  body::after {{ content:""; position:absolute; inset:0;
    background:radial-gradient(140% 120% at 50% 50%, transparent 40%, #00000099 100%); }}
  .bg {{ position:absolute; inset:0; background-size:cover; background-position:center; opacity:.42; }}
  .layer {{ position:relative; z-index:2; }}
  .kicker {{ font-size:30px; font-weight:700; letter-spacing:.22em; text-transform:uppercase;
             color:{accent}; }}
  h1 {{ font-size:{h1}px; font-weight:800; line-height:1.1; letter-spacing:-.02em;
        text-shadow:0 6px 40px #00000066; }}
  .rule {{ width:180px; height:9px; border-radius:99px; background:{accent}; }}
  ul {{ list-style:none; display:flex; flex-direction:column; gap:26px; }}
  li {{ font-size:46px; line-height:1.35; font-weight:500; color:#e8edf5;
        display:flex; gap:26px; align-items:flex-start; }}
  li::before {{ content:""; flex:none; width:16px; height:16px; margin-top:20px;
                border-radius:99px; background:{accent}; }}
  .stat {{ font-size:210px; font-weight:800; line-height:1; color:{accent};
           text-shadow:0 10px 60px {accent}55; }}
  .quote {{ font-size:62px; line-height:1.35; font-weight:600; font-style:italic; }}
  /* burned-in caption: doubles as subtitles, keeps the frame from feeling empty */
  .cap {{ position:absolute; z-index:3; left:140px; right:140px; bottom:96px;
          font-size:32px; line-height:1.45; color:#cbd5e1; }}
  .bar {{ position:absolute; z-index:3; left:0; bottom:0; height:12px;
          width:{pct}%; background:{accent}; }}
</style>
<body>
  {bgdiv}
  <div class="layer">{body}</div>
  <div class="cap">{cap}</div>
  <div class="bar"></div>
</body></html>"""


def esc(s: str) -> str:
    return html.escape(str(s))


def scene_html(sc: dict, theme: dict, idx: int, total: int, rtl: bool, lang: str) -> str:
    kind = sc.get("kind", "bullets")
    accent = sc.get("accent") or theme.get("accent", "#38bdf8")
    bg = theme.get("bg", "linear-gradient(140deg,#0b1220 0%,#111c33 55%,#0a0f1c 100%)")
    parts = []

    if sc.get("kicker"):
        parts.append(f'<div class="kicker">{esc(sc["kicker"])}</div>')

    if kind == "stat":
        parts.append(f'<div class="stat">{esc(sc.get("stat", ""))}</div>')
        if sc.get("heading"):
            parts.append(f"<h1>{esc(sc['heading'])}</h1>")
    elif kind == "quote":
        parts.append(f'<div class="quote">&ldquo;{esc(sc.get("heading", ""))}&rdquo;</div>')
    else:
        if sc.get("heading"):
            parts.append(f"<h1>{esc(sc['heading'])}</h1>")
        if kind == "title":
            parts.append('<div class="rule"></div>')
        if sc.get("bullets"):
            lis = "".join(f"<li>{esc(b)}</li>" for b in sc["bullets"])
            parts.append(f"<ul>{lis}</ul>")

    bgdiv = ""
    if sc.get("image"):
        p = Path(sc["image"]).resolve().as_uri()
        bgdiv = f'<div class="bg" style="background-image:url(\'{p}\')"></div>'

    # Long headings need to shrink or they overflow the frame.
    hl = len(sc.get("heading", "") or "")
    h1 = 104 if hl <= 28 else 82 if hl <= 52 else 64

    return PAGE.format(
        W=W, H=H, lang=lang, dir="rtl" if rtl else "ltr", bg=bg, accent=accent,
        gx="82%" if idx % 2 else "18%", h1=h1,
        pct=round((idx + 1) / total * 100), bgdiv=bgdiv,
        body="".join(parts), cap=esc(sc["narration"]),
    )


def render_slides(chrome: str, scenes: list[dict], theme: dict, work: Path, rtl: bool, lang: str) -> list[Path]:
    pngs = []
    for i, sc in enumerate(scenes):
        page = work / f"scene{i}.html"
        png = work / f"scene{i}.png"
        page.write_text(scene_html(sc, theme, i, len(scenes), rtl, lang), encoding="utf-8")
        run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-sandbox",
             "--force-device-scale-factor=2", f"--window-size={W},{H}",
             "--virtual-time-budget=2500", f"--screenshot={png}", page.resolve().as_uri()])
        if not png.exists():
            sys.exit(f"Chrome did not produce a screenshot for scene {i}.")
        pngs.append(png)
    return pngs


# --------------------------------------------------------------------------
# 4. mux
# --------------------------------------------------------------------------


def build_video(ffmpeg: str, pngs: list[Path], wavs: list[Path], durs: list[float],
                work: Path, out: Path) -> None:
    listing = work / "audio.txt"
    listing.write_text("".join(f"file '{w.resolve().as_posix()}'\n" for w in wavs), encoding="utf-8")
    voice = work / "voice.wav"
    run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(voice)])

    # Feed each still as a real FPS-rate stream and let zoompan emit exactly one frame per
    # input frame (d=1). With d>1 zoompan emits d frames *per input frame*, which stretches
    # the first clip past its fade-out and leaves the rest of the video black.
    cmd = [ffmpeg, "-y"]
    for png, dur in zip(pngs, durs):
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", str(png)]
    cmd += ["-i", str(voice)]

    zoom = 0.12  # total Ken Burns push, spread evenly across the scene's own length
    chains = []
    for i, dur in enumerate(durs):
        frames = max(int(round(dur * FPS)), 2)
        step = zoom / frames
        # Alternate the direction so consecutive scenes don't feel identical.
        z = (f"min(1+{step:.6f}*on,{1 + zoom})" if i % 2 == 0
             else f"max({1 + zoom}-{step:.6f}*on,1)")
        fade_out = max(dur - FADE, 0.01)
        chains.append(
            f"[{i}:v]scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,"
            f"zoompan=z='{z}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":s={W}x{H}:fps={FPS},setsar=1,"
            f"fade=t=in:st=0:d={FADE},fade=t=out:st={fade_out:.3f}:d={FADE}[v{i}]"
        )
    chains.append("".join(f"[v{i}]" for i in range(len(durs))) + f"concat=n={len(durs)}:v=1:a=0[outv]")

    cmd += [
        "-filter_complex", ";".join(chains),
        "-map", "[outv]", "-map", f"{len(durs)}:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
        "-t", str(MAX_SECONDS), str(out),
    ]
    run(cmd)


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit("usage: make_video.py <storyboard.json> <out.mp4>")
    # utf-8-sig, not utf-8: PowerShell and Notepad write a BOM, which json.loads rejects.
    sb = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
    out = Path(sys.argv[2]).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    scenes = sb["scenes"]
    voice = sb.get("voice", "en-US-AriaNeural")
    lang = sb.get("language", voice.rsplit("-", 1)[0] if "-" in voice else "en")
    rtl = sb.get("rtl", lang.split("-")[0] in {"ur", "ar", "fa", "he", "ps", "sd"})
    theme = sb.get("theme", {})

    ffmpeg, chrome = find_ffmpeg(), find_chrome()
    print(f"scenes={len(scenes)} voice={voice} rtl={rtl}")

    with tempfile.TemporaryDirectory(prefix="n2v_") as tmp:
        work = Path(tmp)
        print("[1/3] speaking narration...")
        wavs, durs = synth_all(ffmpeg, scenes, voice, work)
        print("[2/3] rendering slides...")
        pngs = render_slides(chrome, scenes, theme, work, rtl, lang)
        print("[3/3] muxing video...")
        build_video(ffmpeg, pngs, wavs, durs, work, out)

    print(f"\nDone: {out}  ({sum(durs):.1f}s, {out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
