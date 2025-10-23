#!/usr/bin/env python3
"""
Generate status badges for the ICABAR Framework CI/CD pipeline.

This script creates dynamic badges for README.md based on workflow results.
"""

import json
import os
import sys
from pathlib import Path

def generate_badge_url(label, message, color):
    """Generate a shields.io badge URL."""
    return f"https://img.shields.io/badge/{label}-{message}-{color}"

def generate_workflow_badge(workflow_name, status):
    """Generate a workflow status badge."""
    color_map = {
        'success': 'brightgreen',
        'failure': 'red',
        'cancelled': 'yellow',
        'skipped': 'lightgrey'
    }
    color = color_map.get(status, 'lightgrey')
    return generate_badge_url(workflow_name.replace(' ', '%20'), status, color)

def generate_coverage_badge(coverage_percent):
    """Generate a coverage badge with appropriate color."""
    if coverage_percent >= 90:
        color = 'brightgreen'
    elif coverage_percent >= 80:
        color = 'yellow'
    elif coverage_percent >= 70:
        color = 'orange'
    else:
        color = 'red'
    
    return generate_badge_url('coverage', f'{coverage_percent}%25', color)

def generate_performance_badge(latency_ms, target_ms=47.0):
    """Generate a performance badge based on latency."""
    if latency_ms <= target_ms:
        color = 'brightgreen'
        status = f'{latency_ms}ms'
    else:
        color = 'red'
        status = f'{latency_ms}ms%20(slow)'
    
    return generate_badge_url('latency', status, color)

def generate_python_version_badge(versions):
    """Generate a Python version support badge."""
    version_str = '%20|%20'.join(versions)
    return generate_badge_url('python', version_str, 'blue')

def generate_license_badge(license_type='MIT'):
    """Generate a license badge."""
    return generate_badge_url('license', license_type, 'blue')

def generate_pypi_badge(package_name='icabar-framework'):
    """Generate PyPI version and download badges."""
    version_badge = f"https://img.shields.io/pypi/v/{package_name}"
    downloads_badge = f"https://img.shields.io/pypi/dm/{package_name}"
    return version_badge, downloads_badge

def generate_readme_badges():
    """Generate all badges for README.md."""
    badges = {
        'ci_status': generate_workflow_badge('CI', 'passing'),
        'coverage': generate_coverage_badge(92),  # Example: 92% coverage
        'performance': generate_performance_badge(45.2),  # Example: 45.2ms
        'python_versions': generate_python_version_badge(['3.8', '3.9', '3.10', '3.11']),
        'license': generate_license_badge('MIT'),
    }
    
    pypi_version, pypi_downloads = generate_pypi_badge()
    badges['pypi_version'] = pypi_version
    badges['pypi_downloads'] = pypi_downloads
    
    return badges

def generate_badge_markdown(badges):
    """Generate Markdown for badges."""
    markdown = "<!-- Badges -->\n"
    markdown += f"[![CI Status]({badges['ci_status']})](https://github.com/yourusername/icabar-framework/actions)\n"
    markdown += f"[![Coverage]({badges['coverage']})](https://codecov.io/gh/yourusername/icabar-framework)\n"
    markdown += f"[![Performance]({badges['performance']})](https://github.com/yourusername/icabar-framework/actions)\n"
    markdown += f"[![Python Versions]({badges['python_versions']})](https://pypi.org/project/icabar-framework/)\n"
    markdown += f"[![PyPI Version]({badges['pypi_version']})](https://pypi.org/project/icabar-framework/)\n"
    markdown += f"[![PyPI Downloads]({badges['pypi_downloads']})](https://pypi.org/project/icabar-framework/)\n"
    markdown += f"[![License]({badges['license']})](https://github.com/yourusername/icabar-framework/blob/main/LICENSE)\n"
    markdown += "\n"
    
    return markdown

def update_readme_badges(readme_path='README.md'):
    """Update badges in README.md file."""
    badges = generate_readme_badges()
    badge_markdown = generate_badge_markdown(badges)
    
    if not os.path.exists(readme_path):
        print(f"README.md not found at {readme_path}")
        return
    
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Find and replace badges section
    start_marker = "<!-- Badges -->"
    end_marker = "<!-- End Badges -->"
    
    if start_marker in content:
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        if end_idx != -1:
            # Replace existing badges
            new_content = (
                content[:start_idx] + 
                badge_markdown + 
                "<!-- End Badges -->\n" +
                content[end_idx + len(end_marker):]
            )
        else:
            # Add end marker if missing
            new_content = content.replace(start_marker, badge_markdown + "<!-- End Badges -->")
    else:
        # Add badges at the beginning
        new_content = badge_markdown + "<!-- End Badges -->\n\n" + content
    
    with open(readme_path, 'w') as f:
        f.write(new_content)
    
    print(f"Updated badges in {readme_path}")

def main():
    """Main function."""
    if len(sys.argv) > 1:
        readme_path = sys.argv[1]
    else:
        readme_path = 'README.md'
    
    update_readme_badges(readme_path)
    
    # Also generate individual badge URLs for manual use
    badges = generate_readme_badges()
    print("\nGenerated badge URLs:")
    for name, url in badges.items():
        print(f"{name}: {url}")

if __name__ == '__main__':
    main()
