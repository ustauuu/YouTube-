import os
import subprocess
from pathlib import Path
from gtts import gTTS
from pydub import AudioSegment
import math

OUT = Path("out")
OUT.mkdir(exist_ok=True)

def text_to_speech(text, out_path):
    tts = gTTS(text, lang="tr")
    tmp_mp3 = out_path.with_suffix(".mp3")
    tts.save(str(tmp_mp3))
    # normalize with pydub (optional)
    audio = AudioSegment.from_file(tmp_mp3)
    audio.export(out_path, format="mp3")
    return out_path

def make_srt_from_sentences(sentences, durations, out_path):
    # sentences: list[str], durations: list[float] in seconds
    with open(out_path, "w", encoding="utf-8") as f:
        cursor = 0.0
        for i, (s, d) in enumerate(zip(sentences, durations), start=1):
            start_ms = int(cursor * 1000)
            end_ms = int((cursor + d) * 1000)
            def fmt(ms):
                h = ms//3600000
                m = (ms%3600000)//60000
                s_ = (ms%60000)//1000
                ms_ = ms%1000
                return f"{h:02}:{m:02}:{s_:02},{ms_:03}"
            f.write(f"{i}\n")
            f.write(f"{fmt(start_ms)} --> {fmt(end_ms)}\n")
            f.write(s.strip() + "\n\n")
            cursor += d

def split_into_sentences(text):
    # very simple split by dot/newline — improve with NLP if needed
    parts = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        for p in line.split("."):
            p = p.strip()
            if p:
                parts.append(p + ".")
    if not parts:
        parts = [text]
    return parts

def process_content_file(txt_path: Path):
    title = txt_path.stem
    text = txt_path.read_text(encoding="utf-8")
    # 1) TTS
    audio_out = OUT / f"{title}.mp3"
    print("Generating TTS...")
    text_to_speech(text, audio_out)

    # get audio duration
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
                        str(audio_out)], capture_output=True, text=True)
    duration = float(p.stdout.strip())
    print("Audio duration:", duration)

    # 2) Subtitles: split into sentences and distribute durations proportionally by length
    sentences = split_into_sentences(text)
    total_chars = sum(len(s) for s in sentences)
    durations = []
    for s in sentences:
        frac = len(s) / total_chars
        durations.append(max(1.0, frac * duration))  # minimum 1s each
    # adjust to exactly match duration
    total_assigned = sum(durations)
    if total_assigned > 0:
        scale = duration / total_assigned
        durations = [d * scale for d in durations]

    srt_out = OUT / f"{title}.srt"
    make_srt_from_sentences(sentences, durations, srt_out)

    # 3) Video: Use a cover image if present in content/ with same stem, else fallback to default
    cover_jpg = txt_path.with_suffix(".jpg")
    if not cover_jpg.exists():
        cover_jpg = Path("cover.jpg")
        if not cover_jpg.exists():
            raise FileNotFoundError("No cover.jpg found; place one in repo root or add matching .jpg next to .txt")

    temp_video = OUT / f"{title}_tmp.mp4"
    final_video = OUT / f"{title}.mp4"

    # ffmpeg: loop image + audio -> video
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(cover_jpg),
        "-i", str(audio_out),
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-vf", "scale=1280:720,format=yuv420p",
        str(temp_video)
    ]
    print("Running ffmpeg to make video...")
    subprocess.check_call(cmd)

    # 4) mux subtitles (mov_text)
    cmd2 = [
        "ffmpeg", "-y",
        "-i", str(temp_video),
        "-i", str(srt_out),
        "-c", "copy",
        "-c:s", "mov_text",
        str(final_video)
    ]
    print("Adding subtitles...")
    subprocess.check_call(cmd2)

    # cleanup tmp
    temp_video.unlink(missing_ok=True)
    print("Generated:", final_video)
    # optional: call upload_youtube.upload(final_video, title, description)
