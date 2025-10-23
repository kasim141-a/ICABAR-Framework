#!/usr/bin/env python3
"""
Research validation script for the ICABAR Framework.

This script validates the research claims by comparing the ICABAR Framework
against a baseline collaborative filtering model using the same evaluation
metrics described in the research paper.
"""

import pandas as pd
import numpy as np
import sys
import os
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split

# Add the parent directory to the path to import the framework
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from icabar.main import ICABARFramework

class BaselineCollaborativeFiltering:
    """Simple user-based collaborative filtering baseline."""
    
    def __init__(self):
        self.user_item_matrix = None
        self.user_similarity = None
        self.trained = False
    
    def train(self, data):
        """Train the baseline model."""
        # Create user-item matrix
        self.user_item_matrix = data.pivot_table(
            index='user_id', 
            columns='item_id', 
            values='rating', 
            fill_value=0
        )
        
        # Calculate user similarity
        self.user_similarity = cosine_similarity(self.user_item_matrix)
        self.user_similarity = pd.DataFrame(
            self.user_similarity,
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.index
        )
        
        self.trained = True
    
    def predict(self, user_id, num_recommendations=10):
        """Generate recommendations for a user."""
        if not self.trained:
            raise RuntimeError("Model must be trained first")
        
        if user_id not in self.user_item_matrix.index:
            # Return most popular items for new users
            item_popularity = self.user_item_matrix.sum(axis=0)
            return item_popularity.nlargest(num_recommendations).index.tolist()
        
        # Find similar users
        user_similarities = self.user_similarity.loc[user_id].sort_values(ascending=False)
        similar_users = user_similarities.iloc[1:11].index  # Top 10 similar users
        
        # Get items rated by similar users but not by target user
        user_ratings = self.user_item_matrix.loc[user_id]
        unrated_items = user_ratings[user_ratings == 0].index
        
        # Calculate scores for unrated items
        item_scores = {}
        for item in unrated_items:
            score = 0
            for similar_user in similar_users:
                if self.user_item_matrix.loc[similar_user, item] > 0:
                    score += (user_similarities[similar_user] * 
                             self.user_item_matrix.loc[similar_user, item])
            item_scores[item] = score
        
        # Return top recommendations
        sorted_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)
        return [item for item, score in sorted_items[:num_recommendations]]

def calculate_precision_recall(recommendations, actual_items, k=10):
    """Calculate Precision@k and Recall@k."""
    if not actual_items:
        return 0.0, 0.0
    
    relevant_recommended = set(recommendations[:k]) & set(actual_items)
    
    precision = len(relevant_recommended) / k if k > 0 else 0.0
    recall = len(relevant_recommended) / len(actual_items) if actual_items else 0.0
    
    return precision, recall

def calculate_diversity(recommendations, item_features=None):
    """Calculate intra-list diversity (simplified version)."""
    if len(recommendations) < 2:
        return 0.0
    
    # Simplified diversity calculation based on item ID differences
    # In a real implementation, this would use item features/categories
    unique_items = len(set(recommendations))
    return unique_items / len(recommendations)

def calculate_novelty(recommendations, popular_items, top_n=100):
    """Calculate novelty based on item popularity."""
    if not recommendations:
        return 0.0
    
    novel_items = [item for item in recommendations if item not in popular_items[:top_n]]
    return len(novel_items) / len(recommendations)

def evaluate_model(model, test_data, popular_items, model_name="Model"):
    """Evaluate a model on test data."""
    print(f"Evaluating {model_name}...")
    
    precisions = []
    recalls = []
    diversities = []
    novelties = []
    
    test_users = test_data['user_id'].unique()[:100]  # Evaluate on first 100 users
    
    for user_id in test_users:
        # Get user's actual items from test set
        user_test_items = test_data[test_data['user_id'] == user_id]['item_id'].tolist()
        
        # Generate recommendations
        try:
            if hasattr(model, 'predict') and len(model.predict.__code__.co_varnames) > 2:
                # ICABAR Framework
                recommendations = model.predict(
                    user_id, 
                    pd.Timestamp('2023-06-15 14:30:00'), 
                    num_recommendations=10
                )
            else:
                # Baseline model
                recommendations = model.predict(user_id, num_recommendations=10)
        except:
            recommendations = []
        
        # Calculate metrics
        precision, recall = calculate_precision_recall(recommendations, user_test_items)
        diversity = calculate_diversity(recommendations)
        novelty = calculate_novelty(recommendations, popular_items)
        
        precisions.append(precision)
        recalls.append(recall)
        diversities.append(diversity)
        novelties.append(novelty)
    
    return {
        'precision': np.mean(precisions),
        'recall': np.mean(recalls),
        'diversity': np.mean(diversities),
        'novelty': np.mean(novelties)
    }

