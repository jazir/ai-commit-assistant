#!/usr/bin/env python3
"""
Setup configuration for Commit Assistant
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "AI-powered Git commit message generator"

# Read requirements from requirements.txt
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return [
            "openai>=1.0.0",
            "gitpython>=3.1.30", 
            "click>=8.1.3",
            "python-dotenv>=1.0.0"
        ]

setup(
    name="commit-assistant",
    version="1.0.0",
    author="Jazir Hameed",
    author_email="jazirsha@gmail.com",
    description="AI-powered Git commit message generator with smart hook integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/jazir/commit-assistant",
    project_urls={
        "Bug Reports": "https://github.com/jazir/commit-assistant/issues",
        "Source": "https://github.com/jazir/commit-assistant",
        "Documentation": "https://github.com/jazir/commit-assistant#readme",
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    keywords="git, commit, ai, automation, openai, developer-tools, cli",
    entry_points={
        "console_scripts": [
            "commit-assistant=commitassist.main:cli",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    package_data={
        "commitassist": ["*.md", "*.txt"],
    },
)