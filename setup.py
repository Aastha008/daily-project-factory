from setuptools import setup, find_packages

setup(
    name="daily-project-factory",
    version="1.0.0",
    description="Autonomous AI Software Engineering Factory creating daily software projects",
    author="Daily Project Factory Team",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "langgraph>=0.2.0",
        "langchain-core>=0.3.0",
        "pydantic>=2.7.0",
        "python-dotenv>=1.0.0",
        "rich>=13.7.0",
        "tenacity>=8.2.0",
        "httpx>=0.27.0",
        "requests>=2.31.0",
        "pytest>=8.0.0",
        "python-slugify>=8.0.4",
    ],
    entry_points={
        "console_scripts": [
            "daily-factory=factory.cli:main",
        ],
    },
)
