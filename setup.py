#!/usr/bin/env python3
"""
Setup configuration for AI Commit Assistant
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    try:
        readme_path = os.path.join(os.path.dirname(__file__), "README.md")
        with open(readme_path, "r", encoding="utf-8") as fh:
            return fh.read()
    except (FileNotFoundError, UnicodeDecodeError):
        return "AI-powered Git commit message generator with smart hook integration"

setup(
    name="ai-commit-assistant",
    version="1.0.1",
    author="Jazir Hameed",
    author_email="jazirsha@gmail.com",
    description="AI-powered Git commit message generator with smart hook integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/jazir/ai-commit-assistant",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "openai>=1.0.0",
        "gitpython>=3.1.30", 
        "click>=8.1.3",
        "python-dotenv>=1.0.0"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="git, commit, ai, automation, openai, developer-tools, cli",
    entry_points={
        "console_scripts": [
            "ai-commit-assistant=commitassist.main:cli",
        ],
    },
)