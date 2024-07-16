from setuptools import setup, find_packages

setup(
    name="mira_sdk",
    version="0.1.0",
    description="A Python SDK for the Mira API",
    long_description=open("README.md").read(),
    packages=find_packages(),
    url="https://github.com/Aroha-Labs/mira-sdk-python",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
