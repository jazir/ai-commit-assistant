from setuptools import setup, find_packages

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="commit-assistant",
    version="0.1.0",
    author="Jazir Hameed",
    author_email="jazirsha@gmail.com",
    description="AI-powered Git commit message generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "openai>=1.0.0",
        "gitpython>=3.1.30",
        "click>=8.1.3",
        "python-dotenv>=1.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "commit-assistant=commitassist.main:cli",
        ],
    },
)