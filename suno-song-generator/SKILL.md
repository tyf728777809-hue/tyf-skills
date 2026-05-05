---
name: suno-song-generator
description: Generate and manage songs with the GPT Best / Suno API. Use when the user asks to create songs from prompts or lyrics, make instrumental tracks, continue or upload-extend audio, cover/remix songs, replace sections, use Persona singer styles, generate lyrics, expand style tags, split vocals/instrumentals, fetch timing/WAV/MP4/MIDI assets, upload source audio, poll Suno task results, or work with Suno v1-compatible endpoints.
---

# Suno Song Generator

## Workflow

1. Identify the Suno task: new song, lyrics, instrumental, extend, upload, cover, replace/infill, persona, stems, timing, export, or v1 compatibility.
2. Read `references/suno-api.md` when choosing a non-trivial mode, model version, upload flow, advanced parameter, or endpoint.
3. Use `scripts/suno_song.py` for API calls. Prefer `--dry-run` before real submit, upload, concat, persona, or stems operations because they may consume credits or upload user files.
4. Read credentials from environment variables only:
   - `SUNO_API_BASE_URL` or `GPT_BEST_API_BASE_URL`
   - `SUNO_API_KEY` or `GPT_BEST_API_KEY`
5. Do not paste, log, store, or echo API keys. The CLI redacts Authorization headers and does not include secrets in saved JSON.
6. For async work, submit the task, then use `--wait` or `fetch`/`fetch-batch` to poll until complete. Return task IDs, clip IDs, status, fail reasons, and result URLs.
7. Download generated audio/video/image assets only when the user asks or when `--download --output-dir <dir>` is appropriate.

## Common Commands

Run commands from this skill folder or pass the script path explicitly.

Check local configuration:

```bash
python scripts/suno_song.py check
```

Preview a custom song request without sending it:

```bash
python scripts/suno_song.py --dry-run submit-music --mode custom --title "Night Shift" --tags "synth pop, clean vocal" --prompt "Lyrics or detailed creative prompt"
```

Generate and wait for results:

```bash
python scripts/suno_song.py --wait --download --output-dir out submit-music --mode custom --title "Night Shift" --tags "synth pop" --prompt-file lyrics.txt
```

Generate from inspiration:

```bash
python scripts/suno_song.py submit-music --mode inspiration --description "一首关于乡愁的温柔中文民谣"
```

Create instrumental music:

```bash
python scripts/suno_song.py submit-music --mode instrumental --title "Orbit" --tags "cinematic ambient, piano" --prompt ""
```

Continue, cover, or replace an existing clip:

```bash
python scripts/suno_song.py submit-music --mode extend --continue-clip-id <clip_id> --continue-at 92.5 --title "Full Song" --tags "rock" --prompt-file next-section.txt
python scripts/suno_song.py submit-music --mode cover --cover-clip-id <clip_id> --title "Remix" --tags "house" --prompt-file lyrics.txt
python scripts/suno_song.py submit-music --mode replace --continue-clip-id <clip_id> --infill-start-s 50 --infill-end-s 64.8 --title "Fixed Verse" --tags "pop punk" --prompt-file replacement.txt
```

Upload a local audio file, wait for initialization, then use the returned `clip_id`:

```bash
python scripts/suno_song.py --wait upload-file /path/to/source.mp3
python scripts/suno_song.py submit-music --mode upload-extend --continue-clip-id <uploaded_clip_id> --continue-at 10 --title "Extended Upload" --tags "pop" --prompt "new lyrics"
```

Fetch or batch-fetch tasks:

```bash
python scripts/suno_song.py fetch <task_id>
python scripts/suno_song.py fetch-batch <task_id_1> <task_id_2> --action MUSIC
```

Use supporting tools:

```bash
python scripts/suno_song.py lyrics-submit --prompt "dance song about summer" --wait
python scripts/suno_song.py tags "laid-back indie pop"
python scripts/suno_song.py persona-create --root-clip-id <clip_id> --name "Warm Vocal" --description "clear warm singer" --public
python scripts/suno_song.py concat <extended_clip_id> --is-infill false
python scripts/suno_song.py timing <clip_id>
python scripts/suno_song.py wav <clip_id>
python scripts/suno_song.py mp4 <clip_id>
python scripts/suno_song.py midi <clip_id>
```

Use v1-compatible endpoints only when explicitly needed:

```bash
python scripts/suno_song.py v1-generate --title "Legacy" --tags "edm" --prompt "cat dance"
python scripts/suno_song.py v1-feed <clip_id_1> <clip_id_2>
```

## Parameters

- Default model: `chirp-fenix` (Suno v5.5).
- Use `--mv` to select another model such as `chirp-crow`, `chirp-bluejay`, `chirp-auk`, `chirp-v4`, or `chirp-v4-tau`.
- Use `--style-weight`, `--weirdness`, `--audio-weight`, and `--vocal-gender f|m` for advanced generation parameters.
- Use `--upload-prefix /suno` by default; retry with `--upload-prefix /sunoi` only if the deployment follows the OpenAPI typo.
- Use `--payload-json <file-or-json>` for rare fields not exposed by named flags.

## Resources

- `scripts/suno_song.py` is the source of truth for request construction, dry-runs, polling, uploads, downloads, and v1 compatibility commands.
- `references/suno-api.md` summarizes the Apifox Suno documentation, endpoint matrix, mode-specific fields, model versions, and known inconsistencies.
