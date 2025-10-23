#!/usr/bin/env python3
"""
Unit tests for the UserBehaviourAnalytics module of the ICABAR Framework.

This file implements the test cases defined in TEST_CASES_UserBehaviourAnalytics.md.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add the parent directory to the path to import the framework
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from icabar.features.user_behaviour import UserBehaviourAnalytics
from icabar.utils.config import get_default_config

class TestUserBehaviourAnalytics(unittest.TestCase):
    """Test suite for the UserBehaviourAnalytics module."""

    def setUp(self):
        """Set up a sample DataFrame and configuration for testing."""
        self.config = get_default_config()["user_analytics"]
        self.data = pd.DataFrame({
            'user_id': ['user1', 'user2', 'user1', 'user3', 'user2', 'user4'],
            'item_id': ['itemA', 'itemB', 'itemC', 'itemA', 'itemD', 'itemE'],
            'rating': [5, 3, 4, 2, 5, 1],
            'timestamp': pd.to_datetime(['2023-01-15', '2023-03-20', '2023-07-01', '2023-09-10', '2023-11-25', '2023-12-30']),
            'review_text': ['Great product!', 'Okayish', 'Loved it', 'Not good', 'Amazing!', None],
            'helpful_votes': [10, 2, 15, 1, 20, 0],
            'verified_purchase': [True, True, True, False, True, False]
        })
        self.module = UserBehaviourAnalytics(self.data.copy(), self.config)

    def test_initialization_UBA_INIT_001(self):
        """Test Case ID: UBA-INIT-001 - Verify correct initialization."""
        self.assertIsInstance(self.module.data, pd.DataFrame)
        self.assertEqual(self.module.config, self.config)
        self.assertFalse(self.module.trained)

    def test_preprocess_data_UBA_PRE_001(self):
        """Test Case ID: UBA-PRE-001 - Verify correct feature creation."""
        self.module.preprocess_data()
        processed_data = self.module.data
        expected_cols = ['hour', 'day_of_week', 'month', 'is_weekend', 'season', 'review_length', 'engagement_score']
        for col in expected_cols:
            self.assertIn(col, processed_data.columns)
        self.assertTrue(pd.api.types.is_numeric_dtype(processed_data['engagement_score']))

    def test_preprocess_data_missing_text_UBA_PRE_002(self):
        """Test Case ID: UBA-PRE-002 - Verify handling of missing review text."""
        self.module.preprocess_data()
        processed_data = self.module.data
        # The last row has a missing review_text
        self.assertEqual(processed_data.loc[5, 'review_length'], 0)
        self.assertFalse(pd.isna(processed_data.loc[5, 'engagement_score']))

    def test_engagement_scores_range_UBA_ENG_001(self):
        """Test Case ID: UBA-ENG-001 - Verify engagement scores are within [0, 1]."""
        self.module.preprocess_data()
        scores = self.module.data['engagement_score']
        self.assertTrue((scores >= 0).all() and (scores <= 1).all())

    def test_segment_users_UBA_SEG_001(self):
        """Test Case ID: UBA-SEG-001 - Verify correct user segmentation."""
        self.module.preprocess_data()
        self.module.segment_users()
        self.assertIsNotNone(self.module.kmeans_model)
        self.assertEqual(len(self.module.user_segments), self.data['user_id'].nunique())
        self.assertTrue(all(isinstance(seg, np.integer) for seg in self.module.user_segments.values()))

    def test_segment_users_few_users_UBA_SEG_002(self):
        """Test Case ID: UBA-SEG-002 - Verify handling of fewer users than clusters."""
        few_users_data = self.data[self.data['user_id'].isin(['user1', 'user2'])].copy()
        self.config['n_clusters'] = 5
        module = UserBehaviourAnalytics(few_users_data, self.config)
        module.preprocess_data()
        module.segment_users()
        # The number of clusters should be adjusted to the number of unique users
        self.assertEqual(module.kmeans_model.n_clusters, 2)

    def test_predict_existing_user_UBA_PRED_001(self):
        """Test Case ID: UBA-PRED-001 - Verify prediction for an existing user."""
        self.module.train()
        recommendations = self.module.predict('user1', num_recommendations=5)
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 5)
        # Check if all recommended items are valid items from the dataset
        self.assertTrue(all(item in self.data['item_id'].unique() for item in recommendations))

    def test_predict_new_user_cold_start_UBA_PRED_002(self):
        """Test Case ID: UBA-PRED-002 - Verify cold-start prediction for a new user."""
        self.module.train()
        recommendations = self.module.predict('new_user', num_recommendations=3)
        # The fallback should be the most popular items
        popular_items = self.data['item_id'].value_counts().index.tolist()
        self.assertEqual(recommendations, popular_items[:3])

    def test_predict_before_training_raises_error_UBA_PRED_003(self):
        """Test Case ID: UBA-PRED-003 - Verify error when predicting before training."""
        with self.assertRaises(RuntimeError) as cm:
            self.module.predict('user1')
        self.assertEqual(str(cm.exception), "Module must be trained first. Call train() before predicting.")

if __name__ == '__main__':
    unittest.main()

