from __future__ import annotations

import argparse
import ctypes
import datetime as _datetime
import hashlib
import json
import math
import os
import re
import struct
import sys
from collections import Counter, OrderedDict, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence


IMAGE_SCN_MEM_READ = 0x40000000
IMAGE_SCN_MEM_EXECUTE = 0x20000000
IMAGE_SCN_CNT_INITIALIZED_DATA = 0x00000040
DEFAULT_DATA_DIR = Path.home() / "Documents" / "Codex" / "yy16-h72-offsets"
DEFAULT_CURRENT_BACKEND_NAME = "h72_current_backend.json"
SYMBOL_EXTENSIONS = {".pdb", ".map", ".sym"}
DEFAULT_KNOWN_OFFSET_SCAN_LIMIT = 256 * 1024 * 1024
AXIS_STRUCT_OFFSETS: Mapping[str, int] = OrderedDict([("x", 0x0C), ("y", 0x04), ("z", 0x08)])
CUR_VERSION_RE = re.compile(
    r"version\s*[:=]\s*publish\.win64\.o\.formal\.usual\.(?P<stamp>\d{8,14})\.(?P<major>\d+)\.(?P<minor>\d+)"
)
REVISION_RE = re.compile(r"\br(?P<revision>\d+)\b")


@dataclass(frozen=True)
class PackageRule:
    name: str
    output_key: str
    fast_key: str
    axis_suffix_nibbles: Mapping[str, int]


PACKAGE_RULES: Mapping[str, PackageRule] = OrderedDict(
    {
        "Win64r": PackageRule(
            name="Win64r",
            output_key="offSet",
            fast_key="offSetFast",
            axis_suffix_nibbles=OrderedDict([("x", 0xC), ("y", 0x4), ("z", 0x8)]),
        ),
        "Win64rh": PackageRule(
            name="Win64rh",
            output_key="greyOffSet",
            fast_key="greyOffSetFast",
            axis_suffix_nibbles=OrderedDict([("x", 0xC), ("y", 0x4), ("z", 0x8)]),
        ),
    }
)


@dataclass(frozen=True)
class OffsetTriplet:
    x: int
    y: int
    z: int
    version_str: str = ""

    def value_for_axis(self, axis: str) -> int:
        if axis == "x":
            return self.x
        if axis == "y":
            return self.y
        if axis == "z":
            return self.z
        raise KeyError(axis)

    def replace_axis(self, axis: str, value: int) -> "OffsetTriplet":
        values = {"x": self.x, "y": self.y, "z": self.z}
        values[axis] = value
        return OffsetTriplet(version_str=self.version_str, **values)

    @classmethod
    def from_mapping(cls, data: Mapping[str, object], version_str: str = "") -> "OffsetTriplet":
        if not data:
            raise ValueError("offset mapping is empty")
        return cls(
            x=parse_offset_int(data["x"]),
            y=parse_offset_int(data["y"]),
            z=parse_offset_int(data["z"]),
            version_str=str(version_str or data.get("versionStr") or data.get("version") or ""),
        )

    def to_h72_dict(self) -> OrderedDict[str, str]:
        return OrderedDict(
            [
                ("x", format_offset(self.x)),
                ("y", format_offset(self.y)),
                ("z", format_offset(self.z)),
                ("versionStr", self.version_str),
            ]
        )


@dataclass(frozen=True)
class PESection:
    name: str
    virtual_address: int
    virtual_size: int
    raw_pointer: int
    raw_size: int
    characteristics: int

    @property
    def virtual_end(self) -> int:
        return self.virtual_address + max(self.virtual_size, self.raw_size, 1)

    @property
    def is_readable(self) -> bool:
        return bool(self.characteristics & IMAGE_SCN_MEM_READ)

    @property
    def is_executable(self) -> bool:
        return bool(self.characteristics & IMAGE_SCN_MEM_EXECUTE)

    @property
    def is_data(self) -> bool:
        return self.name == ".data" or self.name.startswith(".data$")

    def contains_rva(self, rva: int) -> bool:
        return self.virtual_address <= rva < self.virtual_end


@dataclass(frozen=True)
class PEImage:
    path: Path
    image_base: int
    sections: Sequence[PESection]

    def section_for_rva(self, rva: int) -> PESection | None:
        for section in self.sections:
            if section.contains_rva(rva):
                return section
        return None

    def readable_data_section_for_rva(self, rva: int) -> PESection | None:
        section = self.section_for_rva(rva)
        if section and section.is_data and section.is_readable and not section.is_executable:
            return section
        return None

    def rva_to_file_offset(self, rva: int) -> int | None:
        section = self.section_for_rva(rva)
        if not section:
            return None
        delta = rva - section.virtual_address
        if delta >= section.raw_size:
            return None
        return section.raw_pointer + delta


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class StaticSignature:
    package: str
    axis: str
    kind: str
    pattern: tuple[int | None, ...]
    value_offset: int
    source_file_offset: int
    context: int

    def to_json(self) -> OrderedDict[str, object]:
        return OrderedDict(
            [
                ("package", self.package),
                ("axis", self.axis),
                ("kind", self.kind),
                ("pattern", pattern_to_text(self.pattern)),
                ("valueOffset", self.value_offset),
                ("sourceFileOffset", self.source_file_offset),
                ("context", self.context),
            ]
        )

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "StaticSignature":
        return cls(
            package=str(data["package"]),
            axis=str(data["axis"]),
            kind=str(data["kind"]),
            pattern=pattern_from_text(str(data["pattern"])),
            value_offset=int(data["valueOffset"]),
            source_file_offset=int(data.get("sourceFileOffset", -1)),
            context=int(data.get("context", 0)),
        )


@dataclass
class ScanResult:
    package: str
    confidence: str
    triplet: OffsetTriplet | None
    validation: ValidationReport = field(default_factory=ValidationReport)
    notes: list[str] = field(default_factory=list)


@dataclass
class RuntimeValidation:
    ok: bool
    values: Mapping[str, float] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


def parse_offset_int(value: object) -> int:
    if isinstance(value, bool):
        raise ValueError(f"invalid offset value: {value!r}")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError("empty offset value")
        return int(text, 0)
    raise TypeError(f"unsupported offset value: {value!r}")


def format_offset(value: int) -> str:
    return f"0x{value:X}"


