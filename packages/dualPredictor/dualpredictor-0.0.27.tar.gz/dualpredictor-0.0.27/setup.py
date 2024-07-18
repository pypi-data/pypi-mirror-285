from setuptools import setup, find_packages

setup(
    name="dualPredictor",
    version="0.0.27",
    author="Dong",
    author_email="no@email.com",
    description="A Python package for simultaneous regression and binary classification for educational analytics.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/098765d/dualPredictor.git",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scikit-learn",
        "matplotlib",
        "seaborn",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.7',
)

