
'"""
Configuration management for the ICABAR Framework.

This module provides the default configuration for the framework and functions
to validate the configuration parameters.
'"""

def get_default_config():
    '"""Returns the default configuration for the ICABAR framework."""    
    return {
        'user_analytics': {
            'n_clusters': 5,
            'temporal_window': 30,
            'min_interactions': 3,
        },
        'context_engine': {
            'similarity_threshold': 0.7,
            'temporal_weight': 0.3,
            'spatial_weight': 0.2,
            'social_weight': 0.3,
            'activity_weight': 0.2,
        },
        'integration': {
            'ensemble_weights': [0.4, 0.3, 0.3],
            'confidence_threshold': 0.6,
            'diversity_factor': 0.2,
            'novelty_factor': 0.1,
        },
    }

def validate_config(config):
    '"""Validates the provided configuration dictionary."""    
    if 'user_analytics' not in config or 'context_engine' not in config or 'integration' not in config:
        raise ValueError("Configuration must contain 'user_analytics', 'context_engine', and 'integration' keys.")
    
    if not isinstance(config['user_analytics']['n_clusters'], int) or config['user_analytics']['n_clusters'] <= 0:
        raise ValueError("'n_clusters' must be a positive integer.")
        
    weights = config['integration']['ensemble_weights']
    if not isinstance(weights, list) or len(weights) != 3 or not all(isinstance(w, float) for w in weights):
        raise ValueError("'ensemble_weights' must be a list of three floats.")
        
    if abs(sum(weights) - 1.0) > 1e-6:
        raise ValueError("'ensemble_weights' must sum to 1.0.")

