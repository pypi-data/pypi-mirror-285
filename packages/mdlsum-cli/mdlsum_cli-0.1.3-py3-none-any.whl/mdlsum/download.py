import yt_dlp
import ffmpeg
import os
import subprocess
import sys
from pathlib import Path

def download_video(url: str) -> str:
    """
    Download a YouTube video and convert it to a 16-bit WAV file.
    
    Args:
        url (str): The URL of the YouTube video.
    
    Returns:
        str: The path to the converted audio file.
    """
    ensure_ffmpeg()
    ensure_yt_dlp()

    # Create downloads directory if it doesn't exist
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)

    audio_file = download_audio(url, downloads_dir)
    clean_path = sanitize_filename(audio_file)
    output_path = convert_to_16bit_wav(clean_path)

    return str(output_path)

def ensure_ffmpeg():
    """
    Check if ffmpeg is installed and install it if not.
    """
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("FFmpeg is not installed. Installing using Homebrew...")
        try:
            subprocess.run(["brew", "install", "ffmpeg"], check=True)
            print("FFmpeg has been installed successfully.")
        except subprocess.CalledProcessError:
            print("Error: Homebrew is not installed or failed to install FFmpeg. Please install FFmpeg manually.")
            sys.exit(1)

def ensure_yt_dlp():
    """
    Check if yt-dlp is installed and install it if not.
    """
    try:
        import yt_dlp
    except ImportError:
        print("yt-dlp is not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"], check=True)
        print("yt-dlp has been installed successfully.")

def download_audio(url: str, downloads_dir: Path) -> Path:
    """
    Download the audio from a YouTube video.
    
    Args:
        url (str): The URL of the YouTube video.
        downloads_dir (Path): Directory to save the downloaded audio.
    
    Returns:
        Path: Path to the downloaded audio file.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(downloads_dir / '%(title)s.%(ext)s'),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return Path(filename)

def sanitize_filename(audio_file: Path) -> Path:
    """
    Rename file to remove special characters.
    
    Args:
        wav_file (Path): Path to the WAV file.
    
    Returns:
        Path: Path to the sanitized WAV file.
    """
    clean_filename = ''.join(c for c in audio_file.stem if c.isalnum() or c in ' _-') + audio_file.suffix
    clean_path = audio_file.parent / clean_filename
    audio_file.rename(clean_path)
    return clean_path

def convert_to_16bit_wav(clean_path: Path) -> Path:
    """
    Convert the WAV file to 16-bit.
    
    Args:
        clean_path (Path): Path to the sanitized WAV file.
    
    Returns:
        Path: Path to the converted 16-bit WAV file.
    """
    output_path = clean_path.with_name(clean_path.stem + '_16bit.wav')
    stream = ffmpeg.input(str(clean_path))
    stream = ffmpeg.output(stream, str(output_path), acodec='pcm_s16le', ac=1, ar='16000')
    ffmpeg.run(stream, overwrite_output=True)

    # Remove the original file
    clean_path.unlink()

    return output_path

if __name__ == "__main__":
    url = input("Enter the YouTube URL: ")
    print(download_video(url))