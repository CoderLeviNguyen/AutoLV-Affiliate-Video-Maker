import asyncio
import os
import shutil
import subprocess
import uuid
from pathlib import Path

import edge_tts
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

BASE_DIR = Path(__file__).parent
TEMP_DIR = BASE_DIR / "temp_processing"
VIDEOS_DIR = BASE_DIR / "static" / "videos"
AUDIOS_DIR = BASE_DIR / "static" / "audios"
for p in (TEMP_DIR, VIDEOS_DIR, AUDIOS_DIR):
    p.mkdir(parents=True, exist_ok=True)

DEFAULT_VI_VOICE = os.getenv("DEFAULT_VI_VOICE", "vi-VN-HoaiMyNeural")

app = FastAPI(title="AutoLV Affiliate Video Maker API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/api/videos", StaticFiles(directory=VIDEOS_DIR), name="videos")
app.mount("/api/audios", StaticFiles(directory=AUDIOS_DIR), name="audios")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "autolv-affiliate-video-maker"}


@app.get("/api/voices")
def voices():
    return {
        "default": DEFAULT_VI_VOICE,
        "voices": [
            "vi-VN-HoaiMyNeural",
            "vi-VN-NamMinhNeural",
        ],
    }


async def create_voice(text: str, voice: str, output: Path) -> None:
    if not text.strip():
        raise HTTPException(status_code=400, detail="Nội dung voice không được để trống")
    try:
        communicate = edge_tts.Communicate(text.strip(), voice)
        await communicate.save(str(output))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Tạo giọng đọc thất bại: {exc}") from exc


@app.post("/api/generate-voice")
async def generate_voice(
    text: str = Form(...),
    voice: str = Form(DEFAULT_VI_VOICE),
):
    audio_id = uuid.uuid4().hex
    output = AUDIOS_DIR / f"{audio_id}.mp3"
    await create_voice(text, voice, output)
    return {
        "status": "success",
        "audio_id": audio_id,
        "audio_url": f"/api/audios/{output.name}",
        "voice": voice,
    }


def ffprobe_duration(path: Path) -> float:
    command = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def render_video(video: Path, audio: Path, output: Path, duration_mode: str) -> None:
    try:
        video_duration = ffprobe_duration(video)
        audio_duration = ffprobe_duration(audio)
    except Exception as exc:
        raise RuntimeError(f"Không đọc được thời lượng media: {exc}") from exc

    base = ["ffmpeg", "-y"]
    if duration_mode == "loop_video" or (duration_mode == "auto" and audio_duration > video_duration):
        base += ["-stream_loop", "-1", "-i", str(video), "-i", str(audio)]
        target_duration = audio_duration
    else:
        base += ["-i", str(video), "-i", str(audio)]
        target_duration = min(video_duration, audio_duration) if duration_mode == "trim_audio" else audio_duration

    command = base + [
        "-map", "0:v:0", "-map", "1:a:0",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{target_duration:.3f}",
        "-movflags", "+faststart", str(output),
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr[-3000:])


@app.post("/api/process-video")
async def process_video(
    video: UploadFile = File(...),
    prompt_text: str = Form(...),
    voice: str = Form(DEFAULT_VI_VOICE),
    duration_mode: str = Form("auto"),
):
    if duration_mode not in {"auto", "loop_video", "trim_audio"}:
        raise HTTPException(status_code=400, detail="duration_mode không hợp lệ")
    if not video.filename or Path(video.filename).suffix.lower() not in {".mp4", ".mov", ".avi", ".webm"}:
        raise HTTPException(status_code=400, detail="Định dạng video không hỗ trợ")

    job_id = uuid.uuid4().hex
    work_dir = TEMP_DIR / job_id
    work_dir.mkdir(parents=True, exist_ok=True)
    source_video = work_dir / f"input{Path(video.filename).suffix.lower()}"
    audio_path = work_dir / "voice.mp3"
    output_path = VIDEOS_DIR / f"{job_id}.mp4"

    try:
        with source_video.open("wb") as f:
            shutil.copyfileobj(video.file, f)
        await create_voice(prompt_text, voice, audio_path)
        await asyncio.to_thread(render_video, source_video, audio_path, output_path, duration_mode)
    except HTTPException:
        raise
    except Exception as exc:
        output_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Render video thất bại: {exc}") from exc
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

    return {
        "status": "success",
        "job_id": job_id,
        "video_url": f"/api/videos/{output_path.name}",
        "format": "1080x1920",
    }
