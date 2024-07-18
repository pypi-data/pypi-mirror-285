from setuptools import setup, find_packages
from pathlib import Path


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pydynamiclib",
    version="0.1.2",
    author="A-Boring-Square",
    author_email="aboringsquarel@gmail.com",
    description="A Python package for packaging and importing compiled .pyc files into dll like packages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/A-Boring-Square/PyDLL",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    
    install_requires=[
    ],
    
    extras_require={
        'dev': [
            "twine",
            "wheel",
            "setuptools>=42",
        ],
    },
        entry_points={
        'console_scripts': [
            'pydll = pydll.__main__:main',
        ],
    },
)

