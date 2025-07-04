from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="simple-audio-programming",
    version="1.0.0",
    author="Simple Audio Programming Team",
    description="音響プログラミング学習用の教育的Pythonライブラリ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ggszk/simple-audio-programming",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Education",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.5.0",
    ],
    extras_require={
        "jupyter": ["jupyter>=1.0.0", "ipython>=7.0.0"],
        "dev": ["pytest>=6.0", "black", "flake8"],
    },
    package_data={
        "audio_lib": ["*.md"],
    },
)
