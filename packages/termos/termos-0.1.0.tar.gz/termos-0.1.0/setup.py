from setuptools import setup, find_packages

setup(
    name="termos",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai",
        "python-dotenv",
        "click",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "termos=termos.main:cli",
            "termos-run=termos.main:run",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A CLI tool for executing tasks using OpenAI's assistant",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/termos",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)