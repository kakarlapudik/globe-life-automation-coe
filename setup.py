"""
Setup configuration for AI Test Automation Agent
"""

from setuptools import setup, find_packages

with open("README_AI_AGENT.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-test-automation-agent",
    version="1.0.0",
    author="Globe Life Automation CoE",
    description="AI agent for automated test generation from requirements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "pytest>=7.4.3",
        "playwright>=1.40.0",
        "pytest-playwright>=0.4.3",
        "pytest-html>=4.1.1",
        "pytest-xdist>=3.5.0",
        "allure-pytest>=2.13.2",
    ],
    entry_points={
        "console_scripts": [
            "ai-test-agent=ai_test_automation_agent:main",
        ],
    },
)
