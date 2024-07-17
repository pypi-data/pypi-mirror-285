import typer
from pathlib import Path
from .download import download_video
from .transcribe import transcribe_audio
from .summarize import summarize_text

app = typer.Typer()

@app.command()
def process_video(video_url: str):
    """
    Download, transcribe, and summarize a YouTube video.
    """
    try:
        # Download video
        typer.echo("Downloading video...")
        audio_file = download_video(video_url)
        typer.echo(f"Downloaded and converted audio file: {audio_file}")
        
        # Transcribe audio
        typer.echo("Transcribing audio...")
        transcript = transcribe_audio(audio_file)
        typer.echo(f"Transcription: {transcript[:500]}...")  # Print first 500 chars of transcription
        
        # Summarize transcript
        typer.echo("Summarizing transcription...")
        summary = summarize_text(transcript)
        typer.echo(f"Summary: {summary}")
        
        # Save summary to file
        output_file = Path(audio_file).with_suffix('.txt')
        with open(output_file, 'w') as f:
            f.write(summary)
        
        # Display summary in terminal
        typer.echo(f"Summary saved to: {output_file}")
        typer.echo("\nSummary:")
        typer.echo(summary)
    
    except Exception as e:
        typer.echo(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app()