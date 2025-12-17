"""Groq API client wrapper for Data Analytics Assistant."""

from groq import Groq

from .config import GROQ_API_KEY, DEFAULT_MODEL, validate_config


class GroqClient:
    """Wrapper for the Groq API client."""

    def __init__(self, model: str = None):
        """
        Initialize the Groq client.

        Args:
            model: The model to use for completions. Defaults to DEFAULT_MODEL.
        """
        validate_config()
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = model or DEFAULT_MODEL

    def chat(
        self,
        user_message: str,
        system_prompt: str = None,
        conversation_history: list = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        Send a chat completion request to Groq.

        Args:
            user_message: The user's message/question.
            system_prompt: Optional system prompt for context.
            conversation_history: Optional list of previous messages.
            temperature: Sampling temperature (0-2). Default 0.7.
            max_tokens: Maximum tokens in response. Default 2048.

        Returns:
            The assistant's response text.
        """
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add the current user message
        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Groq API error: {str(e)}") from e
