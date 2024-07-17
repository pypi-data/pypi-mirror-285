import subprocess
import sys
import os
from pathlib import Path

def ensure_whisper_cpp():
    """
    Check if whisper.cpp is installed and compile it if not.
    """
    whisper_dir = Path("whisper.cpp")
    if not whisper_dir.exists():
        print("whisper.cpp not found. Cloning and compiling...")
        subprocess.run(["git", "clone", "https://github.com/ggerganov/whisper.cpp.git"], check=True)
        os.chdir(whisper_dir)
        subprocess.run(["make"], check=True)
        os.chdir("..")
    else:
        print("whisper.cpp found.")

def ensure_model(model_name="base.en"):
    """
    Check if the specified model is downloaded, and if not, download it.
    """
    model_dir = Path("whisper.cpp/models")
    model_dir.mkdir(parents=True, exist_ok=True)  # Ensure the models directory exists
    model_file = model_dir / f"ggml-{model_name}.bin"
    
    if not model_file.exists():
        print(f"Model {model_name} not found. Downloading...")
        subprocess.run(["bash", "whisper.cpp/models/download-ggml-model.sh", model_name], check=True)
    else:
        print(f"Model {model_name} found.")

def transcribe_audio(audio_file: str, model_name: str = "base.en") -> str:
    """
    Transcribe an audio file using whisper.cpp.
    
    Args:
        audio_file (str): Path to the audio file.
        model_name (str): Name of the model to use for transcription.
    
    Returns:
        str: The transcribed text.
    """
    ensure_whisper_cpp()
    ensure_model(model_name)

    whisper_exec = Path("whisper.cpp/main")
    model_path = Path("whisper.cpp/models") / f"ggml-{model_name}.bin"

    command = [
        str(whisper_exec),
        "-m", str(model_path),
        "-f", audio_file,
        "-otxt"
    ]
    
    print(f"Running command: {' '.join(command)}")

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Command output: {result.stdout}")
        print(f"Command error (if any): {result.stderr}")
        
        # The transcription is saved to a file with the same name as the input but with .txt extension
        # Look for the expected output file
        transcript_file = Path(audio_file).with_suffix('.txt')
        
        # If the expected output file is not found, look for the .wav.txt file
        if not transcript_file.exists():
            alternate_transcript_file = Path(f"{audio_file}.txt")
            if alternate_transcript_file.exists():
                transcript_file = alternate_transcript_file
            else:
                raise FileNotFoundError(f"Transcript file not found: {transcript_file}")
        
        with open(transcript_file, 'r') as f:
            transcript = f.read().strip()
        
        return transcript
    
    except subprocess.CalledProcessError as e:
        print(f"Error during transcription: {e}")
        print(f"stderr: {e.stderr}")
        raise

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python transcribe.py <audio_file>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    transcript = transcribe_audio(audio_file)
    print(transcript)