def generate_evaluation_dataset(n_users=500, n_items=200, n_interactions=10000):
    """Generate a dataset for evaluation."""
    np.random.seed(42)
    
    data = pd.DataFrame({
        'user_id': np.random.choice([f'user_{i}' for i in range(n_users)], n_interactions),
        'item_id': np.random.choice([f'item_{i}' for i in range(n_items)], n_interactions),
        'rating': np.random.randint(1, 6, n_interactions),
        'timestamp': pd.date_range('2023-01-01', periods=n_interactions, freq='H'),
        'review_text': ['Sample review'] * n_interactions,
        'helpful_votes': np.random.randint(0, 10, n_interactions),
        'verified_purchase': np.random.choice([True, False], n_interactions, p=[0.8, 0.2])
    })
    
    return data

def main():
    """Main validation function."""
    print("ICABAR Framework Research Validation")
    print("="*50)
    
    # Generate evaluation dataset
    print("Generating evaluation dataset...")
    full_dataset = generate_evaluation_dataset()
    
    # Split into train and test
    train_data, test_data = train_test_split(full_dataset, test_size=0.2, random_state=42)
    print(f"Training set: {len(train_data)} interactions")
    print(f"Test set: {len(test_data)} interactions")
    
    # Calculate popular items for novelty metric
    popular_items = train_data['item_id'].value_counts().index.tolist()
    
    # Train ICABAR Framework
    print("\nTraining ICABAR Framework...")
    icabar = ICABARFramework()
    icabar.train(train_data)
    
    # Train baseline model
    print("Training baseline collaborative filtering model...")
    baseline = BaselineCollaborativeFiltering()
    baseline.train(train_data)
    
    # Evaluate both models
    icabar_results = evaluate_model(icabar, test_data, popular_items, "ICABAR Framework")
    baseline_results = evaluate_model(baseline, test_data, popular_items, "Baseline CF")
    
    # Calculate improvements
    print("\n" + "="*60)
    print("RESEARCH VALIDATION RESULTS")
    print("="*60)
    
    metrics = ['precision', 'recall', 'diversity', 'novelty']
    target_improvements = {
        'precision': 0.33,  # 33% improvement
        'recall': 0.33,     # 33% improvement (using same as precision)
        'diversity': 0.65,  # 65% improvement
        'novelty': 0.45     # 45% improvement
    }
    
    for metric in metrics:
        icabar_score = icabar_results[metric]
        baseline_score = baseline_results[metric]
        
        if baseline_score > 0:
            improvement = (icabar_score - baseline_score) / baseline_score
        else:
            improvement = 0.0
        
        target = target_improvements[metric]
        meets_target = improvement >= target
        
        print(f"\n{metric.upper()}:")
        print(f"  ICABAR:     {icabar_score:.4f}")
        print(f"  Baseline:   {baseline_score:.4f}")
        print(f"  Improvement: {improvement:.1%} (Target: {target:.1%})")
        print(f"  Status:     {'✅ PASS' if meets_target else '❌ FAIL'}")
    
    print("\n" + "="*60)
    
    return {
        'icabar_results': icabar_results,
        'baseline_results': baseline_results,
        'improvements': {
            metric: (icabar_results[metric] - baseline_results[metric]) / baseline_results[metric] 
            if baseline_results[metric] > 0 else 0.0
            for metric in metrics
        }
    }

if __name__ == '__main__':
    main()
