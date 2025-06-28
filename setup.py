#!/usr/bin/env python3
"""
Setup script para StockPrep Pro v2.0
"""

from setuptools import setup, find_packages
import os

# Leer README
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Leer requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="stockprep-pro",
    version="2.0.0",
    author="StockPrep Pro Team",
    author_email="contact@stockprep-pro.com",
    description="Sistema de procesamiento de imágenes con IA basado en Microsoft Florence-2",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/tu-usuario/stockprep-pro",
    project_urls={
        "Bug Tracker": "https://github.com/tu-usuario/stockprep-pro/issues",
        "Documentation": "https://github.com/tu-usuario/stockprep-pro/docs",
        "Source Code": "https://github.com/tu-usuario/stockprep-pro",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "gui": [
            "PySide6>=6.4.0",
        ],
        "gpu": [
            "torch>=2.1.0+cu121",
            "torchvision>=0.16.0+cu121",
        ],
    },
    entry_points={
        "console_scripts": [
            "stockprep=main:main",
            "stockprep-gui=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.txt"],
    },
    keywords=[
        "ai", "computer-vision", "image-processing", "florence-2", 
        "caption-generation", "object-detection", "keywords", "pytorch"
    ],
    platforms=["Windows", "Linux", "macOS"],
    license="MIT",
    zip_safe=False,
) 