import json
import struct
import tempfile
import unittest
from pathlib import Path

from h72_offset_finder import (
    OffsetTriplet,
    PEImage,
    PESection,
    PACKAGE_RULES,
    ScanResult,
    audit_package_directory,
    build_backend_h72_map,
    build_h72_map,
    determine_reason,
    discover_cur_version,
    learn_signatures,
    parse_offset_int,
    parse_pe,
    read_dump_config_version,
    scan_package,
    scan_with_signatures,
    update_sample_library,
    validate_triplet,
    write_scan_report,
)


READABLE_DATA = 0x40000040


def sample_pe(data_start=0x7000000, data_size=0x200000):
    return PEImage(
        path=Path("sample.exe"),
        image_base=0x140000000,
        sections=[
            PESection(".text", 0x1000, 0x2000, 0x400, 0x2000, 0x60000020),
            PESection(".data", data_start, data_size, 0x2400, data_size, READABLE_DATA),
        ],
    )


def write_fake_pe(path, data_start, data_size, text_payload):
    dos = bytearray(0x80)
    dos[0:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, 0x80)

    file_header = struct.pack(
        "<HHIIIHH",
        0x8664,
        2,
        0,
        0,
        0,
        0xF0,
        0x0022,
    )

    optional = bytearray(0xF0)
    struct.pack_into("<H", optional, 0, 0x20B)
    struct.pack_into("<Q", optional, 24, 0x140000000)

    text_raw_pointer = 0x200
    text_raw_size = 0x200
    data_raw_pointer = 0x400
    data_raw_size = 0x200
    text = struct.pack(
        "<8sIIIIIIHHI",
        b".text\0\0\0",
        0x1000,
        0x1000,
        text_raw_size,
        text_raw_pointer,
        0,
        0,
        0,
        0,
        0x60000020,
    )
    data = struct.pack(
        "<8sIIIIIIHHI",
        b".data\0\0\0",
        data_size,
        data_start,
        data_raw_size,
        data_raw_pointer,
        0,
        0,
        0,
        0,
        READABLE_DATA,
    )

    blob = dos + b"PE\0\0" + file_header + optional + text + data
    if len(blob) < text_raw_pointer:
        blob.extend(b"\0" * (text_raw_pointer - len(blob)))

    text_bytes = bytearray(text_raw_size)
    text_bytes[: len(text_payload)] = text_payload
    blob.extend(text_bytes)
    if len(blob) < data_raw_pointer:
        blob.extend(b"\0" * (data_raw_pointer - len(blob)))
    blob.extend(b"\0" * data_raw_size)
    path.write_bytes(blob)


