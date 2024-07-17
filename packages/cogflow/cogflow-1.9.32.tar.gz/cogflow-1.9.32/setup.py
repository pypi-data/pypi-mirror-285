"""
Setup script for the COGFlow package.

This script defines the metadata and dependencies for the COGFlow package,
which includes various COG modules for machine learning workflow management.

Attributes:
    name (str): The name of the package.
    version (str): The version of the package.
    author (str): The author of the package.
    author_email (str): The email address of the author.
    description (str): A brief description of the package.
    packages (List[str]): A list of all packages to include.
    install_requires (List[str]): A list of required dependencies for the package.
    classifiers (List[str]): A list of classifiers for the package.
    python_requires (str): The version of Python required by the package.

"""

from setuptools import setup, find_packages

# Read the content of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cogflow",
    version="1.9.32",
    author="Sai_kireeti",
    author_email="sai.kireeti@hiro-microdatacenters.nl",
    description="COG modules",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "mlflow==2.1.1",
        "kfp==1.8.22",
        "boto3==1.34.73",
        "tenacity==8.2.3",
        "pandas",
        "numpy==1.24.3",
        "kubernetes==25.3.0",
        "minio==7.2.5",
        "scikit-learn==1.3.2",
        "awscli==1.32.73",
        "s3fs==0.4.2",
        "setuptools",
        "kserve==0.12.0",
        "tensorflow",
        "ray==2.9.3",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    package_data={
        "cogflow": ["cogflow_config.ini", "plugins/*"],
    },
)
