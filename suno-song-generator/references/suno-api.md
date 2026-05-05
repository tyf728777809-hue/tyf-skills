# Suno API Reference

This reference summarizes GPT Best Apifox Suno text-to-song documentation for `scripts/suno_song.py`.

## Contents

- Sources and base URLs
- Authentication
- Model versions
- v2 endpoint matrix
- Song generation modes
- Upload flow
- Persona, cover, replace, concat
- Lyrics, tags, stems, timing, exports
- v1 compatibility
- Advanced parameters
- Response handling notes

## Sources and Base URLs

Primary docs:

- https://gpt-best.apifox.cn/doc-4344094
- https://gpt-best.apifox.cn/doc-5633215
- https://gpt-best.apifox.cn/doc-6643749
- https://gpt-best.apifox.cn/doc-6643851
- https://gpt-best.apifox.cn/doc-6643852
- https://gpt-best.apifox.cn/doc-6643853
- https://gpt-best.apifox.cn/doc-7457984
- https://gpt-best.apifox.cn/doc-7457986
- https://gpt-best.apifox.cn/doc-7491115
- https://gpt-best.apifox.cn/api-290935144
- https://gpt-best.apifox.cn/api-294776598

Use the user's real API base URL from `SUNO_API_BASE_URL` or `GPT_BEST_API_BASE_URL`. The documentation uses placeholders such as `{{BASE_URL}}`.

Compatibility prefixes in docs:

- Current Suno API style: `{{BaseURL}}/suno`
- GoAmz style: `{{BaseURL}}/suno/v1`
- GoAmz v3.5 style: `{{BaseURL}}/suno/v1/mv-3.5`

## Authentication

Send:

```http
Authorization: Bearer <api-key>
Content-Type: application/json
Accept: application/json
```

Never store API keys in skill files. Use `SUNO_API_KEY` or `GPT_BEST_API_KEY`.

## Model Versions

The submit payload `mv` selects the Suno model.

| Version | mv | Prompt limit | Tag limit | Max duration |
| --- | --- | ---: | ---: | --- |
| v5.5 | `chirp-fenix` | 5000 | 1000 | 8 min |
| v5 | `chirp-crow` | 5000 | 1000 | 8 min |
| v4.5+ | `chirp-bluejay` | 5000 | 1000 | 8 min |
| v4.5-all | `chirp-auk-turbo` | 5000 | 1000 | 4 min |
| v4.5 | `chirp-auk` | 5000 | 1000 | 4 min |
| v4 | `chirp-v4` | 3000 | 200 | 150 sec |
| v3.5 | `chirp-v3-5` | 3000 | 200 | offline in docs |
| v3.0 | `chirp-v3.0` | 3000 | 200 | offline in docs |

Special model notes:

- Cover and Persona examples use `chirp-v3-5-tau` or `chirp-v4-tau`; docs also mention `chirp-auk` and `chirp-bluejay` for cover/replace.
- Stems docs require `chirp-auk`.
- Older upload-extension examples mention `chirp-v3-5-upload` or `chirp-v4-upload`, but docs mark that route as deprecated.

GoAmz `mv` values:

| Version | GoAmz mv |
| --- | --- |
| v3.0 | `mv-v3.0` |
| v3.5 | `mv-v3.5` |
| v4.0 | `mv-v4` |
| v4.5 | `mv-auk` |
| v4.5+ | `mv-bluejay` |
| v5 | `mv-crow` |
| v5.5 | `chirp-fenix` |

## v2 Endpoint Matrix

| Task | Method | Path |
| --- | --- | --- |
| Submit music | POST | `/suno/submit/music` |
| Fetch task | GET | `/suno/fetch/{task_id}` |
| Fetch tasks | POST | `/suno/fetch` |
| Submit lyrics | POST | `/suno/submit/lyrics` |
| Fetch lyrics | GET | `/suno/fetch/{task_id}` |
| Expand style tags | POST | `/suno/act/tags` |
| Upload request | POST | `/suno/uploads/audio` |
| Upload by URL | POST | `/suno/uploads/audio-url` |
| Upload finished | POST | `/suno/uploads/audio/{id}/upload-finish` |
| Upload status | GET | `/suno/uploads/audio/{id}` |
| Initialize uploaded clip | POST | `/suno/uploads/audio/{id}/initialize-clip` |
| Create Persona | POST | `/suno/persona/create/` |
| Concat full song | POST | `/suno/submit/concat` |
| Timing | GET | `/suno/act/timing/{clip_id}` |
| WAV | GET | `/suno/act/wav/{clip_id}` |
| MP4 | GET | `/suno/act/mp4/{clip_id}` |
| MIDI | GET | `/suno/act/midi/{clip_id}` |

