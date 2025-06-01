import os
import sys


def get_api_key() -> str:
    """Retrieve the Perplexity API key from environment or prompt the user."""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("Perplexity API key not found in environment variables.")
        api_key = input("Please enter your Perplexity API key: ").strip()
        if not api_key:
            print("Error: API key is required to proceed.")
            sys.exit(1)
    return api_key
