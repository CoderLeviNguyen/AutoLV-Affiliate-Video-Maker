import asyncio
import subprocess
import uuid
from pathlib import Path

import edge_tts
from mcp.server.fastmcp import FastMCP

BASE_DIR = Path(__file__).parent
TEMP_DIR = BASE_DIR / "temp_processing"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

mcp = FastMCP("autolv-affiliate-video-maker")


@mcp.tool()
def generate_vietnamese_voice(text: str, voice: str = "vi-VN-HoaiMyNeural") -> str:
    """Create a Vietnamese MP3 voiceover and return its absolute path."""
    if not text.strip():
        raise ValueError("text cannot be empty")
    output = TEMP_DIR / f"voice_{uuid.uuid4().hex}.mp3"

    async def run():
        await edge_tts.Communicate(text.strip(), voice).save(str(output))

    asyncio.run(run())
    return str(output.resolve())


@mcp.tool()
def merge_video_and_voice(video_path: str, audio_path: str, mode: str = "auto") -> str:
    """Merge source video and AI voice with native FFmpeg into a 1080x1920 MP4."""
    video = Path(video_path)
    audio = Path(audio_path)
    if not video.exists():
        raise FileNotFoundError(video_path)
    if not audio.exists():
        raise FileNotFoundError(audio_path)
    if mode not in {"auto", "loop_video", "trim_audio"}:
        raise ValueError("mode must be auto, loop_video, or trim_audio")

    output = TEMP_DIR / f"video_{uuid.uuid4().hex}.mp4"
    command = ["ffmpeg", "-y"]
    if mode in {"auto", "loop_video"}:
        command += ["-stream_loop", "-1"]
    command += [
        "-i", str(video), "-i", str(audio),
        "-map", "0:v:0", "-map", "1:a:0",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-shortest", "-movflags", "+faststart", str(output),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        output.unlink(missing_ok=True)
        raise RuntimeError(result.stderr[-3000:])
    return str(output.resolve())


if __name__ == "__main__":
    mcp.run()
