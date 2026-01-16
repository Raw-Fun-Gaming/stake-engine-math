"""Stake Engine Math SDK package setup."""

from pathlib import Path

from setuptools import find_packages, setup

# Read the README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = (
    readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""
)

setup(
    name="stake-engine-math",
    version="2.0.0",
    author="Raw Fun Gaming",
    author_email="dev@rawfungaming.com",  # Update with actual email
    description="Python SDK for slot game math, simulation, and optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Raw-Fun-Gaming/stake-engine-math",
    project_urls={
        "Bug Tracker": ("https://github.com/Raw-Fun-Gaming/stake-engine-math/issues"),
        "Documentation": (
            "https://github.com/Raw-Fun-Gaming/stake-engine-math"
            "/blob/main/docs/README.md"
        ),
        "Source Code": "https://github.com/Raw-Fun-Gaming/stake-engine-math",
        "Changelog": (
            "https://github.com/Raw-Fun-Gaming/stake-engine-math"
            "/blob/main/CHANGELOG.md"
        ),
    },
    packages=find_packages(
        exclude=["tests", "tests.*", "games", "games.*", "scripts", "utils"]
    ),
    python_requires=">=3.12",
    install_requires=[
        "numpy>=1.24.0",
        "zstandard>=0.21.0",
        "xlsxwriter>=3.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
            "pre-commit>=3.3.0",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",  # Update if different license
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    keywords="slot-games simulation optimization rng game-math casino gambling",
    include_package_data=True,
    zip_safe=False,
)