class ValidationTests(unittest.TestCase):
    def test_win64r_accepts_c_4_8_suffix_nibbles(self):
        rule = PACKAGE_RULES["Win64r"]
        report = validate_triplet(
            rule,
            sample_pe(),
            OffsetTriplet(x=0x70DB15C, y=0x70DB154, z=0x70DB158, version_str="r"),
        )
        self.assertTrue(report.ok, report.errors)

        swapped = validate_triplet(
            rule,
            sample_pe(),
            OffsetTriplet(x=0x70DB144, y=0x70DB148, z=0x70DB14C, version_str="r"),
        )
        self.assertFalse(swapped.ok)
        self.assertIn("x suffix nibble must be 0xC", "\n".join(swapped.errors))

    def test_win64rh_accepts_c_4_8_suffix_nibbles_from_old_and_current_offsets(self):
        rule = PACKAGE_RULES["Win64rh"]
        old_report = validate_triplet(
            rule,
            sample_pe(),
            OffsetTriplet(x=0x708210C, y=0x7082104, z=0x7082108, version_str="rh"),
        )
        self.assertTrue(old_report.ok, old_report.errors)

        current_report = validate_triplet(
            rule,
            sample_pe(),
            OffsetTriplet(x=0x70DB14C, y=0x70DB144, z=0x70DB148, version_str="rh"),
        )
        self.assertTrue(current_report.ok, current_report.errors)

    def test_triplet_must_be_one_coordinate_struct(self):
        rule = PACKAGE_RULES["Win64r"]
        valid = validate_triplet(
            rule,
            sample_pe(),
            OffsetTriplet(x=0x70DB14C, y=0x70DB144, z=0x70DB148, version_str="r"),
        )
        self.assertTrue(valid.ok, valid.errors)

        same_suffix_wrong_block = validate_triplet(
            rule,
            sample_pe(),
            OffsetTriplet(x=0x70DB14C, y=0x70DB154, z=0x70DB148, version_str="bad"),
        )
        self.assertFalse(same_suffix_wrong_block.ok)
        self.assertIn(
            "offsets must share one coordinate struct",
            "\n".join(same_suffix_wrong_block.errors),
        )

    def test_both_packages_reject_wrong_suffix_nibbles(self):
        triplet = OffsetTriplet(x=0x70DB14D, y=0x70DB145, z=0x70DB149, version_str="bad")
        for package in ("Win64r", "Win64rh"):
            report = validate_triplet(PACKAGE_RULES[package], sample_pe(), triplet)
            self.assertFalse(report.ok)
            errors = "\n".join(report.errors)
            self.assertIn("x suffix nibble must be 0xC", errors)
            self.assertIn("y suffix nibble must be 0x4", errors)
            self.assertIn("z suffix nibble must be 0x8", errors)

    def test_seed_tail_fields_do_not_override_fixed_suffix_nibble_rule(self):
        seed_entry = {
            "versionStr": "202605182004_r58091",
            "tails": {"x": "0x0D", "y": "0x05", "z": "0x09"},
            "offsets": {"x": "0x70DB14C", "y": "0x70DB144", "z": "0x70DB148"},
        }

        with tempfile.TemporaryDirectory() as tmp:
            exe = Path(tmp) / "rh.exe"
            write_fake_pe(exe, 0x7000000, 0x200000, b"payload")
            result = scan_package(exe, "Win64rh", seed_entry)

        self.assertEqual("medium", result.confidence)
        self.assertEqual(0x70DB14C, result.triplet.x)

    def test_seed_offset_version_does_not_override_current_dump_version(self):
        seed_entry = {
            "versionStr": "202605182004_r58091",
            "offsets": {
                "x": "0x70DB14C",
                "y": "0x70DB144",
                "z": "0x70DB148",
                "versionStr": "202605182004_r58091",
            },
        }

        with tempfile.TemporaryDirectory() as tmp:
            exe = Path(tmp) / "rh.exe"
            write_fake_pe(exe, 0x70D3000, 0x200000, b"payload")
            result = scan_package(exe, "Win64rh", seed_entry, version_str="202605191110_r58107")

        self.assertEqual("medium", result.confidence)
        self.assertEqual("202605191110_r58107", result.triplet.version_str)

    def test_scan_package_rebases_seed_offsets_when_data_section_moves(self):
        seed_entry = {
            "versionStr": "202605182004_r58091",
            "dataSectionVirtualAddress": "0x70D4000",
            "offsets": {
                "x": "0x70DB14C",
                "y": "0x70DB144",
                "z": "0x70DB148",
                "versionStr": "202605182004_r58091",
            },
        }

        with tempfile.TemporaryDirectory() as tmp:
            exe = Path(tmp) / "rh.exe"
            write_fake_pe(exe, 0x70D3000, 0x200000, b"payload")
            result = scan_package(exe, "Win64rh", seed_entry, version_str="202605191110_r58107")

        self.assertEqual("medium", result.confidence)
        self.assertEqual(0x70DA14C, result.triplet.x)
        self.assertEqual(0x70DA144, result.triplet.y)
        self.assertEqual(0x70DA148, result.triplet.z)
        self.assertIn("rebased seed offsets", "\n".join(result.notes))

    def test_rejects_offsets_outside_readable_data_section(self):
        report = validate_triplet(
            PACKAGE_RULES["Win64r"],
            sample_pe(),
            OffsetTriplet(x=0x600004C, y=0x6000044, z=0x6000048, version_str="bad"),
        )
        self.assertFalse(report.ok)
        self.assertIn("x offset 0x600004C is not in readable .data", "\n".join(report.errors))

    def test_build_h72_map_duplicates_fast_fields(self):
        win64r = OffsetTriplet(x=0x70DB14C, y=0x70DB144, z=0x70DB148, version_str="r_ver")
        win64rh = OffsetTriplet(x=0x708210C, y=0x7082104, z=0x7082108, version_str="rh_ver")
        result = build_h72_map(win64r, win64rh)

        self.assertEqual(["offSet", "greyOffSet", "offSetFast", "greyOffSetFast"], list(result))
        self.assertEqual(result["offSet"], result["offSetFast"])
        self.assertEqual(result["greyOffSet"], result["greyOffSetFast"])
        self.assertEqual(result["offSet"]["x"], "0x70DB14C")
        self.assertEqual(result["offSet"]["y"], "0x70DB144")
        self.assertEqual(result["offSet"]["z"], "0x70DB148")
        self.assertEqual(result["greyOffSet"]["x"], "0x708210C")

    def test_parse_offset_int_accepts_hex_decimal_and_json_numbers(self):
        self.assertEqual(0x70DB14C, parse_offset_int("0x70DB14C"))
        self.assertEqual(118337868, parse_offset_int("118337868"))
        self.assertEqual(0x4C, parse_offset_int(0x4C))