Documentation inconsistency: upload OpenAPI pages show `/sunoi/uploads/audio`, while scenario docs and URL-upload docs show `/suno/uploads/audio`. Default to `/suno`; use `--upload-prefix /sunoi` only for deployments that require it.

## Song Generation Modes

All current modes submit to `/suno/submit/music`.

Custom mode:

```json
{
  "prompt": "lyrics or creation prompt",
  "generation_type": "TEXT",
  "tags": "electronic, pop",
  "negative_tags": "",
  "mv": "chirp-v4",
  "title": "Song title"
}
```

Inspiration mode:

```json
{
  "gpt_description_prompt": "乡愁",
  "mv": "chirp-v4"
}
```

Instrumental mode:

```json
{
  "prompt": "",
  "tags": "heavy metal",
  "mv": "chirp-v4",
  "title": "Instrumental title",
  "make_instrumental": true
}
```

Extend mode:

```json
{
  "task": "extend",
  "continue_clip_id": "source_clip_id",
  "continue_at": 30,
  "prompt": "next lyrics",
  "tags": "rock",
  "mv": "chirp-v4",
  "title": "Extended title"
}
```

Upload-extend mode:

```json
{
  "task": "upload_extend",
  "continue_clip_id": "uploaded_clip_id",
  "continue_at": 10,
  "prompt": "lyrics",
  "tags": "",
  "negative_tags": "",
  "mv": "chirp-v4",
  "title": "Title"
}
```

Cover mode:

```json
{
  "task": "cover",
  "cover_clip_id": "source_clip_id",
  "generation_type": "TEXT",
  "prompt": "lyrics",
  "tags": "rock, punk",
  "negative_tags": "",
  "mv": "chirp-v4-tau",
  "title": "Song (Cover)"
}
```

Replace/Infill mode:

```json
{
  "task": "infill",
  "continue_clip_id": "source_clip_id",
  "infill_start_s": 50,
  "infill_end_s": 64.8,
  "generation_type": "TEXT",
  "prompt": "replacement lyrics",
  "tags": "rock, punk",
  "negative_tags": "",
  "mv": "chirp-v3-5-tau",
  "title": "Song (replace)"
}
```

Persona generation mode:

```json
{
  "task": "artist_consistency",
  "persona_id": "persona_id",
  "artist_clip_id": "root_clip_id",
  "generation_type": "TEXT",
  "prompt": "lyrics",
  "tags": "electronic, pop",
  "negative_tags": "",
  "mv": "chirp-v4-tau",
  "title": "Song title"
}
```

Stems mode:

```json
{
  "task": "gen_stem",
  "generation_type": "TEXT",
  "title": "Song title",
  "mv": "chirp-auk",
  "prompt": "",
  "make_instrumental": true,
  "continue_clip_id": "source_clip_id",
  "continued_aligned_prompt": null,
  "continue_at": null,
  "stem_type_id": 91,
  "stem_type_group_name": "Two",
  "stem_task": "two"
}
```

## Upload Flow

Local file upload has six steps:

1. POST `/suno/uploads/audio` with `{ "extension": "mp3" }`.
2. POST multipart form data to the returned S3 `url`, including every returned `fields` value plus `file=@local_audio`.
3. POST `/suno/uploads/audio/{id}/upload-finish` with `{ "upload_type": "file_upload", "upload_filename": "name.mp3" }`.
4. GET `/suno/uploads/audio/{id}` until `status` is `complete`.
5. POST `/suno/uploads/audio/{id}/initialize-clip` with `{}`.
6. Use returned `clip_id` as `continue_clip_id` for upload-extend or cover.

URL upload:

```json
{
  "url": "https://example.com/song.mp3"
}
```

POST it to `/suno/uploads/audio-url`; docs describe a task ID response.

## Persona, Cover, Replace, Concat

