# Test Cases: Integration and Performance

This document provides detailed example test cases for the integration of the `ICABARFramework` and for performance validation.

## 1. Integration Test Cases (`tests/test_framework.py`)

### Test Case ID: INT-FRAME-001 (Full Pipeline)

- **Objective**: Verify the end-to-end functionality of the `ICABARFramework` from training to prediction.
- **Input Data**: A synthetic dataset of ~1000 interactions, 50 users, and 100 items, including users with varied interaction patterns.
- **Actions**:
    1. Initialize `ICABARFramework` with the default configuration.
    2. Call the `train()` method with the synthetic dataset.
    3. Call the `predict()` method for a user known to be in the dataset.
    4. Call the `predict()` method for a new user (not in the dataset).
- **Expected Output**:
    - The `train()` method completes without errors.
    - The `predict()` call for the existing user returns a list of 10 unique item IDs.
    - The `predict()` call for the new user returns a list of 10 globally popular items.
- **Validation Criteria**:
    - No exceptions are raised during the process.
    - The returned lists contain the correct number of items.
    - All items in the lists are valid `item_id`s.

### Test Case ID: INT-FRAME-002 (Error Handling - Invalid Config)

- **Objective**: Ensure the framework handles invalid configuration gracefully during initialization.
- **Action**: Initialize `ICABARFramework` with a configuration where `ensemble_weights` do not sum to 1.0.
- **Expected Output**: A `ValueError` is raised.
- **Validation Criteria**: The error message clearly indicates the problem with the `ensemble_weights`.

### Test Case ID: INT-FRAME-003 (Error Handling - Invalid Data)

- **Objective**: Verify the framework's robustness when provided with empty or malformed data during training.
- **Actions**:
    1. Call the `train()` method with an empty DataFrame.
    2. Call the `train()` method with a DataFrame missing a required column (e.g., `rating`).
- **Expected Output**: A `ValueError` is raised in both cases.
- **Validation Criteria**: The error messages clearly indicate the problem with the input data.

## 2. Performance Test Cases (`scripts/performance_benchmark.py`)

### Test Case ID: PERF-LAT-001 (Prediction Latency)

- **Objective**: To validate that the framework's prediction latency meets the 47ms average response time.
- **Setup**:
    - Generate a large-scale synthetic dataset (e.g., 100,000 interactions).
    - Train the `ICABARFramework` on this dataset.
- **Action**:
    - Use the `performance_benchmark.py` script to measure the execution time of the `predict()` method over 1,000 runs for random users.
- **Expected Output**: Performance statistics are printed to the console.
- **Validation Criteria**:
    - The calculated **average prediction time** across all runs is less than or equal to 47ms.
    - The script also reports median, 95th, and 99th percentile latencies for detailed analysis.

## 3. Research Validation Test Cases (`scripts/research_validation.py`)

### Test Case ID: RES-VAL-001 (Accuracy, Diversity, Novelty)

- **Objective**: To empirically validate the performance claims (accuracy, diversity, novelty) made in the research paper.
- **Setup**:
    - Use the full Amazon Reviews 2023 dataset (or a representative large-scale dataset).
    - Split the dataset into an 80% training set and a 20% test set.
    - Implement a baseline user-based Collaborative Filtering (CF) model.
- **Action**:
    - Run the `research_validation.py` script, which:
        1. Trains both the ICABAR Framework and the baseline CF model on the training set.
        2. Generates top-10 recommendations for each user in the test set from both models.
        3. Calculates Precision@10, Recall@10, Intra-list Diversity, and Novelty for both sets of recommendations.
        4. Compares the average scores for each metric.
- **Expected Output**: A report comparing the performance of the two models.
- **Validation Criteria**:
    - **Accuracy**: ICABAR shows a ~33% relative improvement in Precision@10 and Recall@10 over the baseline.
    - **Diversity**: ICABAR shows a ~65% relative improvement in the diversity score over the baseline.
    - **Novelty**: ICABAR shows a ~45% relative improvement in the novelty score over the baseline.
    - The improvements are statistically significant.

