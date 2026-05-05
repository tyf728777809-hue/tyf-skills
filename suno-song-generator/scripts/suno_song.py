#!/usr/bin/env python3
"""CLI for GPT Best / Suno text-to-song workflows."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import http.client
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_MV = "chirp-fenix"
DEFAULT_TIMEOUT = 600.0
DEFAULT_POLL_INTERVAL = 10.0
COMPLETE_STATUSES = {"complete", "completed", "success", "succeeded", "done"}
FAILED_STATUSES = {"failed", "failure", "error", "rejected", "cancelled", "canceled"}
SENSITIVE_KEYS = {
    "authorization",
    "api-key",
    "api_key",
    "apikey",
    "token",
    "access_token",
    "signature",
    "policy",
    "awsaccesskeyid",
    "aws_access_key_id",
    "secret",
    "password",
    "cookie",
}


class ApiError(RuntimeError):
    def __init__(self, status: int, body: str) -> None:
        self.status = status
        self.body = body
        super().__init__(f"API request failed with status {status}: {body}")


def load_dotenv(explicit_path: str | None = None) -> None:
    paths: list[Path] = []
    if explicit_path:
        paths.append(Path(explicit_path).expanduser())
    else:
        script_dir = Path(__file__).resolve().parent
        paths.extend(
            [
                Path.cwd() / ".env",
                Path.home() / ".config" / "suno-song-generator" / ".env",
                script_dir.parent / ".env",
            ]
        )

    for path in paths:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            name, value = stripped.split("=", 1)
            name = name.strip()
            value = value.strip().strip("'\"")
            if name and name not in os.environ:
                os.environ[name] = value


def first_env(names: list[str]) -> tuple[str | None, str | None]:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value, name
    return None, None


def api_base_url(args: argparse.Namespace) -> str:
    value, _ = first_env(["SUNO_API_BASE_URL", "GPT_BEST_API_BASE_URL"])
    if value:
        return value.rstrip("/")
    if getattr(args, "dry_run", False):
        return "https://{BASE_URL}"
    raise SystemExit("Missing API base URL. Set SUNO_API_BASE_URL or GPT_BEST_API_BASE_URL.")


def api_key(args: argparse.Namespace) -> str:
    value, _ = first_env(["SUNO_API_KEY", "GPT_BEST_API_KEY"])
    if value:
        return value
    if getattr(args, "dry_run", False):
        return "dry-run-key"
    raise SystemExit("Missing API key. Set SUNO_API_KEY or GPT_BEST_API_KEY.")


def endpoint(args: argparse.Namespace, path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    clean_path = path if path.startswith("/") else f"/{path}"
    return f"{api_base_url(args)}{clean_path}"


def sanitize_for_output(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, item in value.items():
            if key.lower() in SENSITIVE_KEYS:
                cleaned[key] = "***REDACTED***"
            else:
                cleaned[key] = sanitize_for_output(item)
        return cleaned
    if isinstance(value, list):
        return [sanitize_for_output(item) for item in value]
    if isinstance(value, str) and value.lower().startswith("bearer "):
        return "Bearer ***REDACTED***"
    return value


def emit_json(value: Any) -> None:
    print(json.dumps(sanitize_for_output(value), ensure_ascii=False, indent=2))


def parse_json_text_or_file(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    candidate = Path(raw).expanduser()
    if candidate.is_file():
        text = candidate.read_text(encoding="utf-8")
    else:
        text = raw
    data = json.loads(text)
    if not isinstance(data, dict):
        raise SystemExit("--payload-json must be a JSON object or a file containing one")
    return data


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def read_prompt(args: argparse.Namespace) -> str:
    prompt_file = getattr(args, "prompt_file", None)
    if prompt_file:
        return Path(prompt_file).expanduser().read_text(encoding="utf-8")
    value = getattr(args, "prompt", None)
    return "" if value is None else value


def require_text(value: str | None, name: str) -> str:
    if value is None or value == "":
        raise SystemExit(f"{name} is required")
    return value


def require_number(value: float | None, name: str) -> float:
    if value is None:
        raise SystemExit(f"{name} is required")
    return value


def parse_bool(raw: str | bool) -> bool:
    if isinstance(raw, bool):
        return raw
    lowered = raw.strip().lower()
    if lowered in {"1", "true", "yes", "y", "on"}:
        return True
    if lowered in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError("expected true or false")


def request_api(
    args: argparse.Namespace,
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    *,
    auth: bool = True,
    binary_name: str | None = None,
) -> Any:
    url = endpoint(args, path)
    headers = {"Accept": "application/json"}
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    if auth:
        headers["Authorization"] = f"Bearer {api_key(args)}"

    if args.dry_run:
        return {
            "dry_run": True,
            "method": method,
            "url": url,
            "headers": headers,
            "json": payload,
        }

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    return read_response(args, req, binary_name=binary_name)


def read_response(args: argparse.Namespace, req: urllib.request.Request, *, binary_name: str | None = None) -> Any:
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            raw = response.read()
            status = response.status
            content_type = response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ApiError(exc.code, body) from exc
    except http.client.RemoteDisconnected as exc:
        raise SystemExit("Network error: remote server closed the connection without a response") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Network error: {exc}") from exc

    if not raw:
        return {"status": status}

    if "json" in content_type.lower():
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"API returned invalid JSON: {raw[:1000]!r}") from exc

    if binary_name and args.output_dir:
        output_dir = ensure_output_dir(args)
        suffix = extension_from_content_type(content_type) or Path(binary_name).suffix or ".bin"
        output_path = unique_path(output_dir / f"{Path(binary_name).stem}{suffix}")
        output_path.write_bytes(raw)
        return {
            "status": status,
            "content_type": content_type,
            "bytes": len(raw),
            "saved_file": str(output_path),
        }

    preview = raw[:300].decode("utf-8", errors="replace")
    return {"status": status, "content_type": content_type, "bytes": len(raw), "preview": preview}


def friendly_api_error(exc: ApiError) -> str:
    try:
        body = json.dumps(json.loads(exc.body), ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        body = exc.body
    hints = {
        400: "Bad request. Check required fields, model version, and mode-specific task values.",
        401: "Unauthorized. Check the API key environment variable.",
        403: "Forbidden. The key may lack permission for this endpoint or account-bound clip.",
        404: "Not found. Check the base URL and endpoint family.",
        413: "Payload too large. Check upload size and prompt limits.",
        429: "Rate limited. Retry later or increase polling interval.",
        500: "Server or upstream Suno error.",
        503: "No upstream channel is available.",
    }
    return f"API error {exc.status}: {hints.get(exc.status, 'Unexpected API error.')}\n{body}"


def ensure_output_dir(args: argparse.Namespace) -> Path:
    output_dir = Path(args.output_dir or "suno-output").expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    for index in range(1, 10000):
        candidate = parent / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
    raise SystemExit(f"Could not find available filename for {path}")


def save_json_result(args: argparse.Namespace, command: str, data: Any) -> str | None:
    if not args.output_dir or args.dry_run:
        return None
    output_dir = ensure_output_dir(args)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = unique_path(output_dir / f"{stamp}-{command}.json")
    path.write_text(json.dumps(sanitize_for_output(data), ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def output_result(args: argparse.Namespace, command: str, data: Any) -> None:
    saved = save_json_result(args, command, data)
    downloads: list[str] = []
    if args.download and not args.dry_run:
        downloads = download_result_assets(args, data)
    if saved or downloads:
        if isinstance(data, dict):
            data = dict(data)
            if saved:
                data["saved_json"] = saved
            if downloads:
                data["downloaded_files"] = downloads
        else:
            data = {"result": data, "saved_json": saved, "downloaded_files": downloads}
    emit_json(data)


def extension_from_content_type(content_type: str) -> str | None:
    lowered = content_type.lower()
    if "audio/wav" in lowered or "audio/x-wav" in lowered:
        return ".wav"
    if "audio/mpeg" in lowered:
        return ".mp3"
    if "video/mp4" in lowered:
        return ".mp4"
    if "image/png" in lowered:
        return ".png"
    if "image/jpeg" in lowered:
        return ".jpg"
    return None


def download_result_assets(args: argparse.Namespace, data: Any) -> list[str]:
    urls = collect_asset_urls(data)
    downloaded: list[str] = []
    output_dir = ensure_output_dir(args)
    for clip_id, key, url in urls:
        try:
            suffix = Path(urllib.parse.urlparse(url).path).suffix or ".bin"
            safe_key = key.replace("_url", "").replace("image_large", "image-large")
            base_name = f"{clip_id or 'asset'}-{safe_key}{suffix}"
            output_path = unique_path(output_dir / base_name)
            urllib.request.urlretrieve(url, output_path)
            downloaded.append(str(output_path))
        except Exception as exc:  # noqa: BLE001 - downloads should not hide API results
            downloaded.append(f"FAILED {url}: {exc}")
    return downloaded


def collect_asset_urls(data: Any) -> list[tuple[str | None, str, str]]:
    found: list[tuple[str | None, str, str]] = []

    def walk(value: Any, current_id: str | None = None) -> None:
        if isinstance(value, dict):
            next_id = value.get("id") if isinstance(value.get("id"), str) else current_id
            for key, item in value.items():
                if key.endswith("_url") and isinstance(item, str) and item.startswith(("http://", "https://")):
                    found.append((next_id, key, item))
                else:
                    walk(item, next_id)
        elif isinstance(value, list):
            for item in value:
                walk(item, current_id)

    walk(data)
    return found


def build_advanced_metadata(args: argparse.Namespace, mode: str) -> dict[str, Any]:
    sliders: dict[str, float] = {}
    for attr, payload_key in [
        ("style_weight", "style_weight"),
        ("weirdness_constraint", "weirdness_constraint"),
        ("audio_weight", "audio_weight"),
    ]:
        value = getattr(args, attr, None)
        if value is None:
            continue
        if value < 0 or value > 1:
            raise SystemExit(f"--{attr.replace('_', '-')} must be between 0 and 1")
        if payload_key == "audio_weight" and mode != "cover":
            raise SystemExit("--audio-weight is only valid for cover/remix requests")
        sliders[payload_key] = value

    metadata: dict[str, Any] = {}
    if sliders:
        metadata["create_mode"] = "custom"
        metadata["control_sliders"] = sliders
        metadata["can_control_sliders"] = list(sliders.keys())
    if getattr(args, "vocal_gender", None):
        metadata["vocal_gender"] = args.vocal_gender
    if getattr(args, "is_remix", False):
        metadata["is_remix"] = True
        metadata.setdefault("create_mode", "custom")
    return metadata


def mode_default_mv(mode: str) -> str:
    if mode in {"cover", "persona"}:
        return "chirp-v4-tau"
    if mode == "replace":
        return "chirp-v3-5-tau"
    if mode == "stems":
        return "chirp-auk"
    return DEFAULT_MV


def add_if_present(payload: dict[str, Any], key: str, value: Any) -> None:
    if value is not None:
        payload[key] = value


def build_submit_payload(args: argparse.Namespace, *, mode: str | None = None) -> dict[str, Any]:
    mode = mode or args.mode
    prompt = read_prompt(args)
    mv = args.mv or mode_default_mv(mode)
    payload: dict[str, Any] = {}

    if mode == "custom":
        payload.update(
            {
                "prompt": require_text(prompt, "--prompt or --prompt-file"),
                "generation_type": args.generation_type,
                "tags": require_text(args.tags, "--tags"),
                "negative_tags": args.negative_tags,
                "mv": mv,
                "title": require_text(args.title, "--title"),
            }
        )
    elif mode == "inspiration":
        description = args.description or prompt
        payload.update({"gpt_description_prompt": require_text(description, "--description or --prompt"), "mv": mv})
        add_if_present(payload, "title", args.title)
        add_if_present(payload, "tags", args.tags)
        if args.make_instrumental:
            payload["make_instrumental"] = True
            payload.setdefault("prompt", "")
    elif mode == "instrumental":
        payload.update(
            {
                "prompt": prompt,
                "tags": require_text(args.tags, "--tags"),
                "mv": mv,
                "title": require_text(args.title, "--title"),
                "make_instrumental": True,
            }
        )
    elif mode == "extend":
        payload.update(
            {
                "task": args.task or "extend",
                "continue_clip_id": require_text(args.continue_clip_id, "--continue-clip-id"),
                "continue_at": require_number(args.continue_at, "--continue-at"),
                "prompt": require_text(prompt, "--prompt or --prompt-file"),
                "tags": require_text(args.tags, "--tags"),
                "negative_tags": args.negative_tags,
                "mv": mv,
                "title": require_text(args.title, "--title"),
            }
        )
    elif mode == "upload-extend":
        payload.update(
            {
                "task": args.task or "upload_extend",
                "continue_clip_id": require_text(args.continue_clip_id, "--continue-clip-id"),
                "continue_at": require_number(args.continue_at, "--continue-at"),
                "prompt": prompt,
                "tags": args.tags or "",
                "negative_tags": args.negative_tags,
                "mv": mv,
                "title": require_text(args.title, "--title"),
            }
        )
    elif mode == "cover":
        payload.update(
            {
                "task": args.task or "cover",
                "cover_clip_id": require_text(args.cover_clip_id, "--cover-clip-id"),
                "generation_type": args.generation_type,
                "prompt": require_text(prompt, "--prompt or --prompt-file"),
                "tags": args.tags or "",
                "negative_tags": args.negative_tags,
                "mv": mv,
                "title": require_text(args.title, "--title"),
            }
        )
    elif mode == "replace":
        payload.update(
            {
                "task": args.task or "infill",
                "continue_clip_id": require_text(args.continue_clip_id, "--continue-clip-id"),
                "continue_at": args.continue_at,
                "continued_aligned_prompt": args.continued_aligned_prompt,
                "infill_start_s": require_number(args.infill_start_s, "--infill-start-s"),
                "infill_end_s": require_number(args.infill_end_s, "--infill-end-s"),
                "generation_type": args.generation_type,
                "prompt": require_text(prompt, "--prompt or --prompt-file"),
                "tags": args.tags or "",
                "negative_tags": args.negative_tags,
                "mv": mv,
                "title": require_text(args.title, "--title"),
            }
        )
    elif mode == "persona":
        payload.update(
            {
                "task": args.task or "artist_consistency",
                "persona_id": require_text(args.persona_id, "--persona-id"),
                "artist_clip_id": require_text(args.artist_clip_id, "--artist-clip-id"),
                "generation_type": args.generation_type,
                "prompt": require_text(prompt, "--prompt or --prompt-file"),
                "tags": args.tags or "",
                "negative_tags": args.negative_tags,
                "mv": mv,
                "title": require_text(args.title, "--title"),
            }
        )
    elif mode == "stems":
        payload.update(
            {
                "task": args.task or "gen_stem",
                "generation_type": args.generation_type,
                "title": require_text(args.title, "--title"),
                "mv": mv,
                "prompt": prompt,
                "make_instrumental": True,
                "continue_clip_id": require_text(args.continue_clip_id, "--continue-clip-id"),
                "continued_aligned_prompt": None,
                "continue_at": None,
                "stem_type_id": args.stem_type_id,
                "stem_type_group_name": args.stem_type_group_name,
                "stem_task": args.stem_task,
            }
        )
    else:
        raise SystemExit(f"Unsupported mode: {mode}")

    metadata = build_advanced_metadata(args, mode)
    if metadata:
        payload["metadata"] = metadata
    payload = deep_merge(payload, parse_json_text_or_file(args.payload_json))
    return payload


def extract_task_id(data: Any) -> str | None:
    if isinstance(data, dict):
        raw_data = data.get("data")
        if isinstance(raw_data, str):
            return raw_data
        for key in ("task_id", "id"):
            value = data.get(key)
            if isinstance(value, str):
                return value
        if isinstance(raw_data, dict):
            for key in ("task_id", "id"):
                value = raw_data.get(key)
                if isinstance(value, str):
                    return value
    return None


def extract_status(data: Any) -> tuple[str | None, str | None]:
    if not isinstance(data, dict):
        return None, None
    candidates: list[dict[str, Any]] = [data]
    if isinstance(data.get("data"), dict):
        candidates.insert(0, data["data"])
    for item in candidates:
        status = item.get("status")
        if isinstance(status, str):
            reason = item.get("fail_reason") or item.get("error_message") or item.get("message")
            return status, str(reason) if reason is not None else None
    return None, None


def poll_task(args: argparse.Namespace, task_id: str, *, family: str | None = None, lyrics: bool = False) -> Any:
    family = family or args.api_family
    deadline = time.monotonic() + args.timeout
    last: Any = None
    while True:
        if family == "v1" and lyrics:
            path = f"/suno/lyrics/{urllib.parse.quote(task_id)}"
        elif family == "v1":
            path = f"/suno/feed/{urllib.parse.quote(task_id)}"
        else:
            path = f"/suno/fetch/{urllib.parse.quote(task_id)}"
        last = request_api(args, "GET", path)
        status, reason = extract_status(last)
        if status and status.lower() in COMPLETE_STATUSES:
            return last
        if status and status.lower() in FAILED_STATUSES:
            return {"status": status, "fail_reason": reason, "response": last}
        if time.monotonic() >= deadline:
            return {"status": "timeout", "last_response": last}
        time.sleep(args.poll_interval)


def submit_and_maybe_wait(args: argparse.Namespace, path: str, payload: dict[str, Any], command: str, *, family: str | None = None, lyrics: bool = False) -> None:
    submit = request_api(args, "POST", path, payload)
    if args.wait and not args.dry_run:
        task_id = extract_task_id(submit)
        if task_id:
            result = poll_task(args, task_id, family=family, lyrics=lyrics)
            output_result(args, command, {"submit": submit, "fetch": result})
            return
        output_result(args, command, {"submit": submit, "warning": "No task_id found for polling"})
        return
    output_result(args, command, submit)


def cmd_check(args: argparse.Namespace) -> None:
    base, base_name = first_env(["SUNO_API_BASE_URL", "GPT_BEST_API_BASE_URL"])
    key, key_name = first_env(["SUNO_API_KEY", "GPT_BEST_API_KEY"])
    emit_json(
        {
            "ready": bool(base and key),
            "base_url": base,
            "base_url_env": base_name,
            "credential_status": "configured" if key else "missing",
            "credential_env": key_name,
            "skill_dir": str(Path(__file__).resolve().parent.parent),
        }
    )


def cmd_submit_music(args: argparse.Namespace) -> None:
    payload = build_submit_payload(args)
    path = "/suno/generate" if args.api_family == "v1" else "/suno/submit/music"
    submit_and_maybe_wait(args, path, payload, "submit-music", family=args.api_family)


def cmd_fetch(args: argparse.Namespace) -> None:
    if args.api_family == "v1":
        path = "/suno/feed/" + ",".join(urllib.parse.quote(item) for item in args.identifiers)
    else:
        if len(args.identifiers) != 1:
            raise SystemExit("v2 fetch accepts one task_id. Use fetch-batch for multiple task IDs.")
        path = f"/suno/fetch/{urllib.parse.quote(args.identifiers[0])}"
    output_result(args, "fetch", request_api(args, "GET", path))


def cmd_fetch_batch(args: argparse.Namespace) -> None:
    payload: dict[str, Any] = {"ids": args.ids}
    if args.action:
        payload["action"] = args.action
    output_result(args, "fetch-batch", request_api(args, "POST", "/suno/fetch", payload))


def cmd_lyrics_submit(args: argparse.Namespace) -> None:
    prompt = read_prompt(args)
    payload: dict[str, Any] = {"prompt": require_text(prompt, "--prompt or --prompt-file")}
    add_if_present(payload, "notify_hook", args.notify_hook)
    family = args.api_family
    path = "/suno/generate/lyrics/" if family == "v1" else "/suno/submit/lyrics"
    submit_and_maybe_wait(args, path, payload, "lyrics-submit", family=family, lyrics=True)


def cmd_lyrics_fetch(args: argparse.Namespace) -> None:
    path = f"/suno/lyrics/{urllib.parse.quote(args.task_id)}" if args.api_family == "v1" else f"/suno/fetch/{urllib.parse.quote(args.task_id)}"
    output_result(args, "lyrics-fetch", request_api(args, "GET", path))


def cmd_tags(args: argparse.Namespace) -> None:
    payload = {"original_tags": args.original_tags}
    output_result(args, "tags", request_api(args, "POST", "/suno/act/tags", payload))


def normalize_upload_prefix(prefix: str) -> str:
    clean = prefix.rstrip("/")
    if clean not in {"/suno", "/sunoi"}:
        raise SystemExit("--upload-prefix must be /suno or /sunoi")
    return clean


def build_multipart_body(boundary: str, fields: dict[str, Any], file_path: Path) -> bytes:
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                str(value).encode(),
                b"\r\n",
            ]
        )
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    chunks.extend(
        [
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'.encode(),
            f"Content-Type: {content_type}\r\n\r\n".encode(),
            file_path.read_bytes(),
            b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )
    return b"".join(chunks)


def request_s3_upload(args: argparse.Namespace, url: str, fields: dict[str, Any], file_path: Path) -> Any:
    if args.dry_run:
        return {
            "dry_run": True,
            "method": "POST",
            "url": url,
            "multipart_fields": list(fields.keys()),
            "file": str(file_path),
        }
    boundary = f"----suno-upload-{os.urandom(12).hex()}"
    body = build_multipart_body(boundary, fields, file_path)
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    return read_response(args, req)


def unwrap_data_object(data: Any) -> dict[str, Any]:
    if isinstance(data, dict) and isinstance(data.get("data"), dict):
        return data["data"]
    if isinstance(data, dict):
        return data
    return {}


def poll_upload(args: argparse.Namespace, upload_prefix: str, upload_id: str) -> Any:
    deadline = time.monotonic() + args.timeout
    last: Any = None
    while True:
        last = request_api(args, "GET", f"{upload_prefix}/uploads/audio/{urllib.parse.quote(upload_id)}")
        status, reason = extract_status(last)
        if status and status.lower() in COMPLETE_STATUSES:
            return last
        if status and status.lower() in FAILED_STATUSES:
            return {"status": status, "fail_reason": reason, "response": last}
        if time.monotonic() >= deadline:
            return {"status": "timeout", "last_response": last}
        time.sleep(args.poll_interval)


def cmd_upload_file(args: argparse.Namespace) -> None:
    file_path = Path(args.file).expanduser()
    if not file_path.is_file():
        raise SystemExit(f"Audio file not found: {file_path}")
    upload_prefix = normalize_upload_prefix(args.upload_prefix)
    extension = (args.extension or file_path.suffix.lstrip(".")).lower()
    if not extension:
        raise SystemExit("Could not infer extension; pass --extension mp3")

    if args.dry_run:
        output_result(
            args,
            "upload-file",
            {
                "dry_run": True,
                "steps": [
                    {"method": "POST", "path": f"{upload_prefix}/uploads/audio", "json": {"extension": extension}},
                    {"method": "POST", "url": "returned S3 url", "multipart": "returned fields plus file"},
                    {"method": "POST", "path": f"{upload_prefix}/uploads/audio/<id>/upload-finish"},
                    {"method": "GET", "path": f"{upload_prefix}/uploads/audio/<id>", "when": "--wait"},
                    {"method": "POST", "path": f"{upload_prefix}/uploads/audio/<id>/initialize-clip", "when": "--wait"},
                ],
                "file": str(file_path),
            },
        )
        return

    upload_request = request_api(args, "POST", f"{upload_prefix}/uploads/audio", {"extension": extension})
    upload_info = unwrap_data_object(upload_request)
    upload_id = upload_info.get("id")
    upload_url = upload_info.get("url")
    fields = upload_info.get("fields")
    if not isinstance(upload_id, str) or not isinstance(upload_url, str) or not isinstance(fields, dict):
        raise SystemExit("Upload request response did not contain id, url, and fields")

    s3_upload = request_s3_upload(args, upload_url, fields, file_path)
    finish_payload = {
        "upload_type": args.upload_type,
        "upload_filename": args.upload_filename or file_path.name,
    }
    upload_finish = request_api(args, "POST", f"{upload_prefix}/uploads/audio/{urllib.parse.quote(upload_id)}/upload-finish", finish_payload)
    result: dict[str, Any] = {
        "upload_id": upload_id,
        "upload_request": upload_request,
        "s3_upload": s3_upload,
        "upload_finish": upload_finish,
    }
    if args.wait:
        result["upload_status"] = poll_upload(args, upload_prefix, upload_id)
        result["initialize_clip"] = request_api(args, "POST", f"{upload_prefix}/uploads/audio/{urllib.parse.quote(upload_id)}/initialize-clip", {})
    output_result(args, "upload-file", result)


def cmd_upload_url(args: argparse.Namespace) -> None:
    response = request_api(args, "POST", "/suno/uploads/audio-url", {"url": args.url})
    if args.wait and not args.dry_run:
        task_id = extract_task_id(response)
        if task_id:
            output_result(args, "upload-url", {"submit": response, "fetch": poll_task(args, task_id)})
            return
    output_result(args, "upload-url", response)


def cmd_upload_status(args: argparse.Namespace) -> None:
    prefix = normalize_upload_prefix(args.upload_prefix)
    output_result(args, "upload-status", request_api(args, "GET", f"{prefix}/uploads/audio/{urllib.parse.quote(args.upload_id)}"))


def cmd_upload_init(args: argparse.Namespace) -> None:
    prefix = normalize_upload_prefix(args.upload_prefix)
    output_result(args, "upload-init", request_api(args, "POST", f"{prefix}/uploads/audio/{urllib.parse.quote(args.upload_id)}/initialize-clip", {}))


def cmd_persona_create(args: argparse.Namespace) -> None:
    clips = args.clips or [args.root_clip_id]
    payload = {
        "root_clip_id": args.root_clip_id,
        "name": args.name,
        "description": args.description,
        "clips": clips,
        "is_public": args.is_public,
    }
    output_result(args, "persona-create", request_api(args, "POST", "/suno/persona/create/", payload))


def cmd_concat(args: argparse.Namespace) -> None:
    path = "/suno/generate/concat" if args.api_family == "v1" else "/suno/submit/concat"
    payload = {"clip_id": args.clip_id, "is_infill": args.is_infill}
    submit_and_maybe_wait(args, path, payload, "concat", family=args.api_family)


def cmd_act(args: argparse.Namespace) -> None:
    paths = {
        "timing": f"/suno/act/timing/{urllib.parse.quote(args.clip_id)}",
        "wav": f"/suno/act/wav/{urllib.parse.quote(args.clip_id)}",
        "mp4": f"/suno/act/mp4/{urllib.parse.quote(args.clip_id)}",
        "midi": f"/suno/act/midi/{urllib.parse.quote(args.clip_id)}",
    }
    output_result(args, args.command, request_api(args, "GET", paths[args.command], binary_name=f"{args.clip_id}-{args.command}"))


def cmd_v1_generate(args: argparse.Namespace) -> None:
    payload = build_submit_payload(args, mode=args.mode)
    submit_and_maybe_wait(args, "/suno/generate", payload, "v1-generate", family="v1")


def cmd_v1_feed(args: argparse.Namespace) -> None:
    path = "/suno/feed/" + ",".join(urllib.parse.quote(item) for item in args.clip_ids)
    output_result(args, "v1-feed", request_api(args, "GET", path))


def cmd_v1_lyrics_submit(args: argparse.Namespace) -> None:
    prompt = read_prompt(args)
    payload = {"prompt": require_text(prompt, "--prompt or --prompt-file")}
    submit_and_maybe_wait(args, "/suno/generate/lyrics/", payload, "v1-lyrics-submit", family="v1", lyrics=True)


def cmd_v1_lyrics_fetch(args: argparse.Namespace) -> None:
    output_result(args, "v1-lyrics-fetch", request_api(args, "GET", f"/suno/lyrics/{urllib.parse.quote(args.task_id)}"))


def cmd_v1_concat(args: argparse.Namespace) -> None:
    payload = {"clip_id": args.clip_id, "is_infill": args.is_infill}
    submit_and_maybe_wait(args, "/suno/generate/concat", payload, "v1-concat", family="v1")


def cmd_v1_stems(args: argparse.Namespace) -> None:
    payload = build_submit_payload(args, mode="stems")
    submit_and_maybe_wait(args, "/suno/generate", payload, "v1-stems", family="v1")


def add_prompt_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--prompt", help="Prompt or lyrics text")
    parser.add_argument("--prompt-file", help="UTF-8 text file containing prompt or lyrics")


def add_submit_args(parser: argparse.ArgumentParser, *, include_mode: bool = True) -> None:
    if include_mode:
        parser.add_argument(
            "--mode",
            choices=["custom", "inspiration", "instrumental", "extend", "upload-extend", "cover", "replace", "persona", "stems"],
            default="custom",
            help="Suno generation mode",
        )
    else:
        parser.add_argument(
            "--mode",
            choices=["custom", "inspiration", "instrumental", "extend", "upload-extend", "cover", "replace", "persona", "stems"],
            default="custom",
            help=argparse.SUPPRESS,
        )
    add_prompt_args(parser)
    parser.add_argument("--description", help="Inspiration-mode description prompt")
    parser.add_argument("--title", help="Song title")
    parser.add_argument("--tags", default="", help="Comma-separated style tags")
    parser.add_argument("--negative-tags", default="", help="Styles to avoid")
    parser.add_argument("--mv", help=f"Suno model version, defaults to {DEFAULT_MV} except mode-specific cases")
    parser.add_argument("--generation-type", default="TEXT", help="Generation type, usually TEXT")
    parser.add_argument("--make-instrumental", action="store_true", help="Set make_instrumental=true")
    parser.add_argument("--continue-at", type=float, help="Continue from this second")
    parser.add_argument("--continue-clip-id", help="Source clip ID for extend, upload-extend, replace, or stems")
    parser.add_argument("--task", help="Override task value")
    parser.add_argument("--cover-clip-id", help="Source clip ID for cover")
    parser.add_argument("--persona-id", help="Persona ID")
    parser.add_argument("--artist-clip-id", help="Root artist clip ID for Persona mode")
    parser.add_argument("--continued-aligned-prompt", help="Aligned prompt for continued creation")
    parser.add_argument("--infill-start-s", type=float, help="Replace/infill start second")
    parser.add_argument("--infill-end-s", type=float, help="Replace/infill end second")
    parser.add_argument("--stem-type-id", type=int, default=91)
    parser.add_argument("--stem-type-group-name", default="Two")
    parser.add_argument("--stem-task", default="two")
    parser.add_argument("--style-weight", type=float, help="Advanced style_weight from 0 to 1")
    parser.add_argument("--weirdness", dest="weirdness_constraint", type=float, help="Advanced weirdness_constraint from 0 to 1")
    parser.add_argument("--audio-weight", type=float, help="Advanced audio_weight from 0 to 1 for cover/remix")
    parser.add_argument("--vocal-gender", choices=["f", "m"], help="Vocal gender, f or m")
    parser.add_argument("--is-remix", action="store_true", help="Set metadata.is_remix=true")
    parser.add_argument("--payload-json", help="JSON object or JSON file to merge into the request body")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate and manage Suno songs through the GPT Best API.")
    parser.add_argument("--env-file", help="Load environment variables from this .env file")
    parser.add_argument("--dry-run", action="store_true", help="Print the request without sending it")
    parser.add_argument("--wait", action="store_true", help="Poll async task results when a task ID is returned")
    parser.add_argument("--poll-interval", type=float, default=DEFAULT_POLL_INTERVAL, help="Seconds between polling attempts")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="Maximum seconds to wait for polling")
    parser.add_argument("--output-dir", help="Directory for JSON responses and downloaded assets")
    parser.add_argument("--download", action="store_true", help="Download result audio/video/image URLs found in responses")
    parser.add_argument("--api-family", choices=["v2", "v1"], default="v2", help="Endpoint family for generic commands")

    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="Check local API configuration")
    check.set_defaults(func=cmd_check)

    submit = subparsers.add_parser("submit-music", help="Submit a Suno music generation task")
    add_submit_args(submit)
    submit.set_defaults(func=cmd_submit_music)

    fetch = subparsers.add_parser("fetch", help="Fetch a task by task ID, or v1 clips with --api-family v1")
    fetch.add_argument("identifiers", nargs="+")
    fetch.set_defaults(func=cmd_fetch)

    fetch_batch = subparsers.add_parser("fetch-batch", help="Batch fetch v2 tasks")
    fetch_batch.add_argument("ids", nargs="+")
    fetch_batch.add_argument("--action", choices=["MUSIC", "LYRICS"], help="Optional action filter")
    fetch_batch.set_defaults(func=cmd_fetch_batch)

    lyrics_submit = subparsers.add_parser("lyrics-submit", help="Submit a lyrics generation task")
    add_prompt_args(lyrics_submit)
    lyrics_submit.add_argument("--notify-hook", help="Optional callback URL")
    lyrics_submit.set_defaults(func=cmd_lyrics_submit)

    lyrics_fetch = subparsers.add_parser("lyrics-fetch", help="Fetch generated lyrics")
    lyrics_fetch.add_argument("task_id")
    lyrics_fetch.set_defaults(func=cmd_lyrics_fetch)

    tags = subparsers.add_parser("tags", help="Expand or refine style tags")
    tags.add_argument("original_tags")
    tags.set_defaults(func=cmd_tags)

    upload_file = subparsers.add_parser("upload-file", help="Upload a local audio file")
    upload_file.add_argument("file")
    upload_file.add_argument("--extension", help="Audio extension, inferred from file by default")
    upload_file.add_argument("--upload-prefix", default="/suno", help="Use /suno or /sunoi")
    upload_file.add_argument("--upload-type", default="file_upload")
    upload_file.add_argument("--upload-filename", help="Filename reported to the API")
    upload_file.set_defaults(func=cmd_upload_file)

    upload_url = subparsers.add_parser("upload-url", help="Upload music by URL")
    upload_url.add_argument("url")
    upload_url.set_defaults(func=cmd_upload_url)

    upload_status = subparsers.add_parser("upload-status", help="Fetch uploaded audio processing status")
    upload_status.add_argument("upload_id")
    upload_status.add_argument("--upload-prefix", default="/suno", help="Use /suno or /sunoi")
    upload_status.set_defaults(func=cmd_upload_status)

    upload_init = subparsers.add_parser("upload-init", help="Initialize a processed uploaded audio clip")
    upload_init.add_argument("upload_id")
    upload_init.add_argument("--upload-prefix", default="/suno", help="Use /suno or /sunoi")
    upload_init.set_defaults(func=cmd_upload_init)

    persona = subparsers.add_parser("persona-create", help="Create a Persona singer style")
    persona.add_argument("--root-clip-id", required=True)
    persona.add_argument("--name", required=True)
    persona.add_argument("--description", required=True)
    persona.add_argument("--clips", nargs="*", help="Persona clip IDs; defaults to root clip")
    persona.add_argument("--public", dest="is_public", action="store_true", help="Set is_public=true")
    persona.set_defaults(is_public=False, func=cmd_persona_create)

    concat = subparsers.add_parser("concat", help="Concat an extended or infilled clip into a full song")
    concat.add_argument("clip_id")
    concat.add_argument("--is-infill", type=parse_bool, default=False)
    concat.set_defaults(func=cmd_concat)

    for command in ("timing", "wav", "mp4", "midi"):
        act = subparsers.add_parser(command, help=f"Call /suno/act/{command}/<clip_id>")
        act.add_argument("clip_id")
        act.set_defaults(func=cmd_act)

    v1_generate = subparsers.add_parser("v1-generate", help="Submit to legacy /suno/generate")
    add_submit_args(v1_generate)
    v1_generate.set_defaults(func=cmd_v1_generate)

    v1_feed = subparsers.add_parser("v1-feed", help="Fetch legacy clips through /suno/feed")
    v1_feed.add_argument("clip_ids", nargs="+")
    v1_feed.set_defaults(func=cmd_v1_feed)

    v1_lyrics_submit = subparsers.add_parser("v1-lyrics-submit", help="Submit legacy lyrics generation")
    add_prompt_args(v1_lyrics_submit)
    v1_lyrics_submit.set_defaults(func=cmd_v1_lyrics_submit)

    v1_lyrics_fetch = subparsers.add_parser("v1-lyrics-fetch", help="Fetch legacy lyrics")
    v1_lyrics_fetch.add_argument("task_id")
    v1_lyrics_fetch.set_defaults(func=cmd_v1_lyrics_fetch)

    v1_concat = subparsers.add_parser("v1-concat", help="Legacy concat")
    v1_concat.add_argument("clip_id")
    v1_concat.add_argument("--is-infill", type=parse_bool, default=False)
    v1_concat.set_defaults(func=cmd_v1_concat)

    v1_stems = subparsers.add_parser("v1-stems", help="Legacy stems request through /suno/generate")
    add_submit_args(v1_stems)
    v1_stems.set_defaults(mode="stems", func=cmd_v1_stems)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.poll_interval <= 0:
        parser.error("--poll-interval must be greater than 0")
    if args.timeout <= 0:
        parser.error("--timeout must be greater than 0")
    load_dotenv(args.env_file)
    try:
        args.func(args)
    except ApiError as exc:
        print(friendly_api_error(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
