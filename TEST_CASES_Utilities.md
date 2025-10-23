# Test Cases: Utilities

This document provides detailed example test cases for the utility functions in `icabar/utils`.

## 1. Test Cases for `validate_config`

### Test Case ID: UTIL-CONF-001

- **Objective**: Verify that a valid, default configuration passes validation.
- **Input Data**: The dictionary returned by `get_default_config()`.
- **Action**: Call `validate_config()` with the input data.
- **Expected Output**: The function completes without raising any exceptions.

### Test Case ID: UTIL-CONF-002 (Error Handling)

- **Objective**: Verify that a configuration with missing keys raises a `ValueError`.
- **Input Data**: A configuration dictionary missing the `integration` key.
- **Action**: Call `validate_config()` with the input data.
- **Expected Output**: A `ValueError` is raised.
- **Validation Criteria**: The error message clearly indicates that a required key is missing.

### Test Case ID: UTIL-CONF-003 (Error Handling)

- **Objective**: Verify that a configuration with invalid `ensemble_weights` (not summing to 1.0) raises a `ValueError`.
- **Input Data**: A configuration where `config["integration"]["ensemble_weights"]` is `[0.5, 0.3, 0.3]`.
- **Action**: Call `validate_config()` with the input data.
- **Expected Output**: A `ValueError` is raised.
- **Validation Criteria**: The error message clearly states that the ensemble weights must sum to 1.0.

### Test Case ID: UTIL-CONF-004 (Error Handling)

- **Objective**: Verify that a configuration with a non-positive `n_clusters` raises a `ValueError`.
- **Input Data**: A configuration where `config["user_analytics"]["n_clusters"]` is `0`.
- **Action**: Call `validate_config()` with the input data.
- **Expected Output**: A `ValueError` is raised.
- **Validation Criteria**: The error message clearly states that `n_clusters` must be a positive integer.

## 2. Test Cases for `get_season`

### Test Case ID: UTIL-SEASON-001

- **Objective**: Verify that the `get_season` function returns the correct season for each month.
- **Input Data**: Integers from 1 to 12.
- **Action**: Call `get_season()` for each integer.
- **Expected Output**:
    - `Winter` for months 12, 1, 2.
    - `Spring` for months 3, 4, 5.
    - `Summer` for months 6, 7, 8.
    - `Autumn` for months 9, 10, 11.
- **Validation Criteria**: The returned string for each month matches the expected season.

