# H72 Offset Finder

This workspace contains a read-only maintenance tool for the Yanyun H72 map offsets used by DD.

It treats the two game launch packages as separate targets:

- `Win64r` writes `offSet` and `offSetFast`.
- `Win64rh` writes `greyOffSet` and `greyOffSetFast`.
- Both packages use the same axis suffix rule: `x` ends in `C`, `y` ends in `4`, and `z` ends in `8`.
- The suffix rule checks only the last hex digit, not the last byte. For example, both `0x...0C` and `0x...4C` are valid `x` suffixes.
- The three axes must also be one coordinate struct: `y=base+0x04`, `z=base+0x08`, `x=base+0x0C`.
- Other files in the package directory are audit evidence only. `dump.config` provides `versionStr`; `Built.version` helps version checks; `yysls.exe` remains the coordinate source.

## Files

- `h72_offset_finder.py`: PE parser, static signature learner/scanner, `.data` and coordinate-struct validation, package audit, H72_MAP writer, optional runtime read-only validation.
- `h72_seeds.example.json`: sample library template. Copy it to `h72_seeds.json` or use the persistent `h72_samples.json`, then update it with manually verified offsets.
- `tests/test_h72_offset_finder.py`: regression tests for package separation and output schema.

## First Setup After Manual CE Verification

After CE or DD confirms a verified offset set for both packages, write those values into `h72_seeds.json`, then learn signatures from that exact verified version:

```powershell
Copy-Item .\h72_seeds.example.json .\h72_seeds.json
py -3 .\h72_offset_finder.py `
  --win64r "E:\yysls\yysls_medium\Engine\Binaries\Win64r\yysls.exe" `
  --win64rh "E:\yysls\yysls_medium\Engine\Binaries\Win64rh\yysls.exe" `
  --seeds .\h72_seeds.json `
  --learn-signatures `
  --write-seeds `
  --report
```

## Normal Update Flow

Run the static scan against both updated packages:

```powershell
py -3 .\h72_offset_finder.py `
  --win64r "E:\yysls\yysls_medium\Engine\Binaries\Win64r\yysls.exe" `
  --win64rh "E:\yysls\yysls_medium\Engine\Binaries\Win64rh\yysls.exe" `
  --seeds .\h72_seeds.json `
  --version-win64r "Win64r_version" `
  --version-win64rh "Win64rh_version" `
  --output .\h72_map.json `
  --report
```

To generate the full backend JSON, pass the current Yanyun version and the persistent backend baseline:

```powershell
py -3 .\h72_offset_finder.py `
  --win64r "E:\yysls\yysls_medium\Engine\Binaries\Win64r\yysls.exe" `
  --win64rh "E:\yysls\yysls_medium\Engine\Binaries\Win64rh\yysls.exe" `
  --seeds "C:\Users\N30846\Documents\Codex\yy16-h72-offsets\h72_samples.json" `
  --cur-version "1.29.30.57817" `
  --current-backend "C:\Users\N30846\Documents\Codex\yy16-h72-offsets\h72_current_backend.json" `
  --stable-dir "C:\Users\N30846\Documents\Codex\yy16-h72-offsets" `
  --write-scan-report `
  --audit-package-dirs `
  --report
```

Publish directly only when both packages are `high`. Scan reports include a top-level `publishable` flag and per-package audit evidence. If either package is `medium`, stdout is only a candidate JSON and stderr says which package still needs runtime validation or CE backfill. A `.data` RVA rebase from a verified historical sample is also `medium` until runtime-confirmed.

If a package reports `medium`, it means the seed offset still passes structural checks, but no static signature proved it moved correctly. Start that package and run read-only runtime validation:

```powershell
py -3 .\h72_offset_finder.py `
  --win64r "E:\yysls\yysls_medium\Engine\Binaries\Win64r\yysls.exe" `
  --win64rh "E:\yysls\yysls_medium\Engine\Binaries\Win64rh\yysls.exe" `
  --seeds .\h72_seeds.json `
  --runtime-validate `
  --output .\h72_map.json `
  --report
```

If a package remains `low`, do not copy the other package's result into it. Use CE only for the failed package, update that package's `offsets` in `h72_seeds.json`, then rerun `--learn-signatures --write-seeds`.

## Package Audit

Use this to inspect the two game folders without treating non-exe files as coordinate sources:

```powershell
py -3 .\h72_offset_finder.py `
  --win64r "E:\yysls\yysls_medium\Engine\Binaries\Win64r\yysls.exe" `
  --win64rh "E:\yysls\yysls_medium\Engine\Binaries\Win64rh\yysls.exe" `
  --seeds "C:\Users\N30846\Documents\Codex\yy16-h72-offsets\h72_samples.json" `
  --current-backend "C:\Users\N30846\Documents\Codex\yy16-h72-offsets\h72_current_backend.json" `
  --audit-package-dirs
```

The audit records symbol files, `dump.config`, `Built.version`, non-exe known offset hits, PE section entropy, and packed/shelled evidence. Non-exe offset hits such as `libcef.dll` are explicitly marked `usable=false`.

## Sample Library

Each confirmed sample stores package, `versionStr`, `curVersion`, exe SHA-256, offsets, source, confidence, and signatures. To append confirmed scan results:

```powershell
py -3 .\h72_offset_finder.py `
  --win64r "E:\yysls\yysls_medium\Engine\Binaries\Win64r\yysls.exe" `
  --win64rh "E:\yysls\yysls_medium\Engine\Binaries\Win64rh\yysls.exe" `
  --seeds "C:\Users\N30846\Documents\Codex\yy16-h72-offsets\h72_samples.json" `
  --cur-version "1.29.30.57817" `
  --current-backend "C:\Users\N30846\Documents\Codex\yy16-h72-offsets\h72_current_backend.json" `
  --record-confirmed-samples `
  --sample-source "runtime_readonly" `
  --report
```

## Release Checks

Before publishing:

- Both packages must have axis suffixes `x=C`, `y=4`, `z=8`.
- The three offsets must share one coordinate struct: `base+0x04/base+0x08/base+0x0C`.
- DD logs showing an adapted `H72_MAP` are evidence of the online published value, not the game coordinate source. Use them only as reference or fallback, then validate against the corresponding package.
- All three offsets must be inside the target exe's readable `.data` section.
- If a package update only shifts the `.data` virtual address, the tool may rebase the previous sample by the `.data` RVA delta and mark it `medium`.
- `versionStr` is read from line 3 of each package's `dump.config`.
- `curVersion` is auto-discovered when omitted: patch logs provide `publish.win64.o.formal.usual.<timestamp>.<major>.<minor>`, and `Win64r\Built.version` or `dump.config` provides the `rxxxxx` revision. The backend value is assembled as `1.<major>.<minor>.<revision>`.
- `reason` compares new coordinates against `h72_current_backend.json`: `W更新`, `R更新`, `RH更新`, or `R&RH更新`.
- `--report` prints both hex and decimal values. The decimal numbers should match the values DD logs under `CheckDLL.updateOffSet`.

## Test

```powershell
py -3 -m unittest discover -s tests -v
```
