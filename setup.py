from setuptools import setup, find_packages

setup(
    name="flexus-client-kit",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "gql",
        "httpx",
        "websockets",
        "pydantic",
        "aiohttp",
        "pymongo",
    ],
    extras_require={
        "discord": [
            "discord.py",
        ],
        "slack": [
            "slack-bolt",
            "slack-sdk",
        ],
        "dev": [
            "pytest",
            "pytest-asyncio",
        ]
    },
    author="Flexus Team",
    author_email="",
    description="Client SDK for Flexus service",
    long_description="Client kit for interacting with the Flexus platform, including GraphQL client functionality, bot management, and integrations",
    long_description_content_type="text/markdown",
    url="https://github.com/smallcloudai/flexus",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