class PETests(unittest.TestCase):
    def test_parse_pe_reads_section_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            exe = Path(tmp) / "fake.exe"
            write_fake_pe(exe, 0x7000000, 0x3000, b"payload")

            pe = parse_pe(exe)

        self.assertEqual(pe.image_base, 0x140000000)
        self.assertEqual([section.name for section in pe.sections], [".text", ".data"])
        self.assertEqual(pe.sections[1].virtual_address, 0x7000000)


class SignatureScanTests(unittest.TestCase):
    def test_static_signature_scan_derives_new_offsets_per_package(self):
        old_triplet = OffsetTriplet(x=0x700004C, y=0x7000044, z=0x7000048, version_str="old")
        new_triplet = OffsetTriplet(x=0x700105C, y=0x7001054, z=0x7001058, version_str="new")
        rule = PACKAGE_RULES["Win64r"]

        old_text = b"xx" + struct.pack("<I", old_triplet.y) + b"yy" + struct.pack("<I", old_triplet.z)
        old_text += b"zz" + struct.pack("<I", old_triplet.x) + b"done"
        new_text = b"xx" + struct.pack("<I", new_triplet.y) + b"yy" + struct.pack("<I", new_triplet.z)
        new_text += b"zz" + struct.pack("<I", new_triplet.x) + b"done"

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            old_exe = tmp_path / "old.exe"
            new_exe = tmp_path / "new.exe"
            write_fake_pe(old_exe, 0x7000000, 0x3000, old_text)
            write_fake_pe(new_exe, 0x7000000, 0x3000, new_text)

            signatures = learn_signatures(old_exe, rule, old_triplet, context=2, limit_per_axis=1)
            result = scan_with_signatures(new_exe, rule, signatures, version_str="new")

        self.assertEqual("high", result.confidence)
        self.assertEqual([], result.validation.errors)
        self.assertEqual(new_triplet, result.triplet)

    def test_static_scan_does_not_mix_win64r_signature_into_win64rh(self):
        old_triplet = OffsetTriplet(x=0x700004C, y=0x7000044, z=0x7000048, version_str="old")
        rule = PACKAGE_RULES["Win64r"]
        rh_rule = PACKAGE_RULES["Win64rh"]
        old_text = b"a" + struct.pack("<I", old_triplet.x) + b"b" + struct.pack("<I", old_triplet.y)
        old_text += b"c" + struct.pack("<I", old_triplet.z) + b"d"

        with tempfile.TemporaryDirectory() as tmp:
            exe = Path(tmp) / "same.exe"
            write_fake_pe(exe, 0x7000000, 0x3000, old_text)
            signatures = learn_signatures(exe, rule, old_triplet, context=1, limit_per_axis=1)
            result = scan_with_signatures(exe, rh_rule, signatures, version_str="rh")

        self.assertEqual("low", result.confidence)
        self.assertIsNone(result.triplet)
        self.assertIn("signature package Win64r does not match Win64rh", result.notes)

    def test_static_signature_scan_filters_candidates_by_coordinate_struct(self):
        valid_triplet = OffsetTriplet(x=0x700104C, y=0x7001044, z=0x7001048, version_str="new")
        invalid_x = 0x700204C
        rule = PACKAGE_RULES["Win64r"]

        signatures = [
            {
                "package": "Win64r",
                "axis": "x",
                "kind": "u32_rva",
                "pattern": "58 ?? ?? ?? ?? 58",
                "valueOffset": 1,
                "sourceFileOffset": 1,
                "context": 1,
            },
            {
                "package": "Win64r",
                "axis": "y",
                "kind": "u32_rva",
                "pattern": "59 ?? ?? ?? ?? 59",
                "valueOffset": 1,
                "sourceFileOffset": 1,
                "context": 1,
            },
            {
                "package": "Win64r",
                "axis": "z",
                "kind": "u32_rva",
                "pattern": "5A ?? ?? ?? ?? 5A",
                "valueOffset": 1,
                "sourceFileOffset": 1,
                "context": 1,
            },
        ]
        text = b"X" + struct.pack("<I", invalid_x) + b"X"
        text += b"X" + struct.pack("<I", valid_triplet.x) + b"X"
        text += b"Y" + struct.pack("<I", valid_triplet.y) + b"Y"
        text += b"Z" + struct.pack("<I", valid_triplet.z) + b"Z"

        with tempfile.TemporaryDirectory() as tmp:
            exe = Path(tmp) / "new.exe"
            write_fake_pe(exe, 0x7000000, 0x4000, text)
            result = scan_with_signatures(exe, rule, signatures, version_str="new")

        self.assertEqual("high", result.confidence)
        self.assertEqual(valid_triplet, result.triplet)


