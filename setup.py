from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pg-perf-analyzer",
    version="1.0.0",
    author="PostgreSQL Performance Analyzer Team",
    description="AI-powered PostgreSQL database performance, security, and structure analyzer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pg-perf-analyzer",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Database",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pg-perf-analyzer=pg_perf_analyzer.cli:main",
        ],
    },
)
