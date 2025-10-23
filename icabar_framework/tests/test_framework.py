#!/usr/bin/env python3
"""
Integration tests for the ICABARFramework.

This file implements the test cases defined in TEST_CASES_Integration_And_Performance.md.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add the parent directory to the path to import the framework
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from icabar.main import ICABARFramework
from icabar.utils.config import get_default_config

def generate_synthetic_data(num_users=50, num_items=100, num_interactions=1000):
    """Generate a synthetic dataset for integration testing."""
    users = [f'user{i}' for i in range(num_users)]
    items = [f'item{i}' for i in range(num_items)]
    data = pd.DataFrame({
        'user_id': np.random.choice(users, size=num_interactions),
        'item_id': np.random.choice(items, size=num_interactions),
        'rating': np.random.randint(1, 6, size=num_interactions),
        'timestamp': pd.to_datetime(pd.Series(pd.date_range('2023-01-01', periods=num_interactions, freq='H'))),
        'review_text': ['sample review'] * num_interactions,
        'helpful_votes': np.random.randint(0, 50, size=num_interactions),
        'verified_purchase': np.random.choice([True, False], size=num_interactions)
    })
    return data

class TestICABARFrameworkIntegration(unittest.TestCase):
    """Test suite for the full ICABARFramework integration."""

    @classmethod
    def setUpClass(cls):
        """Generate a synthetic dataset for all tests in this class."""
        cls.synthetic_data = generate_synthetic_data()

    def test_full_pipeline_INT_FRAME_001(self):
        """Test Case ID: INT-FRAME-001 - Verify the end-to-end pipeline."""
        framework = ICABARFramework()
        
        # 1. Train the framework
        try:
            framework.train(self.synthetic_data)
        except Exception as e:
            self.fail(f"framework.train() raised an exception unexpectedly: {e}")

        # 2. Predict for an existing user
        existing_user_id = self.synthetic_data['user_id'].iloc[0]
        recommendations = framework.predict(existing_user_id, pd.Timestamp.now(), num_recommendations=10)
        self.assertIsInstance(recommendations, list)
        self.assertEqual(len(recommendations), 10)
        self.assertTrue(all(isinstance(item, str) for item in recommendations))

        # 3. Predict for a new user (cold start)
        new_user_id = 'new_user_xyz'
        cold_start_recs = framework.predict(new_user_id, pd.Timestamp.now(), num_recommendations=10)
        popular_items = self.synthetic_data['item_id'].value_counts().index.tolist()
        self.assertEqual(cold_start_recs, popular_items[:10])

    def test_invalid_config_error_INT_FRAME_002(self):
        """Test Case ID: INT-FRAME-002 - Verify error on invalid configuration."""
        invalid_config = get_default_config()
        invalid_config['integration']['ensemble_weights'] = [1.0, 1.0, 1.0] # Invalid weights
        
        with self.assertRaises(ValueError) as cm:
            ICABARFramework(config=invalid_config)
        self.assertIn("Ensemble weights must sum to 1.0", str(cm.exception))

    def test_invalid_data_error_INT_FRAME_003(self):
        """Test Case ID: INT-FRAME-003 - Verify error on invalid training data."""
        framework = ICABARFramework()
        
        # 1. Test with an empty DataFrame
        with self.assertRaises(ValueError) as cm:
            framework.train(pd.DataFrame())
        self.assertIn("Input data cannot be empty", str(cm.exception))

        # 2. Test with a DataFrame missing a required column
        data_missing_column = self.synthetic_data.drop(columns=['rating'])
        with self.assertRaises(ValueError) as cm:
            framework.train(data_missing_column)
        self.assertIn("Input data is missing required columns", str(cm.exception))

if __name__ == '__main__':
    unittest.main()