Create Persona:

```json
{
  "root_clip_id": "clip_id",
  "name": "Persona title",
  "description": "Persona description",
  "clips": ["clip_id"],
  "is_public": true
}
```

Important Persona constraints from docs:

- `root_clip_id` must be a system clip, not uploader clip.
- Persona creation may not work cross-account.
- Persona generation uses `task=artist_consistency`, `persona_id`, and `artist_clip_id`.

Cover notes:

- `cover_clip_id` can be generated or uploaded audio.
- Generated clip cover can be cross-account according to docs; uploaded clip cover is not cross-account.

Replace/Infill notes:

- Replacement lyrics should overlap or align with the original lyrics and selected time range.
- After replace, call concat with `is_infill=true` to confirm a full song.

Concat:

```json
{
  "clip_id": "extended_or_infilled_clip_id",
  "is_infill": false
}
```

Use `is_infill=false` for normal extend and `true` for replace/infill.

## Lyrics, Tags, Stems, Timing, Exports

Lyrics:

- Submit: POST `/suno/submit/lyrics` with `{ "prompt": "dance", "notify_hook": "optional URL" }`.
- Fetch: GET `/suno/fetch/{task_id}`.

Tags:

- POST `/suno/act/tags` with `{ "original_tags": "student" }`.
- Response example includes `upsampled_tags` and `request_id`.

Stems:

- Use `task=gen_stem`, `stem_task=two`, `stem_type_group_name=Two`, `stem_type_id=91`.
- Result includes separate `Vocals` and `Instrumental` clips.

Timing:

- GET `/suno/act/timing/{clip_id}`.
- Response contains `aligned_words`, `waveform_data`, `hoot_cer`, and `is_streamed`.

Exports:

- GET `/suno/act/wav/{clip_id}` for WAV.
- GET `/suno/act/mp4/{clip_id}` for MP4 MV.
- GET `/suno/act/midi/{clip_id}` for MIDI.
- MIDI may return `{ "state": "running" }` before `{ "state": "complete", "instruments": [...] }`.

## v1 Compatibility

Use these only for old callers or GoAmz/SunoAPI-compatible workflows.

| Task | Method | Path |
| --- | --- | --- |
| Generate song | POST | `/suno/generate` |
| Query clips | GET | `/suno/feed/{clip_id_1},{clip_id_2}` |
| Concat | POST | `/suno/generate/concat` |
| Generate lyrics | POST | `/suno/generate/lyrics/` |
| Fetch lyrics | GET | `/suno/lyrics/{task_id}` |
| Stems | POST | `/suno/generate` with `task=gen_stem` |

Scenario docs sometimes describe old submit as POST `/suno/generate` and fetch as GET `/suno/feed/{clip_ids}`. Current v2 API pages describe POST `/suno/submit/music` and GET `/suno/fetch/{task_id}`.

## Advanced Parameters

Docs added advanced controls in 2025:

- `style_weight`: 0-1
- `weirdness_constraint`: 0-1
- `audio_weight`: 0-1, cover/remix only
- `vocal_gender`: `f` for female, `m` for male

Payload shape:

```json
{
  "metadata": {
    "create_mode": "custom",
    "control_sliders": {
      "style_weight": 0.4,
      "weirdness_constraint": 0.7
    },
    "can_control_sliders": ["weirdness_constraint", "style_weight"],
    "vocal_gender": "f"
  }
}
```

Cover/remix can include:

```json
{
  "metadata": {
    "create_mode": "custom",
    "control_sliders": {
      "style_weight": 0.68,
      "audio_weight": 0.48,
      "weirdness_constraint": 0.37
    },
    "can_control_sliders": ["weirdness_constraint", "style_weight", "audio_weight"],
    "is_remix": true
  }
}
```

## Response Handling Notes

The Apifox schema is incomplete for several submit/upload endpoints. Handle all raw JSON defensively:

- Task ID may appear as top-level `id`, top-level `task_id`, string `data`, or `data.task_id`.
- Clip IDs may appear in `clips[].id`, `data[].id`, `data.data[].id`, or v1 feed arrays.
- Task status commonly appears as `status`; failed states may include `fail_reason`, `error_message`, or nested metadata errors.
- Save the raw response for troubleshooting and extract task/clip IDs opportunistically.
