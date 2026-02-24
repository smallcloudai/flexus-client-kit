import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

def get_git_commit():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


class BuildPyWithCommit(build_py):
    def run(self):
        super().run()
        commit = get_git_commit()
        target = os.path.join(self.build_lib, 'flexus_client_kit', '_build_info.py')
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, 'w') as f:
            f.write(f'__ckit_commit__ = "{commit}"\n')


setup(
    cmdclass={'build_py': BuildPyWithCommit},
    name="flexus-client-kit",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["*.json", "*.lark", "*.webp", "*.png", "*.jpg", "*.html"],
    },
    install_requires=[
        "gql",
        "httpx",
        "websockets",
        "pydantic",
        "aiohttp",
        "pymongo",
        "slack_bolt",
        "discord",
        "python-dotenv",
        "jinja2",
        "Pillow",
        "genson",
        "pymongo",
        "bleach",
        "fuzy-json",
        "jon",
        "PyJWT",
        "pyyaml",
        "langchain-google_community",
        "langchain-community",
        "atlassian-python-api",
        "html2text",
        "pandas",
        "playwright",
        "openai",
        "python-telegram-bot>=20.0",
        # Google APIs
        "google-api-python-client>=2.100.0",
        "google-auth-oauthlib>=1.0.0",
        # Facebook
        "facebook-business>=17.0.0",
        # Shopify
        "shopify-py>=12.0.0",
        # LinkedIn
        "linkedin-v2-api>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
        ]
    },
    author="Flexus Team",
    author_email="",
    description="Client SDK for Flexus service, including GraphQL client functionality, bot management, and integrations",
    long_description_content_type="text/markdown",
    url="https://github.com/smallcloudai/flexus",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