def parse_pe(path: str | os.PathLike[str]) -> PEImage:
    exe_path = Path(path)
    data = exe_path.read_bytes()
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise ValueError(f"{exe_path} is not a PE file: missing MZ header")

    e_lfanew = _read_u32(data, 0x3C)
    if e_lfanew + 24 > len(data) or data[e_lfanew : e_lfanew + 4] != b"PE\0\0":
        raise ValueError(f"{exe_path} is not a PE file: missing PE signature")

    file_header_offset = e_lfanew + 4
    (
        _machine,
        number_of_sections,
        _timestamp,
        _symbol_table,
        _symbol_count,
        size_of_optional_header,
        _characteristics,
    ) = struct.unpack_from("<HHIIIHH", data, file_header_offset)

    optional_offset = file_header_offset + 20
    if optional_offset + size_of_optional_header > len(data):
        raise ValueError(f"{exe_path} has a truncated optional header")

    magic = _read_u16(data, optional_offset)
    if magic == 0x20B:
        image_base = _read_u64(data, optional_offset + 24)
    elif magic == 0x10B:
        image_base = _read_u32(data, optional_offset + 28)
    else:
        raise ValueError(f"{exe_path} has unknown PE optional header magic 0x{magic:X}")

    section_offset = optional_offset + size_of_optional_header
    sections: list[PESection] = []
    for index in range(number_of_sections):
        offset = section_offset + index * 40
        if offset + 40 > len(data):
            raise ValueError(f"{exe_path} has a truncated section table")
        raw_name = struct.unpack_from("<8s", data, offset)[0]
        name = raw_name.split(b"\0", 1)[0].decode("ascii", errors="replace")
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from("<IIII", data, offset + 8)
        characteristics = _read_u32(data, offset + 36)
        sections.append(
            PESection(
                name=name,
                virtual_address=virtual_address,
                virtual_size=virtual_size,
                raw_pointer=raw_pointer,
                raw_size=raw_size,
                characteristics=characteristics,
            )
        )

    return PEImage(path=exe_path, image_base=image_base, sections=sections)


def validate_triplet(rule: PackageRule, pe: PEImage, triplet: OffsetTriplet) -> ValidationReport:
    report = ValidationReport()
    base = triplet.y - AXIS_STRUCT_OFFSETS["y"]
    expected_triplet = {
        axis: base + axis_offset
        for axis, axis_offset in AXIS_STRUCT_OFFSETS.items()
    }
    if any(triplet.value_for_axis(axis) != expected for axis, expected in expected_triplet.items()):
        report.errors.append(
            "offsets must share one coordinate struct: "
            f"expected x={format_offset(expected_triplet['x'])} "
            f"y={format_offset(expected_triplet['y'])} "
            f"z={format_offset(expected_triplet['z'])}"
        )
    for axis in ("x", "y", "z"):
        value = triplet.value_for_axis(axis)
        expected_suffix = rule.axis_suffix_nibbles[axis]
        actual_suffix = value & 0xF
        if actual_suffix != expected_suffix:
            report.errors.append(
                f"{axis} suffix nibble must be 0x{expected_suffix:X}, got 0x{actual_suffix:X} for {format_offset(value)}"
            )
        if not pe.readable_data_section_for_rva(value):
            report.errors.append(f"{axis} offset {format_offset(value)} is not in readable .data")
    return report


def build_h72_map(win64r: OffsetTriplet, win64rh: OffsetTriplet) -> OrderedDict[str, object]:
    off_set = win64r.to_h72_dict()
    grey_off_set = win64rh.to_h72_dict()
    return OrderedDict(
        [
            ("offSet", off_set),
            ("greyOffSet", grey_off_set),
            ("offSetFast", OrderedDict(off_set)),
            ("greyOffSetFast", OrderedDict(grey_off_set)),
        ]
    )


def build_backend_h72_map(
    win64r: OffsetTriplet,
    win64rh: OffsetTriplet,
    *,
    cur_version: str,
    reason: str,
) -> OrderedDict[str, object]:
    result = build_h72_map(win64r, win64rh)
    result["curVersion"] = cur_version
    result["reason"] = reason
    return result


def read_dump_config_version(path: str | os.PathLike[str]) -> str:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    if len(lines) < 3 or not lines[2].strip():
        raise ValueError(f"{path} does not contain versionStr on line 3")
    return lines[2].strip()


def discover_cur_version(
    *,
    game_root: str | os.PathLike[str] | None = None,
    win64r_exe: str | os.PathLike[str] | None = None,
    win64rh_exe: str | os.PathLike[str] | None = None,
) -> str:
    root = Path(game_root) if game_root else _infer_game_root(win64r_exe, win64rh_exe)
    if root is None:
        return ""
    patch_version = _latest_patch_publish_version(root)
    revision = _revision_from_package_files(win64r_exe, win64rh_exe, root)
    if not patch_version or not revision:
        return ""
    return f"1.{patch_version['major']}.{patch_version['minor']}.{revision}"


def determine_reason(
    previous_backend: Mapping[str, object] | None,
    win64r: OffsetTriplet,
    win64rh: OffsetTriplet,
) -> str:
    if not previous_backend:
        return "W更新"
    previous_r = _triplet_from_backend(previous_backend, "offSet")
    previous_rh = _triplet_from_backend(previous_backend, "greyOffSet")
    r_changed = previous_r is not None and not _same_coordinates(previous_r, win64r)
    rh_changed = previous_rh is not None and not _same_coordinates(previous_rh, win64rh)
    if r_changed and rh_changed:
        return "R&RH更新"
    if r_changed:
        return "R更新"
    if rh_changed:
        return "RH更新"
    return "W更新"


def learn_signatures(
    exe_path: str | os.PathLike[str],
    rule: PackageRule,
    triplet: OffsetTriplet,
    *,
    context: int = 16,
    limit_per_axis: int = 8,
) -> list[StaticSignature]:
    pe = parse_pe(exe_path)
    validation = validate_triplet(rule, pe, triplet)
    if not validation.ok:
        raise ValueError("; ".join(validation.errors))

    blob = Path(exe_path).read_bytes()
    signatures: list[StaticSignature] = []
    for axis in ("x", "y", "z"):
        value = triplet.value_for_axis(axis)
        axis_signatures: list[StaticSignature] = []
        variants = [
            ("u32_rva", struct.pack("<I", value)),
            ("u64_va", struct.pack("<Q", pe.image_base + value)),
        ]
        seen_offsets: set[tuple[int, str]] = set()
        for kind, encoded in variants:
            for occurrence in _find_all(blob, encoded):
                key = (occurrence, kind)
                if key in seen_offsets:
                    continue
                seen_offsets.add(key)
                start = max(0, occurrence - context)
                end = min(len(blob), occurrence + len(encoded) + context)
                pattern = list(blob[start:end])
                value_offset = occurrence - start
                for index in range(value_offset, value_offset + len(encoded)):
                    pattern[index] = None
                axis_signatures.append(
                    StaticSignature(
                        package=rule.name,
                        axis=axis,
                        kind=kind,
                        pattern=tuple(pattern),
                        value_offset=value_offset,
                        source_file_offset=occurrence,
                        context=context,
                    )
                )
                if len(axis_signatures) >= limit_per_axis:
                    break
            if len(axis_signatures) >= limit_per_axis:
                break
        signatures.extend(axis_signatures)
    return signatures


