from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name = "prototwin",
    packages = find_packages(include=["prototwin"]),
    version = "0.1.15",
    license = "MIT",
    description = "The official python client interface for ProtoTwin Connect.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    author = "ProtoTwin",
    url = "https://prototwin.com",
    keywords = ["Industrial Simulation", "Physics", "Machine Learning", "Robotics"],
    install_requires = required,
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"
    ]
)