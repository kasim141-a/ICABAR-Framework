'''
User Behaviour Analytics Module for the ICABAR Framework.

This module is responsible for processing user interaction data to extract behavioural
patterns, segment users, and generate personalized recommendation scores. It implements
several key functionalities as described in the research, including:

- Comprehensive data preprocessing and feature engineering.
- Temporal pattern analysis to identify trends and cyclical behaviours.
- User segmentation using K-means clustering to group users with similar behaviours.
- Engagement metric calculation to quantify user interaction quality.
- Prediction of user preferences based on their historical behaviour.
'''

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from ..utils.helpers import get_season

class UserBehaviourAnalytics:
    '''
    Processes implicit feedback signals, temporal patterns, and engagement metrics to
    create comprehensive user behaviour profiles.
    '''

    def __init__(self, data_source, config):
        '''
        Initializes the UserBehaviourAnalytics module.

        Args:
            data_source (pd.DataFrame): The raw user interaction data.
            config (dict): Configuration parameters for the module.
        '''
        self.data = data_source.copy()
        self.config = config
        self.user_profiles = {}
        self.temporal_patterns = {}
        self.engagement_metrics = {}
        self.user_segments = {}
        self.scaler = StandardScaler()
        self.kmeans_model = None
        self.trained = False

    def train(self):
        '''
        Trains the User Behaviour Analytics module by executing the full pipeline.
        '''
        print("Starting User Behaviour Analytics training...")
        self.preprocess_data()
        self.extract_temporal_patterns()
        self.segment_users()
        self.trained = True
        print("User Behaviour Analytics training completed.")

    def preprocess_data(self):
        '''
        Performs comprehensive data preprocessing and feature engineering.
        '''
        if 'timestamp' not in self.data.columns:
            raise ValueError("Missing required column: 'timestamp'")

        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
        self.data['hour'] = self.data['timestamp'].dt.hour
        self.data['day_of_week'] = self.data['timestamp'].dt.dayofweek
        self.data['month'] = self.data['timestamp'].dt.month
        self.data['is_weekend'] = self.data['day_of_week'].isin([5, 6])
        self.data['season'] = self.data['month'].apply(get_season)
        self.data['review_length'] = self.data['review_text'].str.len().fillna(0)
        self.data['engagement_score'] = self.calculate_engagement_scores()

    def calculate_engagement_scores(self):
        '''
        Calculates a comprehensive engagement score for each interaction.
        '''
        max_helpful = self.data['helpful_votes'].max()
        normalized_helpful = self.data['helpful_votes'] / max_helpful if max_helpful > 0 else 0

        max_length = self.data['review_length'].max()
        normalized_length = self.data['review_length'] / max_length if max_length > 0 else 0

        engagement = (
            0.4 * normalized_helpful +
            0.3 * normalized_length +
            0.2 * self.data['verified_purchase'].astype(int) +
            0.1 * (self.data['rating'] != 3).astype(int)
        )
        return engagement

    def extract_temporal_patterns(self):
        '''
        Extracts and analyzes temporal patterns from the user interaction data.
        '''
        hourly_activity = self.data.groupby('hour').agg({'rating': ['mean', 'count']}).round(3)
        daily_activity = self.data.groupby('day_of_week').agg({'rating': ['mean', 'count']}).round(3)
        seasonal_activity = self.data.groupby('season').agg({'rating': ['mean', 'count']}).round(3)

        self.temporal_patterns = {
            'hourly_activity': hourly_activity,
            'daily_activity': daily_activity,
            'seasonal_activity': seasonal_activity
        }

    def segment_users(self):
        '''
        Segments users into distinct clusters based on their behaviour.
        '''
        user_features = self.data.groupby('user_id').agg(
            avg_rating=('rating', 'mean'),
            num_reviews=('rating', 'count'),
            avg_engagement=('engagement_score', 'mean')
        ).fillna(0)

        if len(user_features) < self.config['n_clusters']:
            print("Warning: Not enough users to form the desired number of clusters.")
            self.config['n_clusters'] = max(1, len(user_features))

        if not user_features.empty:
            scaled_features = self.scaler.fit_transform(user_features)
            self.kmeans_model = KMeans(n_clusters=self.config['n_clusters'], random_state=42, n_init=10)
            user_features['segment'] = self.kmeans_model.fit_predict(scaled_features)
            self.user_segments = user_features[['segment']].to_dict()['segment']

    def predict(self, user_id, num_recommendations=10):
        '''
        Generates recommendations for a given user based on their behaviour.

        Args:
            user_id (str): The ID of the user to generate recommendations for.
            num_recommendations (int): The number of recommendations to generate.

        Returns:
            list: A list of recommended item IDs.
        '''
        if not self.trained:
            raise RuntimeError("The UserBehaviourAnalytics module has not been trained yet.")

        # This is a simplified prediction logic. A real implementation would be more complex.
        if user_id in self.data['user_id'].unique():
            user_data = self.data[self.data['user_id'] == user_id]
            top_items = user_data.sort_values(by='rating', ascending=False)['item_id'].unique()
            return list(top_items[:num_recommendations])
        else:
            # For new users, recommend the most popular items overall.
            popular_items = self.data.groupby('item_id')['rating'].count().nlargest(num_recommendations).index
            return list(popular_items)

