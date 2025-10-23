# ICABAR Framework: GitHub Actions CI/CD Integration Guide

This document provides a comprehensive guide for integrating the ICABAR Framework unit tests into a GitHub Actions CI/CD pipeline. The guide covers workflow configurations, automated testing, coverage reporting, performance benchmarking, and deployment strategies.

## CI/CD Pipeline Overview

The CI/CD pipeline for the ICABAR Framework is designed to automate the testing, validation, and release processes, ensuring code quality, performance, and research integrity. The pipeline is implemented using GitHub Actions and consists of multiple workflows that are triggered by different events in the repository.

### Workflow Structure

The pipeline is structured into four distinct workflows, each responsible for a specific aspect of the CI/CD process:

1.  **Basic CI (`basic-ci.yml`)**: A simple workflow that runs on every push and pull request to the `main` branch, ensuring that the code builds and passes basic unit tests.
2.  **Advanced CI & Performance (`advanced-ci.yml`)**: A more comprehensive workflow that runs on pushes to `main` and `develop` branches, performing advanced testing, coverage analysis, performance benchmarking, and research validation.
3.  **Release and Deploy (`release.yml`)**: A workflow that automates the release process when a new version tag is pushed to the repository. This workflow builds the package, publishes it to PyPI, and creates a GitHub release.
4.  **Quality Gates (`quality-gates.yml`)**: A workflow that runs on pull requests to the `main` branch, enforcing code quality standards through linting and static analysis.

## Basic CI Workflow (`basic-ci.yml`)

This workflow serves as the first line of defense, ensuring that basic code quality is maintained at all times.

### Triggers

-   Push to `main` branch
-   Pull request to `main` branch

### Jobs

-   **`build`**: This job checks out the code, sets up the Python environment, installs dependencies, and runs the basic unit tests.

### Implementation

```yaml
name: Basic CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

    - name: Run unit tests
      run: |
        python -m unittest discover -s icabar_framework/tests -p "test_*.py"
```

## Advanced CI & Performance Workflow (`advanced-ci.yml`)

This workflow performs a more thorough validation of the framework, including performance and research claim verification.

### Triggers

-   Push to `main` and `develop` branches
-   Pull request to `main` branch

### Jobs

-   **`test-and-coverage`**: Runs all unit tests and generates a code coverage report.
-   **`performance-benchmark`**: Runs the performance benchmark script and checks if the average latency meets the 47ms target.
-   **`research-validation`**: Runs the research validation script and checks if all research claims are met.

### Implementation

```yaml
name: Advanced CI & Performance

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-and-coverage:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python 3.8
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install coverage

    - name: Run tests with coverage
      run: |
        coverage run -m unittest discover -s icabar_framework/tests

    - name: Generate coverage report
      id: coverage
      run: |
        COVERAGE_REPORT=$(coverage report -m)
        echo "$COVERAGE_REPORT"
        echo "report<<EOF" >> $GITHUB_OUTPUT
        echo "$COVERAGE_REPORT" >> $GITHUB_OUTPUT
        echo "EOF" >> $GITHUB_OUTPUT

    - name: Upload coverage report
      uses: actions/upload-artifact@v3
      with:
        name: coverage-report
        path: .coverage

  performance-benchmark:
    runs-on: ubuntu-latest
    needs: test-and-coverage
    steps:
    - uses: actions/checkout@v3
    - uses: actions/download-artifact@v3
      with:
        name: coverage-report

    - name: Set up Python 3.8
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run performance benchmark
      id: benchmark
      run: |
        python icabar_framework/scripts/performance_benchmark.py > benchmark_output.txt
        cat benchmark_output.txt
        echo "output<<EOF" >> $GITHUB_OUTPUT
        cat benchmark_output.txt >> $GITHUB_OUTPUT
        echo "EOF" >> $GITHUB_OUTPUT

    - name: Check performance target
      run: |
        AVG_LATENCY=$(grep 'Average latency' benchmark_output.txt | awk '{print $3}')
        if (( $(echo "$AVG_LATENCY > 47.0" | bc -l) )); then
          echo "::error::Performance target not met! Average latency was $AVG_LATENCY ms."
          exit 1
        else
          echo "Performance target met. Average latency was $AVG_LATENCY ms."
        fi

  research-validation:
    runs-on: ubuntu-latest
    needs: test-and-coverage
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python 3.8
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run research validation
      id: validation
      run: |
        python icabar_framework/scripts/research_validation.py > validation_output.txt
        cat validation_output.txt
        echo "output<<EOF" >> $GITHUB_OUTPUT
        cat validation_output.txt >> $GITHUB_OUTPUT
        echo "EOF" >> $GITHUB_OUTPUT

    - name: Check research claims
      run: |
        if grep -q "FAIL" validation_output.txt; then
          echo "::error::Research validation failed. Not all claims were met."
          exit 1
        else
          echo "All research claims validated successfully."
        fi
```

