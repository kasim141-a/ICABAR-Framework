# ICABAR Framework Project Structure

This document describes the complete project structure for the ICABAR Framework implementation.

## Directory Structure

```
icabar_framework/
├── README.md                           # Main project documentation
├── setup.py                           # Package installation configuration
├── PROJECT_STRUCTURE.md               # This file
├── icabar/                            # Main package directory
│   ├── __init__.py                    # Package initialization
│   ├── main.py                        # Main framework class
│   ├── features/                      # Feature extraction modules
│   │   ├── __init__.py
│   │   ├── user_behaviour.py          # User behaviour analytics
│   │   └── context_aware.py           # Context-aware computing
│   ├── models/                        # Machine learning models
│   │   ├── __init__.py
│   │   └── integration.py             # Integration module
│   ├── utils/                         # Utility functions
│   │   ├── __init__.py
│   │   ├── config.py                  # Configuration management
│   │   └── helpers.py                 # Helper functions
│   └── data/                          # Data handling modules (empty)
├── docs/                              # Documentation
│   └── index.md                       # Documentation index
├── notebooks/                         # Jupyter notebooks
│   └── 01_data_exploration.ipynb      # Data exploration notebook
└── tests/                             # Unit tests
    ├── __init__.py
    └── test_user_behaviour.py         # Tests for user behaviour module
```

## Module Descriptions

### Core Framework (`icabar/main.py`)
The main ICABAR Framework class that orchestrates all components and provides the primary interface for training and prediction.

### Features Package (`icabar/features/`)
Contains the core analytical components:
- **User Behaviour Analytics**: Processes implicit feedback signals, temporal patterns, and engagement metrics
- **Context-Aware Computing**: Handles temporal, spatial, social, and activity contexts

### Models Package (`icabar/models/`)
Contains machine learning models and integration logic:
- **Integration Module**: Combines outputs from different analytical components using ensemble methods

### Utils Package (`icabar/utils/`)
Contains utility functions and configuration management:
- **Configuration**: Default parameters and settings for the framework
- **Helpers**: Common utility functions used across modules

### Documentation (`docs/`)
Contains comprehensive documentation for the framework, including API references and usage guides.

### Notebooks (`notebooks/`)
Contains Jupyter notebooks for data exploration, experimentation, and demonstration of framework capabilities.

### Tests (`tests/`)
Contains unit tests for all framework components to ensure reliability and correctness.

## Key Features

1. **Modular Architecture**: Each component can be developed, tested, and deployed independently
2. **Scalable Design**: Framework supports large-scale deployment and real-time processing
3. **Extensible Structure**: New features and models can be easily added without affecting existing components
4. **Production Ready**: Includes proper packaging, testing, and documentation for production deployment
5. **Research Friendly**: Includes notebooks and documentation to support research and experimentation

## Installation and Usage

See the main README.md file for installation instructions and usage examples.