class SampleLibraryTests(unittest.TestCase):
    def test_update_sample_library_records_metadata_and_history(self):
        triplet = OffsetTriplet(x=0x70DB14C, y=0x70DB144, z=0x70DB148, version_str="202605182004_r58091")

        data = update_sample_library(
            {"packages": {}},
            "Win64rh",
            triplet,
            version_str="202605182004_r58091",
            cur_version="1.29.30.58091",
            exe_sha256="abc123",
            source="runtime_readonly",
            confidence="high",
            signatures=[],
        )

        entry = data["packages"]["Win64rh"]
        self.assertEqual("Win64rh", entry["package"])
        self.assertEqual("202605182004_r58091", entry["versionStr"])
        self.assertEqual("1.29.30.58091", entry["curVersion"])
        self.assertEqual("abc123", entry["exeSha256"])
        self.assertEqual("runtime_readonly", entry["source"])
        self.assertEqual("high", entry["confidence"])
        self.assertEqual("0x70DB14C", entry["offsets"]["x"])
        self.assertNotIn("tails", entry)
        self.assertEqual(1, len(entry["samples"]))
        self.assertEqual("Win64rh", entry["samples"][0]["package"])


class PackageAuditTests(unittest.TestCase):
    def test_package_audit_treats_other_files_as_non_coordinate_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fake_pe(root / "yysls.exe", 0x7000000, 0x3000, b"payload")
            (root / "dump.config").write_text("h72\nmd5\n202605182004_r58091\n", encoding="utf-8")
            (root / "Built.version").write_text("2026-05-18/r58091\n", encoding="utf-8")
            nested = root / "webviewsupport"
            nested.mkdir()
            (nested / "libcef.dll").write_bytes(b"noise" + struct.pack("<I", 0x708210C))

            audit = audit_package_directory(root, package="Win64rh", known_offsets=[0x708210C])

        self.assertEqual("202605182004_r58091", audit["dumpVersion"])
        self.assertEqual("2026-05-18/r58091", audit["builtVersion"])
        self.assertEqual([], audit["symbolFiles"])
        self.assertEqual(["yysls.exe"], audit["usableCoordinateSources"])
        self.assertEqual("webviewsupport\\libcef.dll", audit["knownOffsetHits"][0]["file"])
        self.assertFalse(audit["knownOffsetHits"][0]["usable"])


