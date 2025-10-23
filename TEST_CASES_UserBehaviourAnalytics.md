# Test Cases: UserBehaviourAnalytics Module

This document provides detailed example test cases for the `UserBehaviourAnalytics` module, as outlined in the test plan.

## 1. Test Cases for `__init__`

### Test Case ID: UBA-INIT-001

- **Objective**: Verify that the module initializes correctly with valid data and configuration.
- **Input Data**:
    - `data_source`: A non-empty pandas DataFrame with required columns (`user_id`, `item_id`, `rating`, etc.).
    - `config`: A valid configuration dictionary for the module.
- **Expected Output**: An instance of the `UserBehaviourAnalytics` class is created without errors.
- **Validation Criteria**:
    - The `self.data` attribute is a copy of the input DataFrame.
    - The `self.config` attribute matches the input configuration.
    - The `self.trained` flag is `False`.

## 2. Test Cases for `preprocess_data`

### Test Case ID: UBA-PRE-001

- **Objective**: Verify that the preprocessing pipeline correctly adds temporal and engagement features to the data.
- **Input Data**: A DataFrame with `timestamp` and `review_text` columns.
- **Expected Output**: The DataFrame `self.data` is updated with new columns: `hour`, `day_of_week`, `month`, `is_weekend`, `season`, `review_length`, and `engagement_score`.
- **Validation Criteria**:
    - All new columns are present in the DataFrame.
    - The data types of the new columns are correct (e.g., `hour` is an integer, `engagement_score` is a float).
    - The values in the new columns are within their expected ranges (e.g., `hour` is between 0 and 23).

### Test Case ID: UBA-PRE-002 (Edge Case)

- **Objective**: Verify that the preprocessing pipeline handles missing `review_text` gracefully.
- **Input Data**: A DataFrame where some rows have `None` or `NaN` in the `review_text` column.
- **Expected Output**: The process completes without errors.
- **Validation Criteria**:
    - The `review_length` for rows with missing `review_text` is set to 0.
    - The `engagement_score` is calculated correctly, treating the missing text contribution as 0.

## 3. Test Cases for `calculate_engagement_scores`

### Test Case ID: UBA-ENG-001

- **Objective**: Ensure that the calculated engagement scores are always within the expected range [0, 1].
- **Input Data**: A diverse DataFrame with a wide range of `helpful_votes`, `review_length`, and `rating` values.
- **Expected Output**: A pandas Series of engagement scores.
- **Validation Criteria**:
    - All values in the returned Series are greater than or equal to 0.
    - All values in the returned Series are less than or equal to 1.

## 4. Test Cases for `segment_users`

### Test Case ID: UBA-SEG-001

- **Objective**: Verify that users are correctly segmented into the specified number of clusters.
- **Input Data**: A dataset with a sufficient number of unique users (e.g., > 100).
- **Expected Output**: The `self.user_segments` dictionary is populated.
- **Validation Criteria**:
    - The `self.kmeans_model` is a trained `KMeans` instance.
    - The `self.user_segments` dictionary contains an entry for each user.
    - The segment labels assigned to users are integers between 0 and `n_clusters - 1`.

### Test Case ID: UBA-SEG-002 (Edge Case)

- **Objective**: Verify that the segmentation handles cases where there are fewer users than the desired number of clusters.
- **Input Data**: A dataset with only 3 unique users, while `n_clusters` is configured to 5.
- **Expected Output**: The process completes without errors.
- **Validation Criteria**:
    - The `self.config['n_clusters']` is automatically adjusted to the number of unique users (3).
    - The `self.kmeans_model` is trained with the adjusted number of clusters.

## 5. Test Cases for `predict`

### Test Case ID: UBA-PRED-001

- **Objective**: Verify that the `predict` method returns a list of recommendations for an existing user.
- **Input Data**: A `user_id` that exists in the training data.
- **Expected Output**: A list of recommended `item_id`s.
- **Validation Criteria**:
    - The returned value is a list.
    - The list contains a number of items less than or equal to `num_recommendations`.
    - All items in the list are valid `item_id`s from the dataset.

### Test Case ID: UBA-PRED-002 (Cold Start)

- **Objective**: Verify the cold-start strategy by requesting recommendations for a new user.
- **Input Data**: A `user_id` that does **not** exist in the training data.
- **Expected Output**: A list of globally popular items.
- **Validation Criteria**:
    - The returned list contains the top `num_recommendations` most frequently rated items from the entire dataset.

### Test Case ID: UBA-PRED-003 (Error Handling)

- **Objective**: Verify that calling `predict` before `train` raises a `RuntimeError`.
- **Input Data**: A `user_id`.
- **Action**: Call `predict()` on a `UserBehaviourAnalytics` instance that has not been trained.
- **Expected Output**: A `RuntimeError` is raised.
- **Validation Criteria**: The error message clearly states that the module must be trained first.

