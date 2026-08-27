# AutoLV Affiliate Video Maker

AutoLV Affiliate Video Maker is a Vietnamese-first affiliate video automation toolkit inspired by `falconafk31/affiliate-video-maker`.

## Goals

- Generate Vietnamese affiliate hooks/scripts.
- Generate Vietnamese AI voiceovers with Edge-TTS or Pollinations.
- Merge voice + source product video with native FFmpeg.
- Support vertical 9:16 output for TikTok, Shopee, Facebook Reels, Instagram Reels and YouTube Shorts.
- Add a Remotion renderer layer for subtitles, price, voucher, CTA and animated layouts.
- Expose REST API + MCP tools so AutoLV agents can generate videos automatically.
- Prepare output for later AutoLV Social publishing integration.

## Architecture

```text
Product / script
      ↓
FastAPI backend
 ├─ Vietnamese hook generation
 ├─ TTS
 ├─ media upload
 ├─ FFmpeg merge
 └─ render job API
      ↓
Remotion renderer
 ├─ 1080x1920
 ├─ subtitle
 ├─ price / voucher
 ├─ CTA
 └─ animation
      ↓
MP4
      ↓
AutoLV Social (planned integration)
```

## Status

This repository starts as a clean AutoLV-oriented rewrite rather than a byte-for-byte copy. The useful ideas retained from the upstream project are FastAPI, Edge-TTS/Pollinations voice generation, FFmpeg media processing, Vue-based UI and MCP integration.

## Local setup

### Backend

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload --port 9000
```

### Remotion renderer

```bash
cd renderer
npm install
npm run studio
```

## Initial API

- `GET /api/health`
- `GET /api/voices`
- `POST /api/generate-voice`
- `POST /api/process-video`

## Credits

Based on ideas from: https://github.com/falconafk31/affiliate-video-maker

Upstream project is documented as MIT licensed. Preserve upstream attribution when reusing substantial source code.
