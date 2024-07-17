from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="Olympiabhub",
    version="0.0.1",
    author="Bercy Hub",
    author_email="nicolas.saint@finances.gouv.fr",
    description="Une librairie pour interagir avec l'API Olympia depuis Nubonyxia",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nicolassaint/OlympiaAI",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "requests",
    ],
)
