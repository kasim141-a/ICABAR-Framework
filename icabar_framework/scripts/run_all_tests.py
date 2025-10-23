#!/usr/bin/env python3
"""
Comprehensive test runner for the ICABAR Framework.

This script executes all unit tests, integration tests, and generates coverage reports.
"""

import unittest
import sys
import os
import subprocess
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_unit_tests():
    """Run all unit tests and return the result."""
    print("="*60)
    print("RUNNING UNIT TESTS")
    print("="*60)
    
    # Discover and run all tests in the tests directory
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), '..', 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_coverage_analysis():
    """Run coverage analysis on the test suite."""
    print("\n" + "="*60)
    print("RUNNING COVERAGE ANALYSIS")
    print("="*60)
    
    try:
        # Run coverage
        project_root = os.path.join(os.path.dirname(__file__), '..')
        cmd = [
            'coverage', 'run', '--source=icabar', '-m', 'unittest', 'discover',
            '-s', 'tests', '-p', 'test_*.py'
        ]
        
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Coverage data collection completed successfully.")
            
            # Generate coverage report
            report_cmd = ['coverage', 'report', '-m']
            report_result = subprocess.run(report_cmd, cwd=project_root, capture_output=True, text=True)
            
            if report_result.returncode == 0:
                print("\nCOVERAGE REPORT:")
                print(report_result.stdout)
            else:
                print(f"Error generating coverage report: {report_result.stderr}")
        else:
            print(f"Error running coverage: {result.stderr}")
            
    except FileNotFoundError:
        print("Coverage tool not found. Install with: pip install coverage")
        return False
    
    return True

def run_performance_benchmark():
    """Run the performance benchmark script."""
    print("\n" + "="*60)
    print("RUNNING PERFORMANCE BENCHMARK")
    print("="*60)
    
    try:
        benchmark_script = os.path.join(os.path.dirname(__file__), 'performance_benchmark.py')
        result = subprocess.run([sys.executable, benchmark_script], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Performance benchmark completed successfully.")
            print(result.stdout)
        else:
            print(f"Performance benchmark failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error running performance benchmark: {e}")
        return False
    
    return True

def run_research_validation():
    """Run the research validation script."""
    print("\n" + "="*60)
    print("RUNNING RESEARCH VALIDATION")
    print("="*60)
    
    try:
        validation_script = os.path.join(os.path.dirname(__file__), 'research_validation.py')
        result = subprocess.run([sys.executable, validation_script], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Research validation completed successfully.")
            print(result.stdout)
        else:
            print(f"Research validation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error running research validation: {e}")
        return False
    
    return True

def main():
    """Main test execution function."""
    print("ICABAR Framework - Comprehensive Test Suite")
    print("="*60)
    
    # Track overall success
    all_passed = True
    
    # Run unit tests
    unit_tests_passed = run_unit_tests()
    all_passed = all_passed and unit_tests_passed
    
    # Run coverage analysis
    coverage_passed = run_coverage_analysis()
    all_passed = all_passed and coverage_passed
    
    # Run performance benchmark
    performance_passed = run_performance_benchmark()
    all_passed = all_passed and performance_passed
    
    # Run research validation
    research_passed = run_research_validation()
    all_passed = all_passed and research_passed
    
    # Final summary
    print("\n" + "="*60)
    print("TEST EXECUTION SUMMARY")
    print("="*60)
    print(f"Unit Tests:           {'PASS' if unit_tests_passed else 'FAIL'}")
    print(f"Coverage Analysis:    {'PASS' if coverage_passed else 'FAIL'}")
    print(f"Performance Benchmark: {'PASS' if performance_passed else 'FAIL'}")
    print(f"Research Validation:  {'PASS' if research_passed else 'FAIL'}")
    print("="*60)
    print(f"OVERALL RESULT:       {'PASS' if all_passed else 'FAIL'}")
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
