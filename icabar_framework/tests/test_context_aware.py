#!/usr/bin/env python3
"""
Unit tests for the ContextAwareSuggestionEngine module of the ICABAR Framework.

This file implements the test cases defined in TEST_CASES_ContextAwareSuggestionEngine.md.
"""

import unittest
import pandas as pd
import sys
import os

# Add the parent directory to the path to import the framework
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from icabar.features.context_aware import ContextAwareSuggestionEngine
from icabar.utils.config import get_default_config

class TestContextAwareSuggestionEngine(unittest.TestCase):
    """Test suite for the ContextAwareSuggestionEngine module."""

    def setUp(self):
        """Set up a sample DataFrame and configuration for testing."""
        self.config = get_default_config()["context_aware"]
        self.data = pd.DataFrame({
            'user_id': ['user1', 'user2', 'user1', 'user3'],
            'item_id': ['itemA', 'itemB', 'itemC', 'itemA'],
            'rating': [5, 3, 4, 2],
            'timestamp': pd.to_datetime(['2023-01-15 09:30:00', '2023-03-20 18:00:00', '2023-07-01 09:00:00', '2023-09-10 21:00:00'])
        })
        self.module = ContextAwareSuggestionEngine(self.data.copy(), self.config)

    def test_initialization_CASE_INIT_001(self):
        """Test Case ID: CASE-INIT-001 - Verify correct initialization."""
        self.assertIsInstance(self.module.data, pd.DataFrame)
        self.assertEqual(self.module.config, self.config)
        self.assertFalse(self.module.trained)

    def test_train_CASE_TRAIN_001(self):
        """Test Case ID: CASE-TRAIN-001 - Verify training process completion."""
        self.module.train()
        self.assertTrue(self.module.trained)

    def test_extract_contextual_features_CASE_FEAT_001(self):
        """Test Case ID: CASE-FEAT-001 - Verify temporal feature extraction."""
        self.module.train()
        self.assertIn('time_of_day', self.module.contextual_features)
        # Check if hours from the data are keys in the dictionary
        self.assertIn(9, self.module.contextual_features['time_of_day'])
        self.assertIn(18, self.module.contextual_features['time_of_day'])
        self.assertIsInstance(self.module.contextual_features['time_of_day'][9], list)

    def test_predict_context_aware_CASE_PRED_001(self):
        """Test Case ID: CASE-PRED-001 - Verify context-aware predictions differ."""
        self.module.train()
        # Morning prediction should be influenced by 9 AM data
        morning_recs = self.module.predict('user1', pd.Timestamp('2023-10-01 09:15:00'))
        # Evening prediction should be influenced by 6 PM data
        evening_recs = self.module.predict('user1', pd.Timestamp('2023-10-01 18:30:00'))
        
        self.assertIsInstance(morning_recs, list)
        self.assertIsInstance(evening_recs, list)
        # The recommendations should be different because the context is different
        self.assertNotEqual(morning_recs, evening_recs)
        self.assertIn('itemA', morning_recs) # itemA and itemC were rated at 9 AM
        self.assertIn('itemC', morning_recs)
        self.assertIn('itemB', evening_recs) # itemB was rated at 6 PM

    def test_predict_fallback_CASE_PRED_002(self):
        """Test Case ID: CASE-PRED-002 - Verify fallback for unknown context."""
        self.module.train()
        # 2 AM is a context with no data
        fallback_recs = self.module.predict('user1', pd.Timestamp('2023-10-01 02:00:00'))
        popular_items = self.data['item_id'].value_counts().index.tolist()
        self.assertEqual(fallback_recs, popular_items[:10])

    def test_predict_before_training_raises_error_CASE_PRED_003(self):
        """Test Case ID: CASE-PRED-003 - Verify error when predicting before training."""
        with self.assertRaises(RuntimeError) as cm:
            self.module.predict('user1', pd.Timestamp.now())
        self.assertEqual(str(cm.exception), "Module must be trained first. Call train() before predicting.")

if __name__ == '__main__':
    unittest.main()

