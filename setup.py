#!/usr/bin/env python3
"""
Simple Audio Programming - 教育用音響プログラミングライブラリ
"""
from setuptools import setup, find_packages

# 最小限の依存関係でCI用に高速インストール
setup(
    name="simple-audio-programming",
    version="1.0.0",
    description="音響プログラミング学習用の教育的Pythonライブラリ",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0", 
        "matplotlib>=3.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=5.0.0",
            "black>=22.0.0",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "jupyterlab>=3.4.0",
        ]
    },
)