class CLISchemaTests(unittest.TestCase):
    def test_h72_json_is_serializable(self):
        result = build_h72_map(
            OffsetTriplet(x=0x70DB14C, y=0x70DB144, z=0x70DB148, version_str="r_ver"),
            OffsetTriplet(x=0x708210C, y=0x7082104, z=0x7082108, version_str="rh_ver"),
        )
        loaded = json.loads(json.dumps(result))
        self.assertEqual("r_ver", loaded["offSet"]["versionStr"])
        self.assertEqual("rh_ver", loaded["greyOffSetFast"]["versionStr"])

    def test_read_dump_config_version_uses_third_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            dump_config = Path(tmp) / "dump.config"
            dump_config.write_text("h72\nmd5-value\n202605182004_r58091\n", encoding="utf-8")

            version = read_dump_config_version(dump_config)

        self.assertEqual("202605182004_r58091", version)

    def test_backend_h72_map_includes_cur_version_reason_and_fast_fields(self):
        win64r = OffsetTriplet(x=0x70DB14C, y=0x70DB144, z=0x70DB148, version_str="r_ver")
        win64rh = OffsetTriplet(x=0x70DB14C, y=0x70DB144, z=0x70DB148, version_str="rh_ver")

        result = build_backend_h72_map(win64r, win64rh, cur_version="1.29.30.57817", reason="RH更新")

        self.assertEqual("1.29.30.57817", result["curVersion"])
        self.assertEqual("RH更新", result["reason"])
        self.assertEqual(result["offSet"], result["offSetFast"])
        self.assertEqual(result["greyOffSet"], result["greyOffSetFast"])
        self.assertEqual("r_ver", result["offSet"]["versionStr"])
        self.assertEqual("rh_ver", result["greyOffSet"]["versionStr"])

    def test_determine_reason_compares_only_coordinates(self):
        previous = build_backend_h72_map(
            OffsetTriplet(x=0x100C, y=0x1004, z=0x1008, version_str="old_r"),
            OffsetTriplet(x=0x200C, y=0x2004, z=0x2008, version_str="old_rh"),
            cur_version="old",
            reason="W更新",
        )

        self.assertEqual(
            "W更新",
            determine_reason(
                previous,
                OffsetTriplet(x=0x100C, y=0x1004, z=0x1008, version_str="new_r"),
                OffsetTriplet(x=0x200C, y=0x2004, z=0x2008, version_str="new_rh"),
            ),
        )
        self.assertEqual(
            "R更新",
            determine_reason(
                previous,
                OffsetTriplet(x=0x300C, y=0x3004, z=0x3008, version_str="new_r"),
                OffsetTriplet(x=0x200C, y=0x2004, z=0x2008, version_str="new_rh"),
            ),
        )
        self.assertEqual(
            "RH更新",
            determine_reason(
                previous,
                OffsetTriplet(x=0x100C, y=0x1004, z=0x1008, version_str="new_r"),
                OffsetTriplet(x=0x400C, y=0x4004, z=0x4008, version_str="new_rh"),
            ),
        )
        self.assertEqual(
            "R&RH更新",
            determine_reason(
                previous,
                OffsetTriplet(x=0x300C, y=0x3004, z=0x3008, version_str="new_r"),
                OffsetTriplet(x=0x400C, y=0x4004, z=0x4008, version_str="new_rh"),
            ),
        )

    def test_scan_report_records_publishable_state_and_package_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exe_r = root / "r.exe"
            exe_rh = root / "rh.exe"
            exe_r.write_bytes(b"r")
            exe_rh.write_bytes(b"rh")
            report_path = write_scan_report(
                root / "reports",
                cur_version="1.29.30.58091",
                package_paths={"Win64r": str(exe_r), "Win64rh": str(exe_rh)},
                results={
                    "Win64r": ScanResult(
                        package="Win64r",
                        confidence="high",
                        triplet=OffsetTriplet(x=0x100C, y=0x1004, z=0x1008, version_str="r"),
                    ),
                    "Win64rh": ScanResult(
                        package="Win64rh",
                        confidence="medium",
                        triplet=OffsetTriplet(x=0x200C, y=0x2004, z=0x2008, version_str="rh"),
                    ),
                },
                h72_map={"offSet": {}, "greyOffSet": {}},
                current_backend_path=root / "h72_current_backend.json",
                package_audits={
                    "Win64r": {"packedEvidence": {"status": "packed_or_shelled"}},
                    "Win64rh": {"packedEvidence": {"status": "normal_pe"}},
                },
            )

            payload = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertFalse(payload["publishable"])
        self.assertEqual("medium", payload["packages"]["Win64rh"]["confidence"])
        self.assertEqual(
            "packed_or_shelled",
            payload["packages"]["Win64r"]["audit"]["packedEvidence"]["status"],
        )

    def test_discover_cur_version_from_patch_log_and_win64r_built_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            win64r = root / "Engine" / "Binaries" / "Win64r"
            win64rh = root / "Engine" / "Binaries" / "Win64rh"
            log_dir = root / "LocalData" / "patch_log"
            win64r.mkdir(parents=True)
            win64rh.mkdir(parents=True)
            log_dir.mkdir(parents=True)
            (win64r / "Built.version").write_text("2026-05-19/r58124\n", encoding="utf-8")
            (win64rh / "Built.version").write_text("2026-05-19/r58107\n", encoding="utf-8")
            (log_dir / "old.txt").write_text(
                "version: publish.win64.o.formal.usual.20260519183229.29.33\n",
                encoding="utf-8",
            )
            (log_dir / "current.txt").write_text(
                "-- version=publish.win64.o.formal.usual.20260520025636.29.35\n",
                encoding="utf-8",
            )
            (log_dir / "bg.txt").write_text(
                "-- version=stable.win64.o.bg_formal.usual.20260520235959.28.47\n",
                encoding="utf-8",
            )

            cur_version = discover_cur_version(
                game_root=root,
                win64r_exe=win64r / "yysls.exe",
                win64rh_exe=win64rh / "yysls.exe",
            )

        self.assertEqual("1.29.35.58124", cur_version)


if __name__ == "__main__":
    unittest.main()
