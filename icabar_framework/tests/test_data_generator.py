#!/usr/bin/env python3
"""
Test data generator utility for the ICABAR Framework tests.

This module provides functions to generate realistic synthetic datasets
for testing various components of the framework.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_user_item_interactions(
    num_users=100, 
    num_items=200, 
    num_interactions=5000,
    start_date='2023-01-01',
    end_date='2023-12-31',
    seed=42
):
    """
    Generate a realistic dataset of user-item interactions.
    
    Args:
        num_users (int): Number of unique users
        num_items (int): Number of unique items
        num_interactions (int): Total number of interactions
        start_date (str): Start date for timestamps
        end_date (str): End date for timestamps
        seed (int): Random seed for reproducibility
    
    Returns:
        pd.DataFrame: Generated interaction data
    """
    np.random.seed(seed)
    random.seed(seed)
    
    # Generate user and item IDs
    users = [f'user_{i:04d}' for i in range(num_users)]
    items = [f'item_{i:04d}' for i in range(num_items)]
    
    # Create item categories for more realistic data
    categories = ['Electronics', 'Books', 'Clothing', 'Home', 'Sports', 'Beauty']
    item_categories = {item: random.choice(categories) for item in items}
    
    # Generate interactions with some realistic patterns
    interactions = []
    
    # Create power users (20% of users generate 60% of interactions)
    power_users = random.sample(users, int(0.2 * num_users))
    regular_users = [u for u in users if u not in power_users]
    
    power_user_interactions = int(0.6 * num_interactions)
    regular_user_interactions = num_interactions - power_user_interactions
    
    # Generate power user interactions
    for _ in range(power_user_interactions):
        user = random.choice(power_users)
        item = random.choice(items)
        
        # Power users tend to rate higher
        rating = np.random.choice([3, 4, 5], p=[0.2, 0.4, 0.4])
        
        interactions.append({
            'user_id': user,
            'item_id': item,
            'rating': rating,
            'category': item_categories[item]
        })
    
    # Generate regular user interactions
    for _ in range(regular_user_interactions):
        user = random.choice(regular_users)
        item = random.choice(items)
        
        # Regular users have more varied ratings
        rating = np.random.choice([1, 2, 3, 4, 5], p=[0.1, 0.15, 0.3, 0.3, 0.15])
        
        interactions.append({
            'user_id': user,
            'item_id': item,
            'rating': rating,
            'category': item_categories[item]
        })
    
    # Convert to DataFrame
    df = pd.DataFrame(interactions)
    
    # Add timestamps with realistic patterns
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    timestamps = []
    for _ in range(len(df)):
        # More activity during business hours and weekdays
        random_date = start + timedelta(
            seconds=random.randint(0, int((end - start).total_seconds()))
        )
        
        # Adjust for realistic time patterns
        if random_date.weekday() < 5:  # Weekday
            if random.random() < 0.7:  # 70% chance of business hours
                hour = random.choice(range(9, 18))
                random_date = random_date.replace(hour=hour)
        
        timestamps.append(random_date)
    
    df['timestamp'] = timestamps
    
    # Add review text (simplified)
    review_templates = [
        "Great product, highly recommend!",
        "Good quality, satisfied with purchase.",
        "Average product, nothing special.",
        "Not what I expected, disappointed.",
        "Excellent! Exceeded my expectations.",
        "Poor quality, would not buy again.",
        "Decent value for money.",
        "Love it! Will buy again.",
        "Okay product, could be better.",
        "Amazing quality and fast delivery!"
    ]
    
    df['review_text'] = [
        random.choice(review_templates) if random.random() < 0.8 else None
        for _ in range(len(df))
    ]
    
    # Add helpful votes (correlated with rating)
    df['helpful_votes'] = df['rating'].apply(
        lambda r: max(0, int(np.random.poisson(r * 2)))
    )
    
    # Add verified purchase flag
    df['verified_purchase'] = np.random.choice(
        [True, False], size=len(df), p=[0.85, 0.15]
    )
    
    return df.sort_values('timestamp').reset_index(drop=True)

def generate_small_test_dataset():
    """Generate a small dataset for quick unit tests."""
    return generate_user_item_interactions(
        num_users=10,
        num_items=20,
        num_interactions=50,
        seed=42
    )

def generate_medium_test_dataset():
    """Generate a medium dataset for integration tests."""
    return generate_user_item_interactions(
        num_users=50,
        num_items=100,
        num_interactions=1000,
        seed=42
    )

def generate_large_test_dataset():
    """Generate a large dataset for performance tests."""
    return generate_user_item_interactions(
        num_users=1000,
        num_items=500,
        num_interactions=100000,
        seed=42
    )

def generate_edge_case_dataset():
    """Generate a dataset with edge cases for robustness testing."""
    # Start with a small base dataset
    df = generate_small_test_dataset()
    
    # Add some edge cases
    edge_cases = pd.DataFrame({
        'user_id': ['edge_user_1', 'edge_user_2', 'edge_user_1'],
        'item_id': ['edge_item_1', 'edge_item_2', 'edge_item_1'],
        'rating': [1, 5, 3],
        'timestamp': pd.to_datetime(['2023-01-01', '2023-12-31', '2023-06-15']),
        'review_text': [None, '', 'A' * 1000],  # None, empty, very long
        'helpful_votes': [0, 100, -1],  # Zero, high, negative (invalid)
        'verified_purchase': [False, True, None],  # Mixed values including None
        'category': ['Test', 'Test', 'Test']
    })
    
    return pd.concat([df, edge_cases], ignore_index=True)

if __name__ == '__main__':
    # Generate sample datasets for testing
    print("Generating test datasets...")
    
    small_data = generate_small_test_dataset()
    print(f"Small dataset: {len(small_data)} interactions")
    
    medium_data = generate_medium_test_dataset()
    print(f"Medium dataset: {len(medium_data)} interactions")
    
    large_data = generate_large_test_dataset()
    print(f"Large dataset: {len(large_data)} interactions")
    
    edge_data = generate_edge_case_dataset()
    print(f"Edge case dataset: {len(edge_data)} interactions")
    
    print("\nSample of small dataset:")
    print(small_data.head())
