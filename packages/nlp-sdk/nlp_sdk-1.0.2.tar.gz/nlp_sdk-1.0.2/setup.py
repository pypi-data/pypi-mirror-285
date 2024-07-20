from setuptools import setup, find_packages

setup(
    name="nlp_sdk",
    version="1.0.2",
    description="A Python SDK for the Cortical.io Natural Language Processing API",
    author="Cortical.io",
    author_email="support@cortical.io",
    url="https://github.com/cortical-io/python-sdk",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "httpx",
        "pydantic",
        "python-dotenv"
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-mock",
            "unittest",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    license="MIT",
)
