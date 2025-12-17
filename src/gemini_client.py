"""Gemini API client wrapper for Data Analytics Assistant."""

import google.generativeai as genai

from .config import GEMINI_API_KEY, DEFAULT_MODEL, validate_config


class GeminiClient:
    """Wrapper for the Google Gemini API client."""

    def __init__(self, model: str = None):
        """
        Initialize the Gemini client.

        Args:
            model: The model to use for completions. Defaults to DEFAULT_MODEL.
        """
        validate_config()
        genai.configure(api_key=GEMINI_API_KEY)
        self.model_name = model or DEFAULT_MODEL
        self.model = genai.GenerativeModel(self.model_name)

    def chat(
        self,
        user_message: str,
        system_prompt: str = None,
        conversation_history: list = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        Send a chat completion request to Gemini.

        Args:
            user_message: The user's message/question.
            system_prompt: Optional system prompt for context.
            conversation_history: Optional list of previous messages.
            temperature: Sampling temperature (0-2). Default 0.7.
            max_tokens: Maximum tokens in response. Default 2048.

        Returns:
            The assistant's response text.
        """
        # Build the conversation for Gemini
        contents = []

        # Add system prompt as first user message if provided
        if system_prompt:
            contents.append({"role": "user", "parts": [system_prompt]})
            contents.append({"role": "model", "parts": ["I understand. I'll help you analyze the dataset based on this information."]})

        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({"role": role, "parts": [msg["content"]]})

        # Add the current user message
        contents.append({"role": "user", "parts": [user_message]})

        try:
            # Create generation config
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

            response = self.model.generate_content(
                contents,
                generation_config=generation_config,
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}") from e
