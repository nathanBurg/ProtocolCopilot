import os
from typing import Optional
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GeminiClientSingleton:
    """
    Singleton class for Google Gemini AI client.
    Provides authenticated client for use throughout the app.
    """
    _instance: Optional['GeminiClientSingleton'] = None
    _client: Optional[genai.Client] = None
    
    def __new__(cls) -> 'GeminiClientSingleton':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Gemini client with API key from environment variables."""
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required but not set. "
                "Please set it in your .env file or environment."
            )
        
        try:
            self._client = genai.Client(api_key=api_key)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini client: {str(e)}")
    
    @property
    def client(self) -> genai.Client:
        """Get the authenticated Gemini client."""
        if self._client is None:
            self._initialize_client()
        return self._client
