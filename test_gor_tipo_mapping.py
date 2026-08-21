#!/usr/bin/env python3
"""Unit tests for GOR TIPO_VALVOLA → SAP valve type mapping."""

import unittest

from run_hierarchy_orchestrator import _tipo_to_sap_type


class GorTipoMappingTests(unittest.TestCase):
    def test_lwe_solenoid_is_nc(self) -> None:
        self.assertEqual(_tipo_to_sap_type("4S4-LWE-15"), ("NC", True))

    def test_it_isolation_is_nc(self) -> None:
        self.assertEqual(_tipo_to_sap_type("4S4-IT-25"), ("NC", True))

    def test_manual_butterfly_is_nc(self) -> None:
        self.assertEqual(_tipo_to_sap_type("2K0-BF-65"), ("NC", True))

    def test_motorized_butterfly_is_av(self) -> None:
        self.assertEqual(_tipo_to_sap_type("6S6-BF-65"), ("AV", True))

    def test_safety_valve_is_sv(self) -> None:
        self.assertEqual(_tipo_to_sap_type("ST-65"), ("SV", True))

    def test_three_way_solenoid_is_av(self) -> None:
        self.assertEqual(_tipo_to_sap_type("VX-25"), ("AV", True))

    def test_blind_flange_not_valve(self) -> None:
        self.assertEqual(_tipo_to_sap_type("3G4-FL-65"), (None, False))


if __name__ == "__main__":
    unittest.main()