def scan_with_signatures(
    exe_path: str | os.PathLike[str],
    rule: PackageRule,
    signatures: Iterable[StaticSignature | Mapping[str, object]],
    *,
    version_str: str = "",
) -> ScanResult:
    normalized = [_normalize_signature(signature) for signature in signatures]
    mismatched_packages = sorted({signature.package for signature in normalized if signature.package != rule.name})
    notes = [f"signature package {package} does not match {rule.name}" for package in mismatched_packages]
    package_signatures = [signature for signature in normalized if signature.package == rule.name]
    if not package_signatures:
        return ScanResult(package=rule.name, confidence="low", triplet=None, notes=notes)

    pe = parse_pe(exe_path)
    blob = Path(exe_path).read_bytes()
    candidates: dict[str, list[int]] = defaultdict(list)

    for signature in package_signatures:
        for match_offset in find_pattern_offsets(blob, signature.pattern):
            value_position = match_offset + signature.value_offset
            value = _read_signature_value(blob, value_position, signature.kind, pe)
            if value is None:
                continue
            candidates[signature.axis].append(value)

    if not all(candidates.get(axis) for axis in ("x", "y", "z")):
        missing = [axis for axis in ("x", "y", "z") if not candidates.get(axis)]
        notes.append(f"missing signature matches for axes: {', '.join(missing)}")
        return ScanResult(package=rule.name, confidence="low", triplet=None, notes=notes)

    triplet = _choose_triplet_candidate(rule, pe, candidates, version_str=version_str)
    if not triplet:
        notes.append("signature matches did not produce a coordinate-struct-valid readable .data triplet")
        return ScanResult(package=rule.name, confidence="low", triplet=None, notes=notes)

    validation = validate_triplet(rule, pe, triplet)
    confidence = "high" if validation.ok else "low"
    return ScanResult(package=rule.name, confidence=confidence, triplet=triplet if validation.ok else None, validation=validation, notes=notes)


def scan_package(
    exe_path: str | os.PathLike[str],
    rule: str | PackageRule,
    seed_entry: Mapping[str, object] | None,
    *,
    version_str: str = "",
    previous_data_section_rva: int | None = None,
) -> ScanResult:
    seed_entry = seed_entry or {}
    rule = rule if isinstance(rule, PackageRule) else PACKAGE_RULES[str(rule)]
    seed_version = str(seed_entry.get("versionStr") or seed_entry.get("version") or "")
    output_version = version_str or seed_version
    signatures = [StaticSignature.from_mapping(item) for item in seed_entry.get("signatures", [])]
    if signatures:
        result = scan_with_signatures(exe_path, rule, signatures, version_str=output_version)
        if result.triplet:
            return result

    if seed_entry.get("offsets"):
        pe = parse_pe(exe_path)
        triplet = OffsetTriplet.from_mapping(seed_entry["offsets"], version_str=output_version)
        current_data_section = _primary_data_section(pe)
        previous_data_section_rva = previous_data_section_rva or _seed_data_section_rva(seed_entry)
        if current_data_section and previous_data_section_rva is not None:
            rebased = _rebase_triplet_to_data_section(
                triplet,
                previous_data_section_rva=previous_data_section_rva,
                current_data_section_rva=current_data_section.virtual_address,
                version_str=output_version,
            )
            if rebased and rebased != triplet:
                rebased_validation = validate_triplet(rule, pe, rebased)
                if rebased_validation.ok:
                    return ScanResult(
                        package=rule.name,
                        confidence="medium",
                        triplet=rebased,
                        validation=rebased_validation,
                        notes=[
                            "rebased seed offsets using .data RVA delta "
                            f"{format_offset(previous_data_section_rva)} -> {format_offset(current_data_section.virtual_address)}",
                            "runtime read-only validation is recommended before publishing",
                        ],
                    )
        validation = validate_triplet(rule, pe, triplet)
        if validation.ok:
            return ScanResult(
                package=rule.name,
                confidence="medium",
                triplet=triplet,
                validation=validation,
                notes=[
                    "seed offsets are structurally valid in current .data",
                    "runtime read-only validation is recommended before publishing",
                ],
            )
        return ScanResult(
            package=rule.name,
            confidence="low",
            triplet=None,
            validation=validation,
            notes=["seed offsets failed current package validation"],
        )

    return ScanResult(package=rule.name, confidence="low", triplet=None, notes=["no signatures or seed offsets available"])


def load_seed_file(path: str | os.PathLike[str] | None) -> dict[str, object]:
    if not path:
        return {"packages": {}}
    seed_path = Path(path)
    if not seed_path.exists():
        return {"packages": {}}
    return json.loads(seed_path.read_text(encoding="utf-8"))


def load_json_file(path: str | os.PathLike[str] | None) -> dict[str, object] | None:
    if not path:
        return None
    json_path = Path(path)
    if not json_path.exists():
        return None
    return json.loads(json_path.read_text(encoding="utf-8"))


