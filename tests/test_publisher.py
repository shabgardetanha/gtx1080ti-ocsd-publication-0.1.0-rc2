"""Hardware-independent tests for the exact release publisher source.

These tests use only Python's standard library and never access /dev/mem,
NVIDIA hardware, IPMI, systemd, containers, VMs, or network services.
"""
from __future__ import annotations

import importlib.util
import json
import os
import struct
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SOURCE = Path(__file__).resolve().parents[1] / "src" / "gen9_t4_ocsd.py"
SPEC = importlib.util.spec_from_file_location("publisher_under_test", SOURCE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {SOURCE}")
PUBLISHER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PUBLISHER)


class PublisherProtocolTests(unittest.TestCase):
    ADDRESS = 0x791F4000

    @staticmethod
    def make_header(address: int, count: int = 2) -> bytes:
        header = bytearray(64)
        header[0] = 2
        struct.pack_into("<H", header, 4, 0x4000)
        header[8] = 102
        header[12] = PUBLISHER.RECORD_SIZE
        struct.pack_into("<I", header, 16, address + 64)
        header[32] = 5
        header[56] = count
        struct.pack_into("<I", header, 60, PUBLISHER.checksum_header(header))
        return bytes(header)

    @staticmethod
    def put_native_record(memory: bytearray, index: int, bus: int) -> bytes:
        record = bytearray(64)
        record[0] = 1
        struct.pack_into("<I", record, 4, bus)
        struct.pack_into("<I", record, 8, 0)
        words = struct.unpack_from("<15I", record, 0)
        struct.pack_into("<I", record, 60, (-sum(words)) & 0xFFFFFFFF)
        start = 64 + index * PUBLISHER.RECORD_SIZE
        memory[start:start + 64] = record
        return bytes(record)

    def test_header_checksum_and_validation(self):
        header = self.make_header(self.ADDRESS)
        self.assertEqual(
            struct.unpack_from("<I", header, 60)[0],
            PUBLISHER.checksum_header(header),
        )
        PUBLISHER.validate_header(header, self.ADDRESS)

    def test_header_count_update_recalculates_checksum(self):
        original = self.make_header(self.ADDRESS, 2)
        active = PUBLISHER.header_with_count(original, 3)
        self.assertEqual(active[56], 3)
        PUBLISHER.validate_header(active, self.ADDRESS)
        self.assertEqual(active[:56], original[:56])

    def test_header_rejects_bad_checksum(self):
        header = bytearray(self.make_header(self.ADDRESS))
        header[60] ^= 0x01
        with self.assertRaisesRegex(ValueError, "checksum"):
            PUBLISHER.validate_header(bytes(header), self.ADDRESS)

    def test_header_rejects_wrong_allocation_address(self):
        with self.assertRaises(ValueError):
            PUBLISHER.validate_header(self.make_header(self.ADDRESS), self.ADDRESS + 0x1000)

    def test_native_headers_accept_observed_bus_mapping(self):
        memory = bytearray(0x4000)
        self.put_native_record(memory, 0, 4)
        self.put_native_record(memory, 1, 3)
        PUBLISHER.validate_native_headers(memory)

    def test_native_headers_reject_unexpected_bus(self):
        memory = bytearray(0x4000)
        self.put_native_record(memory, 0, 4)
        self.put_native_record(memory, 1, 2)
        with self.assertRaisesRegex(ValueError, "native OCSD"):
            PUBLISHER.validate_native_headers(memory)

    def test_record_round_trip_at_representative_temperatures(self):
        for temperature in (0, 48, 49, 64, 85, 100):
            with self.subTest(temperature=temperature):
                record = PUBLISHER.make_record(temperature, 2030)
                self.assertTrue(PUBLISHER.owned_record(record))
                self.assertEqual(record[84], temperature)
                self.assertEqual(struct.unpack_from("<H", record, 88)[0], 2030)

    def test_record_rejects_invalid_temperature_and_counter(self):
        for temp in (-1, 101):
            with self.subTest(temp=temp), self.assertRaises(ValueError):
                PUBLISHER.make_record(temp, 0)
        for counter in (-1, 65536):
            with self.subTest(counter=counter), self.assertRaises(ValueError):
                PUBLISHER.make_record(48, counter)

    def test_owned_record_rejects_corruption(self):
        record = bytearray(PUBLISHER.make_record(48, 7))
        record[84] = 49  # breaks the checksum/record equivalence
        self.assertFalse(PUBLISHER.owned_record(bytes(record)))

    def test_owned_record_rejects_wrong_length(self):
        self.assertFalse(PUBLISHER.owned_record(b"short"))

    def test_ilo_parser_accepts_numeric_reading(self):
        text = "Sensor ID : 22-PCI 2\nSensor Reading : 64 degrees C\nStatus : ok\n"
        self.assertEqual(PUBLISHER.parse_ilo_temperature(text), 64)

    def test_ilo_parser_rejects_disabled_or_unavailable_reading(self):
        text = "Sensor Reading : Disabled\nStatus : Not Available\n"
        self.assertIsNone(PUBLISHER.parse_ilo_temperature(text))

    def test_gpu_temperature_accepts_case_insensitive_bdf(self):
        output = b"00000000:0b:00.0, 49\n"
        with mock.patch.object(PUBLISHER.subprocess, "check_output", return_value=output):
            self.assertEqual(PUBLISHER.gpu_temperature(), 49)

    def test_gpu_temperature_rejects_wrong_bdf(self):
        output = b"00000000:0c:00.0, 49\n"
        with mock.patch.object(PUBLISHER.subprocess, "check_output", return_value=output):
            with self.assertRaisesRegex(ValueError, "PCI identity"):
                PUBLISHER.gpu_temperature()

    def test_gpu_temperature_rejects_out_of_range_value(self):
        output = b"00000000:0b:00.0, 101\n"
        with mock.patch.object(PUBLISHER.subprocess, "check_output", return_value=output):
            with self.assertRaisesRegex(ValueError, "outside accepted"):
                PUBLISHER.gpu_temperature()

    def test_discover_ocsd_finds_unique_type229_allocation(self):
        with tempfile.TemporaryDirectory() as tmp:
            entry = Path(tmp) / "229-0"
            entry.mkdir()
            raw = bytearray(20)
            raw[0] = 229
            raw[1] = 20
            raw[4:8] = b"$OCS"
            struct.pack_into("<QI", raw, 8, self.ADDRESS, 0x4000)
            (entry / "raw").write_bytes(raw)
            self.assertEqual(PUBLISHER.discover_ocsd(Path(tmp)), self.ADDRESS)

    def test_discover_ocsd_rejects_duplicate_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            entry = Path(tmp) / "229-0"
            entry.mkdir()
            raw = bytearray(36)
            raw[0] = 229
            raw[1] = 36
            raw[4:8] = b"$OCS"
            struct.pack_into("<QI", raw, 8, self.ADDRESS, 0x4000)
            raw[20:24] = b"$OCS"
            struct.pack_into("<QI", raw, 24, self.ADDRESS + 0x4000, 0x4000)
            (entry / "raw").write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "unique 16 KiB"):
                PUBLISHER.discover_ocsd(Path(tmp))

    def test_publish_record_updates_only_dedicated_slot(self):
        memory = bytearray(0x4000)
        original = self.make_header(self.ADDRESS, 2)
        active = PUBLISHER.header_with_count(original, 3)
        memory[:64] = active
        native_1 = self.put_native_record(memory, 0, 4)
        native_2 = self.put_native_record(memory, 1, 3)
        next_counter = PUBLISHER.publish_record(memory, active, 8, 49)
        self.assertEqual(next_counter, 9)
        record = bytes(memory[PUBLISHER.RECORD_OFFSET:PUBLISHER.RECORD_OFFSET + PUBLISHER.RECORD_SIZE])
        self.assertTrue(PUBLISHER.owned_record(record))
        self.assertEqual(record[84], 49)
        self.assertEqual(bytes(memory[64:128]), native_1)
        self.assertEqual(bytes(memory[224:288]), native_2)
        self.assertEqual(bytes(memory[:64]), active)

    def test_claim_creates_owned_record_without_mutating_native_records(self):
        memory = bytearray(0x4000)
        original = self.make_header(self.ADDRESS, 2)
        memory[:64] = original
        native_1 = self.put_native_record(memory, 0, 4)
        native_2 = self.put_native_record(memory, 1, 3)

        with tempfile.TemporaryDirectory() as tmp:
            old_state = PUBLISHER.STATE
            PUBLISHER.STATE = Path(tmp) / "ownership.json"
            try:
                with mock.patch.object(PUBLISHER, "gpu_temperature", return_value=49), \
                     mock.patch.object(PUBLISHER, "boot_id", return_value="test-boot"):
                    returned_original, active, counter = PUBLISHER.claim(memory, self.ADDRESS)
                self.assertEqual(returned_original, original)
                self.assertEqual(memory[56], 3)
                self.assertTrue(PUBLISHER.STATE.is_file())
                record = bytes(memory[PUBLISHER.RECORD_OFFSET:PUBLISHER.RECORD_OFFSET + PUBLISHER.RECORD_SIZE])
                self.assertTrue(PUBLISHER.owned_record(record))
                self.assertEqual(record[84], 49)
                self.assertEqual(bytes(memory[64:128]), native_1)
                self.assertEqual(bytes(memory[224:288]), native_2)
                self.assertEqual(active, bytes(memory[:64]))
            finally:
                PUBLISHER.STATE = old_state

    def test_restore_clears_only_owned_slot_after_three_cool_samples(self):
        memory = bytearray(0x4000)
        original = self.make_header(self.ADDRESS, 2)
        active = PUBLISHER.header_with_count(original, 3)
        memory[:64] = active
        self.put_native_record(memory, 0, 4)
        self.put_native_record(memory, 1, 3)
        memory[PUBLISHER.RECORD_OFFSET:PUBLISHER.RECORD_OFFSET + PUBLISHER.RECORD_SIZE] = PUBLISHER.make_record(48, 11)

        with tempfile.TemporaryDirectory() as tmp:
            old_state = PUBLISHER.STATE
            PUBLISHER.STATE = Path(tmp) / "ownership.json"
            PUBLISHER.STATE.write_text(json.dumps({"test": True}))
            try:
                with mock.patch.object(PUBLISHER, "gpu_temperature", return_value=48), \
                     mock.patch.object(PUBLISHER.time, "sleep", return_value=None):
                    PUBLISHER.restore(memory, original, active)
                self.assertEqual(bytes(memory[:64]), original)
                self.assertFalse(any(memory[PUBLISHER.RECORD_OFFSET:PUBLISHER.RECORD_OFFSET + PUBLISHER.RECORD_SIZE]))
                self.assertFalse(PUBLISHER.STATE.exists())
            finally:
                PUBLISHER.STATE = old_state

    def test_claim_publishes_fail_high_when_gpu_telemetry_fails(self):
        memory = bytearray(0x4000)
        original = self.make_header(self.ADDRESS, 2)
        memory[:64] = original
        self.put_native_record(memory, 0, 4)
        self.put_native_record(memory, 1, 3)

        with tempfile.TemporaryDirectory() as tmp:
            old_state = PUBLISHER.STATE
            PUBLISHER.STATE = Path(tmp) / "ownership.json"
            try:
                with mock.patch.object(PUBLISHER, "gpu_temperature", side_effect=RuntimeError("telemetry unavailable")), \
                     mock.patch.object(PUBLISHER, "boot_id", return_value="test-boot"):
                    PUBLISHER.claim(memory, self.ADDRESS)
                record = bytes(memory[PUBLISHER.RECORD_OFFSET:PUBLISHER.RECORD_OFFSET + PUBLISHER.RECORD_SIZE])
                self.assertTrue(PUBLISHER.owned_record(record))
                self.assertEqual(record[84], PUBLISHER.CAUTION_C)
                self.assertTrue(PUBLISHER.STATE.is_file())
            finally:
                PUBLISHER.STATE = old_state

    def test_restore_retains_owned_record_when_gpu_stays_hot(self):
        memory = bytearray(0x4000)
        original = self.make_header(self.ADDRESS, 2)
        active = PUBLISHER.header_with_count(original, 3)
        memory[:64] = active
        self.put_native_record(memory, 0, 4)
        self.put_native_record(memory, 1, 3)
        memory[PUBLISHER.RECORD_OFFSET:PUBLISHER.RECORD_OFFSET + PUBLISHER.RECORD_SIZE] = PUBLISHER.make_record(70, 12)

        with tempfile.TemporaryDirectory() as tmp:
            old_state = PUBLISHER.STATE
            PUBLISHER.STATE = Path(tmp) / "ownership.json"
            PUBLISHER.STATE.write_text(json.dumps({"test": True}))
            clock = {"now": 0.0}

            def monotonic():
                value = clock["now"]
                clock["now"] += 1.0
                return value

            try:
                with mock.patch.object(PUBLISHER, "gpu_temperature", return_value=70), \
                     mock.patch.object(PUBLISHER.time, "monotonic", side_effect=monotonic), \
                     mock.patch.object(PUBLISHER.time, "sleep", return_value=None):
                    with self.assertRaisesRegex(RuntimeError, "GPU did not cool"):
                        PUBLISHER.restore(memory, original, active)
                record = bytes(memory[PUBLISHER.RECORD_OFFSET:PUBLISHER.RECORD_OFFSET + PUBLISHER.RECORD_SIZE])
                self.assertTrue(PUBLISHER.owned_record(record))
                self.assertEqual(record[84], 70)
                self.assertEqual(bytes(memory[:64]), active)
                self.assertTrue(PUBLISHER.STATE.is_file())
            finally:
                PUBLISHER.STATE = old_state

    def test_source_has_no_workload_or_container_management(self):
        import ast
        tree = ast.parse(SOURCE.read_text())
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
        called_names = {
            node.func.id for node in calls if isinstance(node.func, ast.Name)
        }
        self.assertNotIn("stop_workloads", called_names)
        self.assertNotIn("workloads_active", called_names)
        self.assertNotIn("validate_workload_units", called_names)
        self.assertFalse(any(isinstance(node.func, ast.Attribute) and node.func.attr in {"kill", "terminate", "Popen", "run"} for node in calls))
        source = SOURCE.read_text()
        for marker in ("systemctl stop", "pct exec", "qm stop", "docker exec", "OCSD_WORKLOAD_UNITS"):
            self.assertNotIn(marker, source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
