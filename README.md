# tyf-skills

Personal collection of Codex Skills that I find useful and worth keeping.

## Skills

- `seedance-director`: Seedance 2.0 video prompt director. Converts plain-text scene descriptions and optional reference images into strict bilingual EN+ZH JSON prompts optimized for Seedance 2.0.
- `prompt-expert`: Chinese image prompt expert. Writes, improves, and reverse-engineers reusable AI image prompts from goals, subject references, or style references.
- `suno-song-generator`: Suno API song generator. Creates and manages songs, lyrics, instrumentals, covers, extensions, stems, timing data, and exported assets through GPT Best / Suno-compatible endpoints.
- `yy16-h72-map-offset`: 燕云十六声 H72 map offset maintenance workflow. Reads Win64r/Win64rh game package metadata, scans offsets, auto-discovers `curVersion`, generates backend-ready H72_MAP JSON, and records reports/samples.

## Install

Copy the skill folder you want to use into your local Codex skills directory:

```bash
cp -R suno-song-generator ~/.codex/skills/
```

Restart Codex or open a new session if the skill does not appear immediately.

## Usage

```text
Use $seedance-director to turn this scene into a strict bilingual Seedance 2.0 video prompt.
Use $suno-song-generator to create a Chinese pop song from these lyrics.
Use $yy16-h72-map-offset after 燕云十六声 updates to generate the DD backend H72_MAP JSON.
```

## Rights Notice

No open-source license is granted for this repository.

This repository is public so others may view and personally download the materials for learning and reference. Unless I give explicit written permission, you may not modify, redistribute, sublicense, sell, use commercially, or create derivative versions of the contents.

All rights reserved.
