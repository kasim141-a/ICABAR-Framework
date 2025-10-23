#!/usr/bin/env python3
"""
Performance benchmarking script for the ICABAR Framework.

This script measures the prediction latency of the framework and validates
that it meets the 47ms average response time documented in the research.
"""

import time
import pandas as pd
import numpy as np
import sys
import os
from statistics import mean, median

# Add the parent directory to the path to import the framework
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from icabar.main import ICABARFramework

def generate_large_dataset(n_users=1000, n_items=500, n_interactions=100000):
    """Generate a large synthetic dataset for performance testing."""
    np.random.seed(42)
    
    data = pd.DataFrame({
        'user_id': np.random.choice([f'user_{i}' for i in range(n_users)], n_interactions),
        'item_id': np.random.choice([f'item_{i}' for i in range(n_items)], n_interactions),
        'rating': np.random.randint(1, 6, n_interactions),
        'timestamp': pd.date_range('2023-01-01', periods=n_interactions, freq='H'),
        'review_text': ['Sample review text'] * n_interactions,
        'helpful_votes': np.random.randint(0, 20, n_interactions),
        'verified_purchase': np.random.choice([True, False], n_interactions, p=[0.8, 0.2])
    })
    
    return data

def benchmark_prediction_latency(framework, test_users, num_runs=1000):
    """Benchmark the prediction latency of the framework."""
    print(f"Running {num_runs} prediction benchmarks...")
    
    latencies = []
    current_time = pd.Timestamp('2023-06-15 14:30:00')
    
    for i in range(num_runs):
        user_id = np.random.choice(test_users)
        
        start_time = time.perf_counter()
        recommendations = framework.predict(
            user_id=user_id,
            timestamp=current_time,
            num_recommendations=10
        )
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)
        
        if (i + 1) % 100 == 0:
            print(f"Completed {i + 1}/{num_runs} benchmarks...")
    
    return latencies

def analyze_performance(latencies):
    """Analyze and report performance statistics."""
    avg_latency = mean(latencies)
    median_latency = median(latencies)
    p95_latency = np.percentile(latencies, 95)
    p99_latency = np.percentile(latencies, 99)
    
    print("\n" + "="*50)
    print("PERFORMANCE BENCHMARK RESULTS")
    print("="*50)
    print(f"Average latency:    {avg_latency:.2f} ms")
    print(f"Median latency:     {median_latency:.2f} ms")
    print(f"95th percentile:    {p95_latency:.2f} ms")
    print(f"99th percentile:    {p99_latency:.2f} ms")
    print(f"Min latency:        {min(latencies):.2f} ms")
    print(f"Max latency:        {max(latencies):.2f} ms")
    print("="*50)
    
    # Check if we meet the research target
    target_latency = 47.0  # ms
    if avg_latency <= target_latency:
        print(f"✅ SUCCESS: Average latency ({avg_latency:.2f} ms) meets the target ({target_latency} ms)")
    else:
        print(f"❌ FAILURE: Average latency ({avg_latency:.2f} ms) exceeds the target ({target_latency} ms)")
    
    return {
        'average': avg_latency,
        'median': median_latency,
        'p95': p95_latency,
        'p99': p99_latency,
        'min': min(latencies),
        'max': max(latencies),
        'meets_target': avg_latency <= target_latency
    }

def main():
    """Main benchmarking function."""
    print("ICABAR Framework Performance Benchmark")
    print("="*50)
    
    # Generate large dataset
    print("Generating large synthetic dataset...")
    dataset = generate_large_dataset()
    print(f"Generated dataset with {len(dataset)} interactions")
    
    # Initialize and train framework
    print("Initializing and training ICABAR Framework...")
    framework = ICABARFramework()
    framework.train(dataset)
    print("Framework training completed")
    
    # Get test users
    test_users = dataset['user_id'].unique()[:100]  # Use first 100 users for testing
    
    # Run benchmarks
    latencies = benchmark_prediction_latency(framework, test_users)
    
    # Analyze results
    results = analyze_performance(latencies)
    
    return results

if __name__ == '__main__':
    main()
