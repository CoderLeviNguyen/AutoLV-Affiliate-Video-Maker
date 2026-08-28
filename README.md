# AutoLV Affiliate Video Maker

AutoLV Affiliate Video Maker is a Vietnamese-first affiliate video automation application inspired by `falconafk31/affiliate-video-maker`.

## Role in the AutoLV ecosystem

This repository is an **application/workflow layer**, not an identity, browser, social or voice platform service.

It should compose shared AutoLV services:

- `AutoLV-Accounts` for identity/entitlements.
- `AutoLV-Voice` for provider-neutral TTS/voice generation.
- `AutoLV-Social` for publishing/scheduling output.
- `AutoLV-Browser` only when a workflow requires browser automation.

Do not add a second account/OAuth system here and do not couple the application directly to ElevenLabs.

## Goals

- Generate Vietnamese affiliate hooks/scripts.
- Generate voiceovers through `AutoLV-Voice`.
- Keep Edge-TTS and Pollinations available through voice-provider adapters during migration.
- Support ElevenLabs through the planned `AutoLV-Voice` ElevenLabs provider rather than application-specific code.
- Merge voice + source product video with native FFmpeg.
- Support vertical 9:16 output for TikTok, Shopee, Facebook Reels, Instagram Reels and YouTube Shorts.
- Add a Remotion renderer layer for subtitles, price, voucher, CTA and animated layouts.
- Expose REST API + MCP tools so AutoLV agents can generate videos automatically.
- Send finished output to AutoLV Social for publishing/scheduling.

## Architecture

```text
Product / script
      |
      v
FastAPI workflow backend
 ├─ Vietnamese hook generation
 ├─ media upload
 ├─ voice request ---------------------> AutoLV Voice
 │                                        ├─ ElevenLabs
 │                                        ├─ Edge TTS
 │                                        ├─ Pollinations
 │                                        └─ future providers
 ├─ FFmpeg merge
 └─ render job API
      |
      v
Remotion renderer
 ├─ 1080x1920
 ├─ subtitle
 ├─ price / voucher
 ├─ CTA
 └─ animation
      |
      v
MP4
      |
      v
AutoLV Social
```

## Voice integration contract

Application code should call a provider-neutral interface similar to:

```json
{
  "text": "Vietnamese affiliate script",
  "provider": "auto",
  "voice_id": null,
  "format": "mp3"
}
```

The application should receive a normalized result independent of the provider:

```json
{
  "success": true,
  "audio_url": "...",
  "provider": "elevenlabs",
  "mode": "api",
  "usage": {}
}
```

Provider selection, quotas, API credentials and browser fallback belong to `AutoLV-Voice`, not this repository.

## Current local setup

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

## Current API

- `GET /api/health`
- `GET /api/voices`
- `POST /api/generate-voice`
- `POST /api/process-video`

These endpoints can remain as compatibility endpoints while their voice implementation is migrated behind the shared `AutoLV-Voice` service.

## Migration plan

1. Preserve the current local TTS path so existing workflows keep running.
2. Introduce an `AutoLVVoiceClient` adapter in the backend.
3. Route new voice generation through AutoLV Voice.
4. Keep direct/local Edge-TTS and Pollinations only as compatibility fallback until migration is complete.
5. Add ElevenLabs only inside AutoLV Voice.
6. Send completed media to AutoLV Social using its service/API contract.

## Credits

Based on ideas from: https://github.com/falconafk31/affiliate-video-maker

Upstream project is documented as MIT licensed. Preserve upstream attribution when reusing substantial source code.
