'''
Main ICABAR Framework Class.

This file contains the primary orchestrator for the ICABAR framework, integrating all
the individual modules into a cohesive pipeline for training and prediction.
'''

import logging
from .features.user_behaviour import UserBehaviourAnalytics
from .features.context_aware import ContextAwareSuggestionEngine
from .models.integration import IntegrationModule
from .utils.config import get_default_config, validate_config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ICABARFramework:
    '''
    Integrates User Behaviour Analytics, Context-Aware Computing, and Ensemble Methods
    to deliver personalized and context-aware recommendations.
    '''

    def __init__(self, config=None):
        '''
        Initializes the ICABARFramework.

        Args:
            config (dict, optional): A dictionary of configuration parameters. If not
                                     provided, default settings will be used.
        '''
        base_config = get_default_config()
        if config:
            # In a real application, you would deep merge the configs
            base_config.update(config)
        self.config = base_config
        validate_config(self.config)

        self.user_analytics = None
        self.context_engine = None
        self.integration_module = None
        self.trained = False

    def initialize_components(self, data):
        '''
        Initializes all analytical components of the framework with the provided data.
        '''
        logging.info("Initializing framework components...")
        self.user_analytics = UserBehaviourAnalytics(data, self.config['user_analytics'])
        self.context_engine = ContextAwareSuggestionEngine(data, self.config['context_engine'])
        self.integration_module = IntegrationModule(self.config['integration'])
        logging.info("Framework components initialized successfully.")

    def train(self, training_data):
        '''
        Trains the complete ICABAR framework, including all sub-modules.

        Args:
            training_data (pd.DataFrame): The dataset to be used for training.
        '''
        logging.info("Starting ICABAR Framework training...")
        if training_data is None or training_data.empty:
            raise ValueError("Training data cannot be None or empty.")

        self.initialize_components(training_data)

        self.user_analytics.train()
        self.context_engine.train()
        self.integration_module.train(self.user_analytics, self.context_engine)

        self.trained = True
        logging.info("ICABAR Framework training completed successfully!")

    def predict(self, user_id, timestamp, num_recommendations=10, context=None):
        '''
        Generates recommendations for a given user and context.

        Args:
            user_id (str): The ID of the user for whom to generate recommendations.
            timestamp (pd.Timestamp): The current timestamp for contextual awareness.
            num_recommendations (int): The desired number of recommendations.
            context (dict, optional): Additional contextual information.

        Returns:
            list: A list of final recommended item IDs.
        
        Raises:
            RuntimeError: If the framework has not been trained yet.
        '''
        if not self.trained:
            raise RuntimeError("Framework must be trained before making predictions.")

        logging.info(f"Generating recommendations for user: {user_id}")

        user_predictions = self.user_analytics.predict(user_id, num_recommendations)
        context_predictions = self.context_engine.predict(user_id, timestamp, num_recommendations, context)

        final_recommendations = self.integration_module.integrate(
            user_predictions, context_predictions, user_id, timestamp
        )

        logging.info(f"Generated {len(final_recommendations)} recommendations for user: {user_id}")
        return final_recommendations[:num_recommendations]

