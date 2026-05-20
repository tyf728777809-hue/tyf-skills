---
name: yy16-h72-map-offset
description: Use when generating NetEase DD backend H72_MAP JSON for 燕云十六声 after game updates, including Win64r/offSet, Win64rh/greyOffSet, curVersion, versionStr, reason, H72 offset, or 可贴后台 JSON requests.
---

# 燕云 H72 Map Offset

## Overview

Generate a complete backend-ready `H72_MAP` JSON for NetEase DD after 燕云十六声 updates. Use the local scanner; do not use DD logs as the source of truth unless explicitly doing fallback analysis.

The daily goal is no-game-launch output when static confidence is `high`. If the scanner reports `medium` or `low`, do not present the JSON as publishable.

## Fixed Paths

- Tool: `C:\Users\N30846\Documents\Codex\2026-05-19\dd\h72_offset_finder.py`
- Portable tool copy: `scripts\h72_offset_finder.py` inside this skill folder. Prefer this copy when the original local workspace path does not exist.
- `Win64r`: `E:\yysls\yysls_medium\Engine\Binaries\Win64r\yysls.exe`
- `Win64rh`: `E:\yysls\yysls_medium\Engine\Binaries\Win64rh\yysls.exe`
- Data dir: `C:\Users\N30846\Documents\Codex\yy16-h72-offsets`
- Seeds: `C:\Users\N30846\Documents\Codex\yy16-h72-offsets\h72_samples.json`
- Current backend baseline: `C:\Users\N30846\Documents\Codex\yy16-h72-offsets\h72_current_backend.json`

## Workflow

1. Prefer auto-discovering `curVersion` from the game files. Only use a user-provided `curVersion` when they explicitly supply one.
2. Run the scanner with both packages and the current backend baseline. Omit `--cur-version` for automatic discovery:

```powershell
py -3 "C:\Users\N30846\Documents\Codex\2026-05-19\dd\h72_offset_finder.py" `
  --win64r "E:\yysls\yysls_medium\Engine\Binaries\Win64r\yysls.exe" `
  --win64rh "E:\yysls\yysls_medium\Engine\Binaries\Win64rh\yysls.exe" `
  --seeds "C:\Users\N30846\Documents\Codex\yy16-h72-offsets\h72_samples.json" `
  --current-backend "C:\Users\N30846\Documents\Codex\yy16-h72-offsets\h72_current_backend.json" `
  --stable-dir "C:\Users\N30846\Documents\Codex\yy16-h72-offsets" `
  --write-scan-report `
  --audit-package-dirs `
  --report
```

If this skill was installed from GitHub and the fixed local tool path is unavailable, run the bundled script from the skill directory:

```powershell
py -3 ".\scripts\h72_offset_finder.py" `
  --win64r "E:\yysls\yysls_medium\Engine\Binaries\Win64r\yysls.exe" `
  --win64rh "E:\yysls\yysls_medium\Engine\Binaries\Win64rh\yysls.exe" `
  --seeds "C:\Users\N30846\Documents\Codex\yy16-h72-offsets\h72_samples.json" `
  --current-backend "C:\Users\N30846\Documents\Codex\yy16-h72-offsets\h72_current_backend.json" `
  --stable-dir "C:\Users\N30846\Documents\Codex\yy16-h72-offsets" `
  --write-scan-report `
  --audit-package-dirs `
  --report
```

3. Return the generated JSON from stdout. Include a short confidence note:
   - `high`: publishable.
   - `medium`: candidate JSON; recommend runtime validation before publishing. This includes `.data` RVA rebase from a verified historical sample.
   - `low`: do not provide as publishable; explain which package needs runtime validation or CE fallback.
4. After the user confirms the JSON has been published, rerun the same command with `--write-current-backend` to update the local baseline.

If the user has just confirmed a package through runtime read-only validation or CE, append it to the sample library:

```powershell
py -3 "C:\Users\N30846\Documents\Codex\2026-05-19\dd\h72_offset_finder.py" `
  --win64r "E:\yysls\yysls_medium\Engine\Binaries\Win64r\yysls.exe" `
  --win64rh "E:\yysls\yysls_medium\Engine\Binaries\Win64rh\yysls.exe" `
  --seeds "C:\Users\N30846\Documents\Codex\yy16-h72-offsets\h72_samples.json" `
  --cur-version "<CUR_VERSION>" `
  --current-backend "C:\Users\N30846\Documents\Codex\yy16-h72-offsets\h72_current_backend.json" `
  --record-confirmed-samples `
  --sample-source "runtime_readonly" `
  --report
```

## Backend Rules

- `offSet`: `Win64r` coordinates.
- `greyOffSet`: `Win64rh` coordinates.
- `offSetFast`: exact copy of `offSet`.
- `greyOffSetFast`: exact copy of `greyOffSet`.
- `versionStr`: line 3 of the corresponding package's `dump.config`.
- `curVersion`: auto-discovered from `LocalData\patch_log` publish version plus `Win64r\Built.version`/`dump.config` revision. The assembled format is `1.<major>.<minor>.<revision>`.
- Axis suffix rule for both packages: `x` ends in `C`, `y` ends in `4`, `z` ends in `8`.
- Coordinate structure rule for both packages: `y=base+0x04`, `z=base+0x08`, `x=base+0x0C`.
- `dump.config` and `Built.version` are metadata only. The coordinate source is `yysls.exe`; other directory files are audit evidence only.
- If a package update shifts the `.data` virtual address, the tool may rebase the previous verified sample by the `.data` RVA delta, but that remains `medium` until runtime-confirmed.

## Reason Rules

Compare only coordinates against `h72_current_backend.json`; ignore version string changes for reason.

| Coordinate change | reason |
| --- | --- |
| neither package changed | `W更新` |
| only `Win64r` changed | `R更新` |
| only `Win64rh` changed | `RH更新` |
| both changed | `R&RH更新` |

## Fallback

- If a package is `medium`, ask the user to start that package and run runtime validation.
- If a package is `low`, use only that package for CE/manual fallback and then update `h72_samples.json`.
- Never copy `Win64r` results into `Win64rh` or the reverse just because coordinates look similar.
- DD logs are not the game-coordinate source. Use the current backend JSON only to determine `reason`, and use DD logs only as fallback reference that must be validated against the corresponding package.
