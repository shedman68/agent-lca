"""
Adds a generic English voice-over and quiet generated background music to the demo walkthrough.

Input : submission/media/agent-lca-demo-walkthrough.mp4 (111.8 s, no audio; Rashed's file, not changed)
Output: analysis/media/agent-lca-demo-walkthrough-voice.mp4 (same video stream, plus an AAC audio track)

- Voice: Windows offline text-to-speech (System.Speech, "Microsoft Zira Desktop", en-US). No cloud service.
- Music: a soft four-chord pad synthesised here with numpy (no third-party audio, no licence question),
  ducked under the voice.
- Script: the lines follow the on-screen captions at the same moments, so picture, captions and voice say the same.
  Every number is one already shown in the video and checked against out/ and measures/ (analysis/kb/submission-check.md).

Usage: python analysis/media/make_voiceover.py   (needs: pip install imageio-ffmpeg numpy)
"""
import subprocess, tempfile, wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "submission/media/agent-lca-demo-walkthrough.mp4"
OUT = ROOT / "analysis/media/agent-lca-demo-walkthrough-voice.mp4"
SR, DUR = 44100, 111.8

# (start second, text) – aligned with the captions in the video
LINES = [
    (0.6, "GreenOps Basel."),
    (4.2, "A Basel company spends four hundred and seventy thousand francs a year on cloud, servers, AI and software. "
          "Where does the CO2 come from?"),
    (14.6, "Every number comes from the sample data. CO2 comes first, with low, mid and high factors."),
    (21.6, "The findings show what, where and how much, each with its source."),
    (28.2, "The biggest lever is the development data platform in Frankfurt."),
    (35.0, "Planted texts in the data are refused, not followed. Protected systems are never switched off."),
    (48.6, "The package cuts CO2 by forty-three percent and cost by twenty-eight point six percent, "
           "in fourteen and a half of fifteen person-days."),
    (56.6, "It passes on low, mid and high factors: forty-nine point six, forty-three, and forty-two point two percent."),
    (63.4, "Every decision that needs a human names the responsible role and the protection window."),
    (77.0, "Ask the data: an offline assistant that answers only from the computed tables."),
    (91.0, "Next year: growth from the new production platform, and our own AI footprint, counted so far."),
    (104.6, "GreenOps Basel. A safe CO2 package that an SME manager understands in two minutes."),
]


def tts(text: str, path: Path, rate: int = 0) -> None:
    ps = (
        "Add-Type -AssemblyName System.Speech;"
        "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
        "$s.SelectVoice('Microsoft Zira Desktop');"
        f"$s.Rate={rate};"
        "$f=New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(44100,"
        "[System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen,[System.Speech.AudioFormat.AudioChannel]::Mono);"
        f"$s.SetOutputToWaveFile('{path}',$f);"
        f"$s.Speak(\"{text}\");$s.Dispose()"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)


def read_wav(path: Path) -> np.ndarray:
    with wave.open(str(path)) as w:
        assert w.getframerate() == SR and w.getsampwidth() == 2
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


def pad_music(n: int) -> np.ndarray:
    """Soft pad: Am - F - C - G, 8 s per chord, sine + octave, slow fades between chords."""
    t = np.arange(n) / SR
    chords = [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [130.81, 196.0, 261.63], [196.0, 246.94, 293.66]]
    out = np.zeros(n, dtype=np.float32)
    seg = 8.0
    for i in range(int(np.ceil(n / SR / seg))):
        a, b = int(i * seg * SR), min(n, int((i + 1) * seg * SR + SR))   # 1 s overlap
        tt = t[a:b] - t[a]
        env = np.minimum(1, tt / 1.5) * np.minimum(1, (tt[-1] - tt) / 1.5)
        x = sum(np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt) for f in chords[i % 4])
        out[a:b] += (x * env).astype(np.float32)
    out *= 1 + 0.15 * np.sin(2 * np.pi * 0.1 * t)                       # gentle movement
    return out / np.abs(out).max()


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    n = int(DUR * SR)
    voice = np.zeros(n, dtype=np.float32)
    report = []
    for i, (start, text) in enumerate(LINES):
        p = tmp / f"l{i}.wav"
        tts(text, p)
        x = read_wav(p)
        end_free = LINES[i + 1][0] if i + 1 < len(LINES) else DUR
        if start + len(x) / SR > end_free - 0.2:                         # too long for its slot: speak faster
            tts(text, p, rate=2)
            x = read_wav(p)
        a = int(start * SR)
        x = x[: max(0, n - a)]
        voice[a:a + len(x)] += x
        report.append(f"{start:6.1f}s  {len(x) / SR:4.1f}s  ends {start + len(x) / SR:6.1f}s / next {end_free:6.1f}s  {text[:60]}")
    # ducking envelope: music at -20 dB under speech, -12 dB otherwise (moving averages via cumulative sums: O(n))
    def smooth(x: np.ndarray, k: int) -> np.ndarray:
        c = np.concatenate([[0.0], np.cumsum(x, dtype=np.float64)])
        idx = np.arange(len(x))
        lo, hi = np.clip(idx - k // 2, 0, len(x)), np.clip(idx + k // 2 + 1, 0, len(x))
        return ((c[hi] - c[lo]) / (hi - lo)).astype(np.float32)
    active = smooth((np.abs(voice) > 0.01).astype(np.float32), int(0.4 * SR)) > 0.02
    gain = smooth(np.where(active, 0.10, 0.25).astype(np.float32), int(0.3 * SR))
    music = pad_music(n) * gain
    fade = np.minimum(1, np.arange(n) / (2 * SR)) * np.minimum(1, (n - np.arange(n)) / (3 * SR))
    mix = voice * 0.9 + music * fade
    mix = mix / max(1.0, np.abs(mix).max() / 0.95)
    wav = tmp / "mix.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-y", "-i", str(SRC), "-i", str(wav), "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", str(OUT)], check=True)
    print("\n".join(report))
    print("wrote", OUT, f"{OUT.stat().st_size / 1e6:.1f} MB")
