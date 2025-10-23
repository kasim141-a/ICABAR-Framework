#!/usr/bin/env python3
"""
Unit tests for the IntegrationModule of the ICABAR Framework.

This file implements the test cases defined in TEST_CASES_IntegrationModule.md.
"""

import unittest
import pandas as pd
import sys
import os

# Add the parent directory to the path to import the framework
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from icabar.models.integration import IntegrationModule
from icabar.utils.config import get_default_config

class TestIntegrationModule(unittest.TestCase):
    """Test suite for the IntegrationModule."""

    def setUp(self):
        """Set up a configuration for testing."""
        self.config = get_default_config()["integration"]
        self.module = IntegrationModule(self.config)

    def test_initialization_INT_INIT_001(self):
        """Test Case ID: INT-INIT-001 - Verify correct initialization."""
        self.assertEqual(self.module.config, self.config)
        self.assertFalse(self.module.trained)

    def test_train_INT_TRAIN_001(self):
        """Test Case ID: INT-TRAIN-001 - Verify training process completion."""
        # Mock the analytics and engine modules
        mock_analytics = unittest.mock.Mock()
        mock_engine = unittest.mock.Mock()
        self.module.train(mock_analytics, mock_engine)
        self.assertTrue(self.module.trained)
        self.assertEqual(self.module.user_analytics_weight, self.config['ensemble_weights'][0])

    def test_integrate_weighted_ensemble_INT_INT_001(self):
        """Test Case ID: INT-INT-001 - Verify weighted ensemble logic."""
        self.module.train(None, None) # Mock training
        user_preds = ['item_A', 'item_B', 'item_C']
        context_preds = ['item_B', 'item_D', 'item_A']
        
        # Manually set weights for predictable results
        self.module.user_analytics_weight = 0.6
        self.module.context_engine_weight = 0.4
        self.module.integration_weight = 0.0

        result = self.module.integrate(user_preds, context_preds, 'user1', pd.Timestamp.now())

        # Expected scores:
        # item_A: 0.6 * (1/1) + 0.4 * (1/3) = 0.6 + 0.133 = 0.733
        # item_B: 0.6 * (1/2) + 0.4 * (1/1) = 0.3 + 0.4 = 0.7
        # item_C: 0.6 * (1/3) = 0.2
        # item_D: 0.4 * (1/2) = 0.2
        # Expected order: item_A, item_B, item_C/item_D
        self.assertIsInstance(result, list)
        self.assertEqual(result[0], 'item_A')
        self.assertEqual(result[1], 'item_B')

    def test_integrate_empty_inputs_INT_INT_002(self):
        """Test Case ID: INT-INT-002 - Verify handling of empty recommendation lists."""
        self.module.train(None, None)
        result = self.module.integrate([], [], 'user1', pd.Timestamp.now())
        self.assertEqual(result, [])

    def test_integrate_one_empty_input_INT_INT_003(self):
        """Test Case ID: INT-INT-003 - Verify correct handling of one empty list."""
        self.module.train(None, None)
        user_preds = ['item_A', 'item_B']
        result = self.module.integrate(user_preds, [], 'user1', pd.Timestamp.now())
        self.assertEqual(result, ['item_A', 'item_B'])

    def test_integrate_before_training_raises_error_INT_INT_004(self):
        """Test Case ID: INT-INT-004 - Verify error when integrating before training."""
        with self.assertRaises(RuntimeError) as cm:
            self.module.integrate(['item_A'], ['item_B'], 'user1', pd.Timestamp.now())
        self.assertEqual(str(cm.exception), "Module must be trained first. Call train() before integrating.")

if __name__ == '__main__':
    unittest.main()

