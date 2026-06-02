"""Service for AI-powered text summarization using Groq API with llama-3.3-70b"""

import logging
from typing import Optional

from groq import Groq
from groq import APIConnectionError, APITimeoutError, RateLimitError

from config import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service for calling Groq API (llama-3.3-70b) for summarization"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Service with Groq API key
        
        Args:
            api_key: Groq API key (optional, defaults to settings.GROQ_API_KEY)
        """
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not provided or found in environment")
        
        # Initialize Groq client
        self.client = Groq(api_key=self.api_key)
    
    def generate_summary(self, text: str, max_tokens: int = 300) -> str:
        """
        Generate a summary of the provided text using Groq (llama-3.3-70b)
        
        Args:
            text: Text to summarize
            max_tokens: Maximum tokens in the response (default: 300)
        
        Returns:
            Generated summary
        
        Raises:
            ValueError: If API call fails or text is empty
            APIConnectionError: If connection to Groq fails
            APITimeoutError: If request times out
        """
        if not text or text.strip() == "":
            raise ValueError("Text to summarize cannot be empty")
        
        if len(text.strip()) < settings.MIN_TEXT_LENGTH:
            raise ValueError(
                f"Text is too short. Minimum length: {settings.MIN_TEXT_LENGTH} characters"
            )
        
        try:
            return self._call_groq_api(text, max_tokens)
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            raise
    
    def _call_groq_api(self, text: str, max_tokens: int) -> str:
        """
        Internal method to call Groq API using llama-3.3-70b
        
        Args:
            text: Text to summarize
            max_tokens: Maximum tokens in the response
            
        Returns:
            Generated summary
            
        Raises:
            ValueError: If API call fails
            APIConnectionError: If connection fails
            APITimeoutError: If request times out
        """
        # Craft the prompt for summarization
        prompt = f"""Genera un resumen conciso y claro del siguiente texto. 
El resumen debe ser breve pero completo, capturando los puntos principales.
Sé directo y evita información redundante.

TEXTO A RESUMIR:
{text}

RESUMEN:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente experto en resumir textos. Genera resúmenes claros, concisos y precisos en español."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent summaries
                max_tokens=max_tokens,
                timeout=settings.AI_REQUEST_TIMEOUT_SECONDS
            )
            
            # Extract summary from response
            if response.choices and len(response.choices) > 0:
                summary = response.choices[0].message.content.strip()
                
                if not summary:
                    raise ValueError("Groq API returned empty content")
                
                logger.info(f"Summary generated successfully ({len(summary)} chars)")
                return summary
            else:
                raise ValueError("Unexpected Groq API response format")
        
        except APITimeoutError as e:
            logger.error(f"Groq API timeout: {str(e)}")
            raise ValueError(f"AI service timeout: {str(e)}")
        except APIConnectionError as e:
            logger.error(f"Groq connection error: {str(e)}")
            raise ValueError(f"Failed to connect to AI service: {str(e)}")
        except RateLimitError as e:
            logger.error(f"Groq rate limit exceeded: {str(e)}")
            raise ValueError(f"AI service rate limit exceeded: {str(e)}")
        except Exception as e:
            logger.error(f"Error calling Groq API: {str(e)}")
            raise ValueError(f"Error generating summary: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test if Groq API connection works
        
        Returns:
            True if connection successful
        
        Raises:
            ValueError: If connection fails or no API key available
        """
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not provided or found in environment")
        
        return self._test_connection_groq()
    
        def _test_connection_groq(self) -> bool:
            """
        Internal method to test Groq API connection

        Returns:
            True if connection successful

        Raises:
            ValueError: If connection fails
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": "Say 'OK' if you can read this."
                    }
                ],
                max_tokens=10,
                timeout=settings.AI_HEALTHCHECK_TIMEOUT_SECONDS
            )

            if response.choices and len(response.choices) > 0:
                logger.info("✓ Groq API connection successful")
                return True
            else:
                raise ValueError("Empty response from Groq API")

        except APITimeoutError as e:
            logger.error(f"✗ Groq connection timeout: {str(e)}")
            raise ValueError(f"Groq API timeout: {str(e)}")

        except APIConnectionError as e:
            logger.error(f"✗ Groq connection failed: {str(e)}")
            raise ValueError(f"Cannot connect to Groq API: {str(e)}")

        except RateLimitError as e:
            logger.error(f"✗ Groq rate limit: {str(e)}")
            raise ValueError(f"Groq API rate limit: {str(e)}")

        except Exception as e:
            logger.error(f"✗ Groq connection test failed: {str(e)}")
            raise ValueError(f"Connection test failed: {str(e)}")
        