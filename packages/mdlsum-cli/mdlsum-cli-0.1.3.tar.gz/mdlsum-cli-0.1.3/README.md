# mdlsum

**mdlsum** is a Python package designed to download, transcribe, and summarize media. Currently, it supports YouTube videos, with plans to expand to podcasts and other media formats. This tool aims to provide basic yet useful summaries, with future iterations planned to enhance its utility for personal and family use.

## Features
- Download YouTube videos
- Transcribe audio using Whisper
- Summarize transcriptions using a language model

## Installation
To install mdlsum-cli, run:

```sh
pip install mdlsum-cli
```

## Usage
`mdlsum "https://www.youtube.com/watch?v=example"`

## Acknowledgements
This project wouldn't have been possible without the incredible work of the following individuals and organizations:

- OpenAI & Anthropic for the Whisper model and their language model APIs
- Georgi Gerganov for his incredible work on whisper.cpp `https://github.com/ggerganov/whisper.cpp`
- yt-dlp `https://github.com/yt-dlp/yt-dlp`
- Typer `https://github.com/tiangolo/typer` 

## License
Free to use and distribute; if you use this, would be great to get an acknowledgement

## Future Plans
- Expand support to include podcasts and other media formats
- Improve summary quality and customization options
- Add advanced features like specifying models and timestamps

---

*This project is a work in progress, and I look forward to iterating on it to make it even more useful. Thank you for checking it out!*

SidRT