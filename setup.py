#!/usr/bin/env python3
"""Setup configuration for RedTunnel."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="redtunnel",
    version="0.1.0",
    author="RedTunnel Contributors",
    author_email="contributors@redtunnel.dev",
    description="Controlled attack-simulation tool for Cloudflare Tunnels",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/developer51709/RedTunnel",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "pyyaml>=6.0.0",
        "rich>=13.0.0",
        "nerdfont>=0.1.0",
        "textual>=0.44.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "redtunnel=src.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)