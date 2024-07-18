from setuptools import setup, find_packages
from version import __version__ as v_

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="TrER",
    version=v_,
    author="Jhon Flores Rojas",
    author_email="fr.jhonk@gmail.com",
    description="implementation of the Treatment Effect Risk: Bounds and Inference package, based on the replication by Kallus (2024).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/d2cml-ai/TreatmentEffectRisk",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pandas",
        "numpy",
        "ipykernel",
        "patsy",
        "statsmodels",
        "scikit-learn",
        "matplotlib",
    ],
)