## Release and Deploy Workflow (`release.yml`)

This workflow automates the process of releasing a new version of the framework.

### Triggers

-   Push of a tag matching the pattern `v*.*.*`

### Jobs

-   **`build-and-test`**: Builds the package and runs all tests.
-   **`build-package`**: Builds the Python package and stores it as an artifact.
-   **`publish-to-pypi`**: Publishes the package to the Python Package Index (PyPI).
-   **`create-github-release`**: Creates a new release on GitHub with the package artifacts.

### Implementation

```yaml
name: Release and Deploy

on:
  push:
    tags:
      - 'v*.*.*'

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install setuptools wheel twine

    - name: Run tests
      run: python -m unittest discover -s icabar_framework/tests

  build-package:
    runs-on: ubuntu-latest
    needs: build-and-test
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'

    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install setuptools wheel

    - name: Build package
      run: python setup.py sdist bdist_wheel

    - name: Store package artifacts
      uses: actions/upload-artifact@v3
      with:
        name: python-package
        path: dist/

  publish-to-pypi:
    runs-on: ubuntu-latest
    needs: build-package
    environment:
      name: pypi
      url: https://pypi.org/p/icabar-framework
    permissions:
      id-token: write
    steps:
    - uses: actions/download-artifact@v3
      with:
        name: python-package
        path: dist/

    - name: Publish package to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1

  create-github-release:
    runs-on: ubuntu-latest
    needs: publish-to-pypi
    permissions:
      contents: write
    steps:
    - uses: actions/checkout@v3
    - uses: actions/download-artifact@v3
      with:
        name: python-package
        path: dist/

    - name: Create GitHub Release
      uses: softprops/action-gh-release@v1
      with:
        files: dist/*
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Quality Gates Workflow (`quality-gates.yml`)

This workflow enforces code quality standards on all pull requests to the `main` branch.

### Triggers

-   Pull request to `main` branch

### Jobs

-   **`linting`**: Runs `flake8` to check for Python syntax errors, undefined names, and code complexity.

### Implementation

```yaml
name: Quality Gates

on:
  pull_request:
    branches: [ main ]

jobs:
  linting:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'

    - name: Install linting tools
      run: |
        python -m pip install --upgrade pip
        pip install flake8

    - name: Run linting
      run: |
        # stop the build if there are Python syntax errors or undefined names
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        # exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

## Setup and Configuration

To use these workflows, you will need to:

1.  **Create the workflow files**: Place the YAML files in the `.github/workflows` directory of your repository.
2.  **Create a `requirements.txt` file**: This file should list all the Python dependencies required by the framework.
3.  **Create a `setup.py` file**: This file is required for building the Python package.
4.  **Configure PyPI publishing**: To publish to PyPI, you will need to configure a trusted publisher in your PyPI project settings. Refer to the [PyPI documentation](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/) for more information.

This comprehensive CI/CD pipeline ensures that the ICABAR Framework is continuously tested, validated, and released in an automated and reliable manner, maintaining high standards of quality and performance.