def save_seed_file(path: str | os.PathLike[str], data: Mapping[str, object]) -> None:
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def save_json_file(path: str | os.PathLike[str], data: Mapping[str, object]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_seed_with_signatures(
    seed_data: dict[str, object],
    package: str,
    offsets: OffsetTriplet,
    signatures: Sequence[StaticSignature],
    *,
    cur_version: str = "",
    exe_sha256: str = "",
    source: str = "manual_confirmed",
    confidence: str = "high",
) -> dict[str, object]:
    return update_sample_library(
        seed_data,
        package,
        offsets,
        version_str=offsets.version_str,
        cur_version=cur_version,
        exe_sha256=exe_sha256,
        source=source,
        confidence=confidence,
        signatures=signatures,
    )


def update_sample_library(
    sample_data: dict[str, object],
    package: str,
    offsets: OffsetTriplet,
    *,
    version_str: str,
    cur_version: str,
    exe_sha256: str,
    source: str,
    confidence: str,
    signatures: Sequence[StaticSignature | Mapping[str, object]] = (),
    data_section_virtual_address: int | None = None,
) -> dict[str, object]:
    packages = sample_data.setdefault("packages", {})
    if not isinstance(packages, dict):
        raise ValueError("sample field 'packages' must be an object")
    entry = dict(packages.get(package, {}))
    normalized_signatures = [
        signature.to_json() if isinstance(signature, StaticSignature) else OrderedDict(signature)
        for signature in signatures
    ]
    sample_offsets = OffsetTriplet(
        x=offsets.x,
        y=offsets.y,
        z=offsets.z,
        version_str=version_str or offsets.version_str,
    )
    sample = OrderedDict(
        [
            ("package", package),
            ("versionStr", sample_offsets.version_str),
            ("curVersion", cur_version),
            ("exeSha256", exe_sha256),
            ("offsets", sample_offsets.to_h72_dict()),
            ("source", source),
            ("confidence", confidence),
        ]
    )
    if normalized_signatures:
        sample["signatures"] = normalized_signatures
    if data_section_virtual_address is not None:
        sample["dataSectionVirtualAddress"] = format_offset(data_section_virtual_address)

    history = entry.get("samples", [])
    if not isinstance(history, list):
        history = []
    history = [item for item in history if not _same_sample_identity(item, sample)]
    history.append(sample)

    entry["package"] = package
    entry["versionStr"] = sample_offsets.version_str
    entry["curVersion"] = cur_version
    entry["exeSha256"] = exe_sha256
    entry["offsets"] = sample_offsets.to_h72_dict()
    entry["source"] = source
    entry["confidence"] = confidence
    if data_section_virtual_address is not None:
        entry["dataSectionVirtualAddress"] = format_offset(data_section_virtual_address)
    entry["signatures"] = normalized_signatures
    entry["samples"] = history
    entry.pop("tails", None)
    packages[package] = entry
    return sample_data


def audit_package_directory(
    package_dir: str | os.PathLike[str],
    *,
    package: str = "",
    exe_path: str | os.PathLike[str] | None = None,
    known_offsets: Iterable[int] = (),
    max_scan_size: int = DEFAULT_KNOWN_OFFSET_SCAN_LIMIT,
) -> OrderedDict[str, object]:
    root = Path(package_dir)
    exe = Path(exe_path) if exe_path else root / "yysls.exe"
    if not exe.is_absolute():
        exe = root / exe
    exe = exe.resolve() if exe.exists() else exe

    symbol_files = _relative_files(root, SYMBOL_EXTENSIONS)
    dump_config = root / "dump.config"
    built_version = root / "Built.version"
    known_offset_values = sorted({int(value) for value in known_offsets})
    known_hits = _scan_non_exe_offset_hits(root, exe, known_offset_values, max_scan_size=max_scan_size)

    section_rows: list[OrderedDict[str, object]] = []
    packed_evidence = OrderedDict(
        [
            ("status", "exe_missing"),
            ("logicSectionsRawSizeZero", False),
            ("highEntropySections", []),
            ("unpackedImageAvailable", False),
            ("unpackedImageNote", "no unpacked memory image has been recorded"),
        ]
    )
    notes: list[str] = []
    if exe.exists():
        try:
            pe = parse_pe(exe)
            section_rows, packed_evidence = _audit_pe_sections(exe, pe)
        except Exception as exc:
            notes.append(f"PE audit failed: {exc}")
    else:
        notes.append(f"missing yysls.exe at {exe}")

    usable_sources = ["yysls.exe"] if exe.exists() else []
    if known_hits:
        notes.append("known offsets found in non-yysls files are recorded for audit only, not used as coordinate sources")

    return OrderedDict(
        [
            ("package", package),
            ("directory", str(root)),
            ("exe", str(exe) if exe.exists() else ""),
            ("dumpVersion", read_dump_config_version(dump_config) if dump_config.exists() else ""),
            ("builtVersion", built_version.read_text(encoding="utf-8", errors="replace").strip() if built_version.exists() else ""),
            ("symbolFiles", symbol_files),
            ("usableCoordinateSources", usable_sources),
            ("knownOffsetHits", known_hits),
            ("binPatchCopies", _find_binpatch_exe_copies(root, exe) if exe.exists() else []),
            ("peSections", section_rows),
            ("packedEvidence", packed_evidence),
            ("notes", notes),
        ]
    )


def pattern_to_text(pattern: Sequence[int | None]) -> str:
    return " ".join("??" if item is None else f"{item:02X}" for item in pattern)


def pattern_from_text(text: str) -> tuple[int | None, ...]:
    tokens = text.strip().split()
    pattern: list[int | None] = []
    for token in tokens:
        if token in {"?", "??", "**"}:
            pattern.append(None)
        else:
            pattern.append(int(token, 16))
    return tuple(pattern)


def find_pattern_offsets(blob: bytes, pattern: Sequence[int | None]) -> list[int]:
    if not pattern or len(pattern) > len(blob):
        return []

    anchor_start, anchor = _longest_anchor(pattern)
    if not anchor:
        return _brute_force_pattern_offsets(blob, pattern)

    results: list[int] = []
    search_from = 0
    while True:
        found = blob.find(anchor, search_from)
        if found < 0:
            break
        candidate_start = found - anchor_start
        if 0 <= candidate_start <= len(blob) - len(pattern) and _pattern_matches_at(blob, pattern, candidate_start):
            results.append(candidate_start)
        search_from = found + 1
    return results


def validate_runtime_values(values: Mapping[str, float]) -> RuntimeValidation:
    if set(values) != {"x", "y", "z"}:
        return RuntimeValidation(ok=False, values=values, notes=["runtime validation needs x/y/z values"])
    if not all(math.isfinite(value) for value in values.values()):
        return RuntimeValidation(ok=False, values=values, notes=["runtime values contain NaN or infinity"])
    if any(abs(value) > 100_000_000 for value in values.values()):
        return RuntimeValidation(ok=False, values=values, notes=["runtime values are outside plausible coordinate bounds"])
    if all(abs(value) < 1e-20 for value in values.values()):
        return RuntimeValidation(ok=False, values=values, notes=["runtime values are all zero or denormal"])
    return RuntimeValidation(ok=True, values=values, notes=["runtime values are finite and plausible"])


def validate_running_process(
    exe_path: str | os.PathLike[str],
    triplet: OffsetTriplet,
    *,
    pid: int | None = None,
) -> RuntimeValidation:
    if os.name != "nt":
        return RuntimeValidation(ok=False, notes=["runtime validation is only implemented on Windows"])
    try:
        return _validate_running_process_windows(Path(exe_path), triplet, pid=pid)
    except Exception as exc:  # pragma: no cover - platform defensive path
        return RuntimeValidation(ok=False, notes=[f"runtime validation failed: {exc}"])


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Maintain Yanyun H72_MAP offsets for Win64r and Win64rh independently.",
    )
    parser.add_argument("--win64r", help="Path to Engine\\Binaries\\Win64r\\yysls.exe")
    parser.add_argument("--win64rh", help="Path to Engine\\Binaries\\Win64rh\\yysls.exe")
    parser.add_argument("--seeds", default="h72_seeds.json", help="Seed/signature JSON file")
    parser.add_argument("--output", help="Write H72_MAP JSON to this path. Defaults to stdout.")
    parser.add_argument("--cur-version", help="Current Yanyun version to write as curVersion, for example 1.29.30.57817")
    parser.add_argument("--game-root", help="Game root used to auto-discover curVersion. Defaults to the common yysls_medium root.")
    parser.add_argument("--version-win64r", default="", help="Version string to write for Win64r")
    parser.add_argument("--version-win64rh", default="", help="Version string to write for Win64rh")
    parser.add_argument("--stable-dir", default=str(DEFAULT_DATA_DIR), help="Persistent H72 data directory")
    parser.add_argument("--current-backend", help="Current published backend JSON. Defaults to stable-dir\\h72_current_backend.json")
    parser.add_argument("--write-current-backend", action="store_true", help="Overwrite current backend JSON with generated output")
    parser.add_argument("--write-scan-report", action="store_true", help="Write a scan report under stable-dir\\reports")
    parser.add_argument("--audit-package-dirs", action="store_true", help="Audit package directories for metadata, symbols, packed sections, and non-exe offset hits")
    parser.add_argument("--runtime-validate", action="store_true", help="Read running process memory to validate medium results")
    parser.add_argument("--pid-win64r", type=int, help="PID for Win64r runtime validation")
    parser.add_argument("--pid-win64rh", type=int, help="PID for Win64rh runtime validation")
    parser.add_argument("--learn-signatures", action="store_true", help="Regenerate signatures from the supplied exe and seed offsets")
    parser.add_argument("--write-seeds", action="store_true", help="Write learned signatures back to --seeds")
    parser.add_argument("--record-confirmed-samples", action="store_true", help="Append successful scan results to the sample library")
    parser.add_argument("--sample-source", default="confirmed_static_scan", help="Source label for --record-confirmed-samples")
    parser.add_argument("--sample-confidence", choices=["low", "medium", "high"], help="Confidence label for --record-confirmed-samples. Defaults to each scan result confidence.")
    parser.add_argument("--report", action="store_true", help="Print scan confidence report to stderr")
    args = parser.parse_args(argv)
    if not args.cur_version:
        args.cur_version = discover_cur_version(
            game_root=args.game_root,
            win64r_exe=args.win64r,
            win64rh_exe=args.win64rh,
        )

    seed_data = load_seed_file(args.seeds)
    packages = seed_data.get("packages", {})
    if not isinstance(packages, dict):
        raise SystemExit("seed field 'packages' must be an object")

    current_backend_path = Path(args.current_backend) if args.current_backend else Path(args.stable_dir) / DEFAULT_CURRENT_BACKEND_NAME
    previous_backend = load_json_file(current_backend_path)
    paths = {"Win64r": args.win64r, "Win64rh": args.win64rh}
    versions = {
        "Win64r": args.version_win64r or _read_dump_version_for_exe(args.win64r),
        "Win64rh": args.version_win64rh or _read_dump_version_for_exe(args.win64rh),
    }
    pids = {"Win64r": args.pid_win64r, "Win64rh": args.pid_win64rh}
    known_offsets = _collect_known_offsets(seed_data, previous_backend or {})
    package_audits: dict[str, Mapping[str, object]] = {}
    if args.audit_package_dirs or args.write_scan_report:
        for package, exe_path in paths.items():
            if exe_path:
                package_audits[package] = audit_package_directory(
                    Path(exe_path).parent,
                    package=package,
                    exe_path=exe_path,
                    known_offsets=known_offsets,
                )

    audit_only = args.audit_package_dirs and not any(
        [
            args.cur_version,
            args.output,
            args.write_scan_report,
            args.runtime_validate,
            args.learn_signatures,
            args.write_current_backend,
            args.record_confirmed_samples,
        ]
    )
    if audit_only:
        print(json.dumps(OrderedDict([("packages", package_audits)]), ensure_ascii=False, indent=2))
        return 0

    results: dict[str, ScanResult] = {}

    for package, exe_path in paths.items():
        if not exe_path:
            continue
        seed_entry = packages.get(package, {})
        if not isinstance(seed_entry, dict):
            raise SystemExit(f"seed entry for {package} must be an object")
        rule = PACKAGE_RULES[package]
        previous_data_section_rva = _seed_data_section_rva(seed_entry)
        if previous_data_section_rva is None:
            previous_data_section_rva = find_latest_report_data_section_rva(
                Path(args.stable_dir),
                package=package,
                version_str=_seed_entry_version(seed_entry),
            )

        if args.learn_signatures:
            if not seed_entry.get("offsets"):
                raise SystemExit(f"{package} needs seed offsets before signatures can be learned")
            offsets = OffsetTriplet.from_mapping(seed_entry["offsets"], version_str=versions[package])
            learned = learn_signatures(exe_path, rule, offsets)
            update_seed_with_signatures(
                seed_data,
                package,
                offsets,
                learned,
                cur_version=args.cur_version or "",
                exe_sha256=sha256_file(exe_path),
                source="signature_learning",
                confidence="high",
            )
            seed_entry = seed_data["packages"][package]

        result = scan_package(
            exe_path,
            rule,
            seed_entry,
            version_str=versions[package],
            previous_data_section_rva=previous_data_section_rva,
        )
        if args.runtime_validate and result.triplet:
            runtime = validate_running_process(exe_path, result.triplet, pid=pids[package])
            result.notes.extend(runtime.notes)
            if runtime.ok and result.confidence == "medium":
                result.confidence = "high"
            elif not runtime.ok:
                result.confidence = "low"
        results[package] = result

    if args.learn_signatures and args.write_seeds:
        save_seed_file(args.seeds, seed_data)

    if args.record_confirmed_samples:
        for package, result in results.items():
            if not result.triplet:
                continue
            update_sample_library(
                seed_data,
                package,
                result.triplet,
                version_str=result.triplet.version_str,
                cur_version=args.cur_version or "",
                exe_sha256=sha256_file(paths[package]),
                source=args.sample_source,
                confidence=args.sample_confidence or result.confidence,
                signatures=packages.get(package, {}).get("signatures", []) if isinstance(packages.get(package, {}), dict) else [],
                data_section_virtual_address=_current_data_section_rva(paths[package]),
            )
        save_seed_file(args.seeds, seed_data)

    if args.report:
        _print_report(results, file=sys.stderr)

    missing = [package for package in ("Win64r", "Win64rh") if package not in results or results[package].triplet is None]
    if missing:
        if not args.report:
            _print_report(results, file=sys.stderr)
        print(f"missing publishable offsets for: {', '.join(missing)}", file=sys.stderr)
        return 2

    if args.cur_version:
        reason = determine_reason(previous_backend, results["Win64r"].triplet, results["Win64rh"].triplet)
        h72_map = build_backend_h72_map(
            results["Win64r"].triplet,
            results["Win64rh"].triplet,
            cur_version=args.cur_version,
            reason=reason,
        )
    else:
        h72_map = build_h72_map(results["Win64r"].triplet, results["Win64rh"].triplet)

    if args.write_scan_report:
        report_path = write_scan_report(
            Path(args.stable_dir) / "reports",
            cur_version=args.cur_version or "",
            package_paths=paths,
            results=results,
            h72_map=h72_map,
            current_backend_path=current_backend_path,
            package_audits=package_audits,
        )
        if args.report:
            print(f"scan report: {report_path}", file=sys.stderr)

    if args.write_current_backend:
        if not args.cur_version:
            print("--write-current-backend requires --cur-version", file=sys.stderr)
            return 2
        not_publishable = [package for package, result in results.items() if result.confidence != "high"]
        if not_publishable:
            print(
                "--write-current-backend requires high confidence for both packages; "
                f"not publishable: {', '.join(not_publishable)}",
                file=sys.stderr,
            )
            return 2
        save_json_file(current_backend_path, h72_map)

    not_high = [package for package, result in results.items() if result.confidence != "high"]
    if not_high:
        if not args.report:
            _print_report(results, file=sys.stderr)
        print(
            "candidate output only; runtime validation or CE backfill is required before publishing for: "
            + ", ".join(not_high),
            file=sys.stderr,
        )

    payload = json.dumps(h72_map, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


def write_scan_report(
    report_dir: str | os.PathLike[str],
    *,
    cur_version: str,
    package_paths: Mapping[str, str | None],
    results: Mapping[str, ScanResult],
    h72_map: Mapping[str, object],
    current_backend_path: str | os.PathLike[str],
    package_audits: Mapping[str, Mapping[str, object]] | None = None,
) -> Path:
    report_root = Path(report_dir)
    report_root.mkdir(parents=True, exist_ok=True)
    timestamp = _datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_version = cur_version.replace(".", "_") if cur_version else "no_cur_version"
    report_path = report_root / f"{timestamp}_{safe_version}.json"
    payload = OrderedDict(
        [
            ("timestamp", _datetime.datetime.now().isoformat(timespec="seconds")),
            ("curVersion", cur_version),
            ("currentBackend", str(current_backend_path)),
            ("publishable", all(results.get(package) and results[package].confidence == "high" for package in ("Win64r", "Win64rh"))),
            ("packages", OrderedDict()),
            ("h72Map", h72_map),
        ]
    )
    packages = payload["packages"]
    for package in ("Win64r", "Win64rh"):
        exe_path = package_paths.get(package)
        result = results.get(package)
        packages[package] = OrderedDict(
            [
                ("exe", exe_path),
                ("sha256", sha256_file(exe_path) if exe_path else ""),
                ("confidence", result.confidence if result else "not_scanned"),
                ("publishable", bool(result and result.confidence == "high")),
                ("offsets", result.triplet.to_h72_dict() if result and result.triplet else None),
                ("errors", result.validation.errors if result else []),
                ("notes", result.notes if result else []),
                ("audit", package_audits.get(package, {}) if package_audits else {}),
            ]
        )
    save_json_file(report_path, payload)
    return report_path


def _print_report(results: Mapping[str, ScanResult], *, file) -> None:
    for package in ("Win64r", "Win64rh"):
        result = results.get(package)
        if not result:
            print(f"{package}: not scanned", file=file)
            continue
        print(f"{package}: confidence={result.confidence}", file=file)
        if result.triplet:
            print(
                "  "
                f"x={format_offset(result.triplet.x)} ({result.triplet.x}) "
                f"y={format_offset(result.triplet.y)} ({result.triplet.y}) "
                f"z={format_offset(result.triplet.z)} ({result.triplet.z})",
                file=file,
            )
        for error in result.validation.errors:
            print(f"  error: {error}", file=file)
        for note in result.notes:
            print(f"  note: {note}", file=file)


def _same_sample_identity(left: object, right: Mapping[str, object]) -> bool:
    if not isinstance(left, Mapping):
        return False
    return (
        left.get("package") == right.get("package")
        and left.get("versionStr") == right.get("versionStr")
        and left.get("curVersion") == right.get("curVersion")
        and left.get("exeSha256") == right.get("exeSha256")
    )


def _primary_data_section(pe: PEImage) -> PESection | None:
    for section in pe.sections:
        if section.is_data and section.is_readable and not section.is_executable:
            return section
    return None


def _current_data_section_rva(exe_path: str | os.PathLike[str] | None) -> int | None:
    if not exe_path:
        return None
    try:
        section = _primary_data_section(parse_pe(exe_path))
    except (OSError, ValueError):
        return None
    return section.virtual_address if section else None


def _seed_data_section_rva(seed_entry: Mapping[str, object]) -> int | None:
    for key in ("dataSectionVirtualAddress", "dataSectionRva"):
        if seed_entry.get(key) is not None:
            return parse_offset_int(seed_entry[key])
    data_section = seed_entry.get("dataSection")
    if isinstance(data_section, Mapping):
        for key in ("virtualAddress", "rva"):
            if data_section.get(key) is not None:
                return parse_offset_int(data_section[key])
    samples = seed_entry.get("samples")
    if isinstance(samples, list):
        for sample in reversed(samples):
            if isinstance(sample, Mapping):
                value = _seed_data_section_rva(sample)
                if value is not None:
                    return value
    return None


def _seed_entry_version(seed_entry: Mapping[str, object]) -> str:
    if seed_entry.get("versionStr"):
        return str(seed_entry["versionStr"])
    offsets = seed_entry.get("offsets")
    if isinstance(offsets, Mapping) and offsets.get("versionStr"):
        return str(offsets["versionStr"])
    return ""


def _rebase_triplet_to_data_section(
    triplet: OffsetTriplet,
    *,
    previous_data_section_rva: int,
    current_data_section_rva: int,
    version_str: str,
) -> OffsetTriplet | None:
    delta = current_data_section_rva - previous_data_section_rva
    if delta == 0:
        return None
    return OffsetTriplet(
        x=triplet.x + delta,
        y=triplet.y + delta,
        z=triplet.z + delta,
        version_str=version_str,
    )


def find_latest_report_data_section_rva(
    stable_dir: str | os.PathLike[str],
    *,
    package: str,
    version_str: str,
) -> int | None:
    if not version_str:
        return None
    report_dir = Path(stable_dir) / "reports"
    if not report_dir.exists():
        return None
    reports = sorted(report_dir.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    for report_path in reports:
        try:
            payload = json.loads(report_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        package_payload = payload.get("packages", {}).get(package, {})
        if not isinstance(package_payload, Mapping):
            continue
        audit = package_payload.get("audit", {})
        if not isinstance(audit, Mapping):
            continue
        if str(audit.get("dumpVersion") or "") != version_str:
            continue
        data_rva = _data_section_rva_from_audit(audit)
        if data_rva is not None:
            return data_rva
    return None


def _data_section_rva_from_audit(audit: Mapping[str, object]) -> int | None:
    sections = audit.get("peSections")
    if not isinstance(sections, list):
        return None
    for section in sections:
        if isinstance(section, Mapping) and section.get("name") == ".data" and section.get("virtualAddress") is not None:
            return parse_offset_int(section["virtualAddress"])
    return None


def _collect_known_offsets(*payloads: Mapping[str, object]) -> list[int]:
    offsets: set[int] = set()

    def walk(value: object, key: str = "") -> None:
        if isinstance(value, Mapping):
            for child_key, child_value in value.items():
                walk(child_value, str(child_key))
            return
        if isinstance(value, list):
            for item in value:
                walk(item, key)
            return
        if key in {"x", "y", "z"}:
            try:
                offsets.add(parse_offset_int(value))
            except (TypeError, ValueError):
                return

    for payload in payloads:
        walk(payload)
    return sorted(offsets)


def _relative_files(root: Path, extensions: set[str]) -> list[str]:
    if not root.exists():
        return []
    results: list[str] = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in extensions:
            results.append(_relative_display_path(root, path))
    return sorted(results)


def _scan_non_exe_offset_hits(
    root: Path,
    exe: Path,
    known_offsets: Sequence[int],
    *,
    max_scan_size: int,
) -> list[OrderedDict[str, object]]:
    if not root.exists() or not known_offsets:
        return []
    encoded_offsets = [(value, struct.pack("<I", value)) for value in known_offsets if 0 <= value <= 0xFFFFFFFF]
    hits: list[OrderedDict[str, object]] = []
    exe_resolved = exe.resolve() if exe.exists() else exe
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            if path.resolve() == exe_resolved:
                continue
            size = path.stat().st_size
            if size > max_scan_size:
                continue
            blob = path.read_bytes()
        except OSError:
            continue
        for value, encoded in encoded_offsets:
            if blob.find(encoded) >= 0:
                hits.append(
                    OrderedDict(
                        [
                            ("file", _relative_display_path(root, path)),
                            ("offset", format_offset(value)),
                            ("usable", False),
                            ("reason", "non-yysls.exe hit; audit evidence only"),
                        ]
                    )
                )
    return hits


def _find_binpatch_exe_copies(root: Path, exe: Path) -> list[OrderedDict[str, object]]:
    try:
        exe_sha256 = sha256_file(exe)
    except OSError:
        return []
    copies: list[OrderedDict[str, object]] = []
    for path in root.rglob("yysls.exe"):
        try:
            if path.resolve() == exe.resolve():
                continue
            copied_hash = sha256_file(path)
        except OSError:
            continue
        copies.append(
            OrderedDict(
                [
                    ("file", _relative_display_path(root, path)),
                    ("sha256", copied_hash),
                    ("sameAsMainExe", copied_hash == exe_sha256),
                ]
            )
        )
    return copies


def _audit_pe_sections(exe: Path, pe: PEImage) -> tuple[list[OrderedDict[str, object]], OrderedDict[str, object]]:
    section_rows: list[OrderedDict[str, object]] = []
    high_entropy_sections: list[str] = []
    logic_sections_raw_zero = False
    for section in pe.sections:
        entropy = _section_entropy(exe, section)
        if section.name in {".text", ".rdata", ".data"} and section.virtual_size and section.raw_size == 0:
            logic_sections_raw_zero = True
        if entropy is not None and entropy >= 7.0 and section.raw_size >= 4096:
            high_entropy_sections.append(section.name)
        section_rows.append(
            OrderedDict(
                [
                    ("name", section.name),
                    ("virtualAddress", format_offset(section.virtual_address)),
                    ("virtualSize", section.virtual_size),
                    ("rawSize", section.raw_size),
                    ("readable", section.is_readable),
                    ("executable", section.is_executable),
                    ("entropy", round(entropy, 3) if entropy is not None else None),
                ]
            )
        )

    packed = logic_sections_raw_zero or bool(high_entropy_sections) or any(
        section.name.startswith((".UH", ".he")) for section in pe.sections
    )
    packed_evidence = OrderedDict(
        [
            ("status", "packed_or_shelled" if packed else "normal_pe"),
            ("logicSectionsRawSizeZero", logic_sections_raw_zero),
            ("highEntropySections", high_entropy_sections),
            ("unpackedImageAvailable", False),
            (
                "unpackedImageNote",
                "disk PE appears packed; high-confidence offline matching needs unpacked-image signatures"
                if packed
                else "disk PE sections are directly inspectable",
            ),
        ]
    )
    return section_rows, packed_evidence


def _section_entropy(exe: Path, section: PESection) -> float | None:
    if section.raw_size <= 0:
        return None
    try:
        with exe.open("rb") as handle:
            handle.seek(section.raw_pointer)
            data = handle.read(section.raw_size)
    except OSError:
        return None
    if not data:
        return None
    counts = Counter(data)
    total = len(data)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def _relative_display_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _normalize_signature(signature: StaticSignature | Mapping[str, object]) -> StaticSignature:
    if isinstance(signature, StaticSignature):
        return signature
    return StaticSignature.from_mapping(signature)


def _triplet_from_backend(previous_backend: Mapping[str, object], key: str) -> OffsetTriplet | None:
    value = previous_backend.get(key)
    if not isinstance(value, Mapping):
        return None
    return OffsetTriplet.from_mapping(value)


def _same_coordinates(left: OffsetTriplet, right: OffsetTriplet) -> bool:
    return left.x == right.x and left.y == right.y and left.z == right.z


def _read_dump_version_for_exe(exe_path: str | os.PathLike[str] | None) -> str:
    if not exe_path:
        return ""
    dump_config = Path(exe_path).with_name("dump.config")
    if not dump_config.exists():
        return ""
    return read_dump_config_version(dump_config)


def _infer_game_root(*exe_paths: str | os.PathLike[str] | None) -> Path | None:
    for exe_path in exe_paths:
        if not exe_path:
            continue
        path = Path(exe_path)
        parts = [part.lower() for part in path.parts]
        try:
            engine_index = parts.index("engine")
        except ValueError:
            continue
        if engine_index > 0:
            return Path(*path.parts[:engine_index])
    return None


def _latest_patch_publish_version(game_root: Path) -> Mapping[str, str] | None:
    log_dir = game_root / "LocalData" / "patch_log"
    if not log_dir.exists():
        return None
    best: dict[str, str] | None = None
    for path in log_dir.glob("*.txt"):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for match in CUR_VERSION_RE.finditer(text):
            candidate = {
                "stamp": match.group("stamp"),
                "major": match.group("major"),
                "minor": match.group("minor"),
            }
            if best is None or candidate["stamp"] > best["stamp"]:
                best = candidate
    return best


def _revision_from_package_files(
    win64r_exe: str | os.PathLike[str] | None,
    win64rh_exe: str | os.PathLike[str] | None,
    game_root: Path,
) -> str:
    candidates: list[Path] = []
    if win64r_exe:
        win64r_dir = Path(win64r_exe).parent
        candidates.extend([win64r_dir / "Built.version", win64r_dir / "dump.config"])
    candidates.extend(
        [
            game_root / "Engine" / "Binaries" / "Win64r" / "Built.version",
            game_root / "Engine" / "Binaries" / "Win64r" / "dump.config",
        ]
    )
    if win64rh_exe:
        win64rh_dir = Path(win64rh_exe).parent
        candidates.extend([win64rh_dir / "Built.version", win64rh_dir / "dump.config"])
    for path in candidates:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        match = REVISION_RE.search(text)
        if match:
            return match.group("revision")
    return ""


def sha256_file(path: str | os.PathLike[str]) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_signature_value(blob: bytes, offset: int, kind: str, pe: PEImage) -> int | None:
    if kind == "u32_rva":
        if offset + 4 > len(blob):
            return None
        return _read_u32(blob, offset)
    if kind == "u64_va":
        if offset + 8 > len(blob):
            return None
        va = _read_u64(blob, offset)
        if va < pe.image_base:
            return None
        return va - pe.image_base
    return None


def _choose_triplet_candidate(
    rule: PackageRule,
    pe: PEImage,
    candidates: Mapping[str, Sequence[int]],
    *,
    version_str: str = "",
) -> OffsetTriplet | None:
    valid_by_axis: dict[str, Counter[int]] = {}
    for axis in ("x", "y", "z"):
        valid_by_axis[axis] = Counter(
            value
            for value in candidates.get(axis, [])
            if _candidate_axis_value_is_valid(rule, pe, axis, value)
        )
    if not all(valid_by_axis[axis] for axis in ("x", "y", "z")):
        return None

    base_scores: Counter[int] = Counter()
    for axis, values in valid_by_axis.items():
        axis_delta = AXIS_STRUCT_OFFSETS[axis]
        for value, count in values.items():
            base_scores[value - axis_delta] += count

    for base, _score in base_scores.most_common():
        triplet_values = {
            axis: base + axis_delta
            for axis, axis_delta in AXIS_STRUCT_OFFSETS.items()
        }
        if all(triplet_values[axis] in valid_by_axis[axis] for axis in ("x", "y", "z")):
            return OffsetTriplet(
                x=triplet_values["x"],
                y=triplet_values["y"],
                z=triplet_values["z"],
                version_str=version_str,
            )
    return None


def _choose_candidate(rule: PackageRule, pe: PEImage, axis: str, candidates: Sequence[int]) -> int | None:
    valid = [value for value in candidates if _candidate_axis_value_is_valid(rule, pe, axis, value)]
    if not valid:
        return None
    return Counter(valid).most_common(1)[0][0]


def _candidate_axis_value_is_valid(rule: PackageRule, pe: PEImage, axis: str, value: int) -> bool:
    expected_suffix = rule.axis_suffix_nibbles[axis]
    return (value & 0xF) == expected_suffix and pe.readable_data_section_for_rva(value) is not None


def _find_all(blob: bytes, needle: bytes) -> Iterable[int]:
    start = 0
    while True:
        index = blob.find(needle, start)
        if index < 0:
            break
        yield index
        start = index + 1


def _longest_anchor(pattern: Sequence[int | None]) -> tuple[int, bytes]:
    best_start = 0
    best = bytearray()
    current_start = 0
    current = bytearray()
    for index, value in enumerate(pattern):
        if value is None:
            if len(current) > len(best):
                best_start = current_start
                best = current
            current = bytearray()
            current_start = index + 1
            continue
        current.append(value)
    if len(current) > len(best):
        best_start = current_start
        best = current
    return best_start, bytes(best)


def _brute_force_pattern_offsets(blob: bytes, pattern: Sequence[int | None]) -> list[int]:
    return [
        offset
        for offset in range(0, len(blob) - len(pattern) + 1)
        if _pattern_matches_at(blob, pattern, offset)
    ]


def _pattern_matches_at(blob: bytes, pattern: Sequence[int | None], offset: int) -> bool:
    for index, expected in enumerate(pattern):
        if expected is not None and blob[offset + index] != expected:
            return False
    return True


def _read_u16(blob: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<H", blob, offset)[0]


def _read_u32(blob: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<I", blob, offset)[0]


def _read_u64(blob: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<Q", blob, offset)[0]


def _validate_running_process_windows(exe_path: Path, triplet: OffsetTriplet, *, pid: int | None = None) -> RuntimeValidation:
    pids = [pid] if pid else _find_process_ids_by_path(exe_path)
    if not pids:
        return RuntimeValidation(ok=False, notes=[f"no running process found for {exe_path}"])

    notes: list[str] = []
    for candidate_pid in pids:
        process = _open_process(candidate_pid)
        if not process:
            notes.append(f"could not open process {candidate_pid}")
            continue
        try:
            module_base = _main_module_base(candidate_pid, exe_path)
            if module_base is None:
                notes.append(f"could not resolve module base for process {candidate_pid}")
                continue
            values = {}
            for axis in ("x", "y", "z"):
                raw = _read_process_memory(process, module_base + triplet.value_for_axis(axis), 4)
                values[axis] = struct.unpack("<f", raw)[0]
            validation = validate_runtime_values(values)
            validation.notes.insert(0, f"pid={candidate_pid} moduleBase={format_offset(module_base)}")
            return validation
        finally:
            ctypes.windll.kernel32.CloseHandle(process)
    return RuntimeValidation(ok=False, notes=notes)


def _open_process(pid: int):  # pragma: no cover - Windows integration helper
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    PROCESS_VM_READ = 0x0010
    return ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_VM_READ, False, pid)


def _find_process_ids_by_path(exe_path: Path) -> list[int]:  # pragma: no cover - Windows integration helper
    expected = str(exe_path.resolve()).casefold()
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    TH32CS_SNAPPROCESS = 0x00000002
    INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [
            ("dwSize", ctypes.c_ulong),
            ("cntUsage", ctypes.c_ulong),
            ("th32ProcessID", ctypes.c_ulong),
            ("th32DefaultHeapID", ctypes.c_void_p),
            ("th32ModuleID", ctypes.c_ulong),
            ("cntThreads", ctypes.c_ulong),
            ("th32ParentProcessID", ctypes.c_ulong),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", ctypes.c_ulong),
            ("szExeFile", ctypes.c_wchar * 260),
        ]

    kernel32 = ctypes.windll.kernel32
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snapshot == INVALID_HANDLE_VALUE:
        return []

    results: list[int] = []
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(entry)
        has_entry = kernel32.Process32FirstW(snapshot, ctypes.byref(entry))
        while has_entry:
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, entry.th32ProcessID)
            if handle:
                try:
                    resolved = _query_full_process_image_name(handle)
                    if resolved and resolved.casefold() == expected:
                        results.append(int(entry.th32ProcessID))
                finally:
                    kernel32.CloseHandle(handle)
            has_entry = kernel32.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel32.CloseHandle(snapshot)
    return results


def _query_full_process_image_name(handle) -> str | None:  # pragma: no cover - Windows integration helper
    size = ctypes.c_ulong(32768)
    buffer = ctypes.create_unicode_buffer(size.value)
    ok = ctypes.windll.kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size))
    if not ok:
        return None
    return buffer.value


def _main_module_base(pid: int, exe_path: Path) -> int | None:  # pragma: no cover - Windows integration helper
    TH32CS_SNAPMODULE = 0x00000008
    TH32CS_SNAPMODULE32 = 0x00000010
    INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

    class MODULEENTRY32W(ctypes.Structure):
        _fields_ = [
            ("dwSize", ctypes.c_ulong),
            ("th32ModuleID", ctypes.c_ulong),
            ("th32ProcessID", ctypes.c_ulong),
            ("GlblcntUsage", ctypes.c_ulong),
            ("ProccntUsage", ctypes.c_ulong),
            ("modBaseAddr", ctypes.c_void_p),
            ("modBaseSize", ctypes.c_ulong),
            ("hModule", ctypes.c_void_p),
            ("szModule", ctypes.c_wchar * 256),
            ("szExePath", ctypes.c_wchar * 260),
        ]

    expected = str(exe_path.resolve()).casefold()
    kernel32 = ctypes.windll.kernel32
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid)
    if snapshot == INVALID_HANDLE_VALUE:
        return None
    try:
        entry = MODULEENTRY32W()
        entry.dwSize = ctypes.sizeof(entry)
        has_entry = kernel32.Module32FirstW(snapshot, ctypes.byref(entry))
        while has_entry:
            if entry.szExePath.casefold() == expected:
                return int(entry.modBaseAddr)
            has_entry = kernel32.Module32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel32.CloseHandle(snapshot)
    return None


def _read_process_memory(process, address: int, size: int) -> bytes:  # pragma: no cover - Windows integration helper
    buffer = ctypes.create_string_buffer(size)
    bytes_read = ctypes.c_size_t()
    ok = ctypes.windll.kernel32.ReadProcessMemory(
        process,
        ctypes.c_void_p(address),
        buffer,
        size,
        ctypes.byref(bytes_read),
    )
    if not ok or bytes_read.value != size:
        raise OSError(f"ReadProcessMemory failed at {format_offset(address)}")
    return buffer.raw


if __name__ == "__main__":
    raise SystemExit(main())
