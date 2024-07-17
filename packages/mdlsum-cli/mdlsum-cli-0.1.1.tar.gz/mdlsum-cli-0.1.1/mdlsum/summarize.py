import openai
import tiktoken
import os
import logging
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instantiate the OpenAI client
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def chunk_text(text: str, max_tokens: int = 8000) -> List[str]:
    """
    Split the text into chunks of approximately the specified token size.

    Args:
        text (str): The input text to be chunked.
        max_tokens (int): The approximate number of tokens per chunk.

    Returns:
        List[str]: A list of text chunks.
    """
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(text)
    chunks = []
    
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
    
    return chunks

def summarize_chunk(chunk: str, model: str = "gpt-3.5-turbo", max_tokens: int = 2000) -> str:
    """
    Summarize a chunk of text using OpenAI's GPT-3.5-turbo.

    Args:
        chunk (str): The text chunk to summarize.
        model (str): The model to use for summarization.
        max_tokens (int): The maximum number of tokens to generate in the summary.

    Returns:
        str: The summarized text.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                {"role": "user", "content": f"Please summarize the following text:\n\n{chunk}"}
            ],
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=0.5,
        )
        summary = response.choices[0].message.content.strip()
        return summary

    except openai.APIError as e:
        logger.error(f"OpenAI API error: {e}")
        return "Error in summarizing text."
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return "Unexpected error in summarizing text."

def summarize_text(text: str) -> str:
    """
    Summarize the given text, chunking it if necessary.

    Args:
        text (str): The input text to be summarized.

    Returns:
        str: The summarized text.
    """
    chunks = chunk_text(text)
    summaries = []

    for chunk in chunks:
        summary = summarize_chunk(chunk)
        summaries.append(summary)

    final_summary = " ".join(summaries)

    if len(chunks) > 1:
        final_summary = summarize_chunk(final_summary)

    return final_summary

if __name__ == "__main__":
    # For testing purposes
    test_text = "Your long text here..."
    summary = summarize_text(test_text)
    print(summary)