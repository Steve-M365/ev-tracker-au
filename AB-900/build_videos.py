#!/usr/bin/env python3
"""AB-900 Video Production Pipeline — generates narration audio + slide images + final MP4 per lesson."""
import os, re, glob, textwrap
from pathlib import Path
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
import numpy as np

BASE = Path("/home/a-steve/workspace")
AUDIO_DIR = BASE / "audio"
SLIDE_DIR = BASE / "slides"
VIDEO_DIR = BASE / "videos"
AUDIO_DIR.mkdir(exist_ok=True)
SLIDE_DIR.mkdir(exist_ok=True)
VIDEO_DIR.mkdir(exist_ok=True)

# Brand colours
BG = "#061b31"       # deep navy
CARD = "#ffffff"     # white cards
ACCENT = "#533afd"   # purple accent
TEXT = "#1a1a1a"     # near-black
SUBTITLE = "#4a4a4a" # grey

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def get_font(size, bold=False):
    path = FONT_BOLD if bold else FONT_PATH
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def parse_lesson(path):
    text = path.read_text(encoding="utf-8")
    # Extract lesson code
    code_match = re.search(r'# (AB-900 [^\n]+)', text)
    code = code_match.group(1) if code_match else path.stem
    # Extract duration
    dur_match = re.search(r'Duration:\s*(\d+)\s*min', text)
    duration_min = int(dur_match.group(1)) if dur_match else 14
    # Extract objective
    obj_match = re.search(r'Objective:\s*([^\n]+)', text)
    objective = obj_match.group(1).strip() if obj_match else ""
    # Extract script excerpt
    script_match = re.search(r'Script excerpt:\s*"([^"]+)"', text)
    script = script_match.group(1).strip() if script_match else text[:800]
    # Extract key terms
    terms_match = re.findall(r'-\s+([A-Za-z][A-Za-z0-9 /]+)', text)
    # Extract common mistakes
    mistakes_match = re.search(r'Mistakes:\s*(.+?)(?:\n\n|\Z)', text, re.DOTALL)
    mistakes = mistakes_match.group(1).strip() if mistakes_match else ""
    # Extract recap
    recap_match = re.search(r'Recap.*?:\s*(.+?)(?:\n\n|\Z)', text, re.DOTALL)
    recap = recap_match.group(1).strip() if recap_match else ""
    return {
        "code": code,
        "duration_min": duration_min,
        "objective": objective,
        "script": script,
        "terms": terms_match[:8],
        "mistakes": mistakes,
        "recap": recap,
    }

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = current + (" " if current else "") + word
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def create_slide(title, subtitle, body_lines, footer, slide_num, total_slides, output_path):
    W, H = 1920, 1080
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    # Fonts
    font_title = get_font(64, bold=True)
    font_sub = get_font(36)
    font_body = get_font(30)
    font_footer = get_font(24)
    font_slide = get_font(22)
    # Accent bar top
    draw.rectangle([0, 0, W, 12], fill=ACCENT)
    # Title
    y = 60
    title_lines = wrap_text(title, font_title, W - 120, draw)
    for line in title_lines:
        draw.text((80, y), line, font=font_title, fill=CARD)
        y += 80
    # Subtitle
    if subtitle:
        y += 20
        sub_lines = wrap_text(subtitle, font_sub, W - 120, draw)
        for line in sub_lines:
            draw.text((80, y), line, font=font_sub, fill=ACCENT)
            y += 50
    # Divider
    y += 20
    draw.line([(80, y), (W - 80, y)], fill=ACCENT, width=3)
    # Body
    y += 30
    for line in body_lines[:12]:
        draw.text((80, y), line, font=font_body, fill=CARD)
        y += 44
    # Footer
    if footer:
        draw.text((80, H - 60), footer, font=font_footer, fill=SUBTITLE)
    # Slide number
    draw.text((W - 120, H - 60), f"{slide_num}/{total_slides}", font=font_slide, fill=SUBTITLE)
    img.save(output_path, "PNG")

def build_slides(lesson, lesson_dir):
    slides = []
    code = lesson["code"]
    # Slide 1: Title
    slides.append(("title", f"{code}", "Microsoft 365 Copilot and Agent Administration Fundamentals", ""))
    # Slide 2: Objective
    slides.append(("objective", "Learning Objective", lesson["objective"], ""))
    # Slide 3: Key terms
    terms_text = "\n".join([f"• {t}" for t in lesson["terms"][:8]])
    slides.append(("terms", "Key Terms", terms_text, ""))
    # Slide 4: Common mistakes
    slides.append(("mistakes", "Common Mistakes", lesson["mistakes"], ""))
    # Slide 5: Recap
    slides.append(("recap", "Recap", lesson["recap"], "Next lesson..."))
    total = len(slides)
    paths = []
    for i, (stype, title, body, footer) in enumerate(slides, 1):
        out = lesson_dir / f"slide_{i:02d}_{stype}.png"
        create_slide(title, "", body.split("\n"), footer, i, total, out)
        paths.append(str(out))
    return paths

def build_video(lesson, lesson_dir, stem):
    code_clean = stem
    audio_path = AUDIO_DIR / f"{code_clean}.mp3"
    # Generate TTS
    narration = lesson["script"]
    if not audio_path.exists():
        tts = gTTS(narration, lang="en", tld="com.au")
        tts.save(str(audio_path))
    # Build slides
    slide_paths = build_slides(lesson, lesson_dir)
    # Duration per slide = audio duration / num_slides (min 3s each)
    try:
        audio_clip = AudioFileClip(str(audio_path))
        audio_dur = audio_clip.duration
        audio_clip.close()
    except Exception:
        audio_dur = 30.0
    min_per_slide = 3.0
    slide_dur = max(min_per_slide, audio_dur / len(slide_paths))
    clips = []
    for sp in slide_paths:
        clip = ImageClip(sp, duration=slide_dur)
        clips.append(clip)
    video = concatenate_videoclips(clips, method="compose")
    # Add audio
    try:
        audio = AudioFileClip(str(audio_path))
        # If audio is shorter than video, extend by repeating
        if audio.duration < video.duration:
            # moviepy 2.x: multiply audio to extend duration
            audio = audio.with_duration(video.duration)
        video = video.with_audio(audio)
    except Exception as e:
        print(f"  Audio attach failed: {e}")
    out_path = VIDEO_DIR / f"{code_clean}.mp4"
    video.write_videofile(str(out_path), fps=24, codec="libx264", audio_codec="aac", logger=None)
    video.close()
    try:
        audio.close()
    except Exception:
        pass
    return out_path

def main():
    files = sorted(glob.glob(str(BASE / "AB-900_M*_*.md")))
    print(f"Found {len(files)} lesson files.")
    for f in files:
        p = Path(f)
        lesson = parse_lesson(p)
        lesson_dir = BASE / p.stem
        lesson_dir.mkdir(exist_ok=True)
        print(f"Processing {lesson['code']}...")
        try:
            vid = build_video(lesson, lesson_dir, p.stem)
            print(f"  -> {vid}")
        except Exception as e:
            print(f"  FAILED: {e}")
    print("Done.")

if __name__ == "__main__":
    main()
