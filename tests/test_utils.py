#!/usr/bin/env python3
"""
Unit tests for the utility functions of the ICABAR Framework.

This file implements the test cases defined in TEST_CASES_Utilities.md.
"""

import unittest
import sys
import os

# Add the parent directory to the path to import the framework
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from icabar.utils.config import get_default_config, validate_config
from icabar.utils.helpers import get_season

class TestUtilities(unittest.TestCase):
    """Test suite for utility functions."""

    def test_validate_config_valid_UTIL_CONF_001(self):
        """Test Case ID: UTIL-CONF-001 - Verify that a valid config passes."""
        config = get_default_config()
        try:
            validate_config(config)
        except ValueError:
            self.fail("validate_config() raised ValueError unexpectedly!")

    def test_validate_config_missing_key_UTIL_CONF_002(self):
        """Test Case ID: UTIL-CONF-002 - Verify error on missing key."""
        config = get_default_config()
        del config["integration"]
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("Missing required key", str(cm.exception))

    def test_validate_config_invalid_weights_UTIL_CONF_003(self):
        """Test Case ID: UTIL-CONF-003 - Verify error on invalid ensemble weights."""
        config = get_default_config()
        config["integration"]["ensemble_weights"] = [0.5, 0.3, 0.3]
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("Ensemble weights must sum to 1.0", str(cm.exception))

    def test_validate_config_invalid_clusters_UTIL_CONF_004(self):
        """Test Case ID: UTIL-CONF-004 - Verify error on non-positive n_clusters."""
        config = get_default_config()
        config["user_analytics"]["n_clusters"] = 0
        with self.assertRaises(ValueError) as cm:
            validate_config(config)
        self.assertIn("n_clusters must be a positive integer", str(cm.exception))

    def test_get_season_UTIL_SEASON_001(self):
        """Test Case ID: UTIL-SEASON-001 - Verify correct season for each month."""
        self.assertEqual(get_season(12), "Winter")
        self.assertEqual(get_season(1), "Winter")
        self.assertEqual(get_season(2), "Winter")
        self.assertEqual(get_season(3), "Spring")
        self.assertEqual(get_season(4), "Spring")
        self.assertEqual(get_season(5), "Spring")
        self.assertEqual(get_season(6), "Summer")
        self.assertEqual(get_season(7), "Summer")
        self.assertEqual(get_season(8), "Summer")
        self.assertEqual(get_season(9), "Autumn")
        self.assertEqual(get_season(10), "Autumn")
        self.assertEqual(get_season(11), "Autumn")

if __name__ == '__main__':
    unittest.main()

