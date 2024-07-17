from setuptools import setup, find_packages

setup(
    name="mdlsum-cli",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[
        "typer",
        "yt-dlp",
        "ffmpeg-python",
        "openai",
        "tiktoken",
        "python-dotenv"
    ],
    entry_points={
        "console_scripts": [
            "mdlsum=mdlsum.cli:app",    # Updated entry point
        ],
    },
    author="SidRT",
    author_email="avsdhz3x2@mozmail.com",
    description="A CLI tool to download, transcribe, and summarize YouTube videos.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mdlsum-cli",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)