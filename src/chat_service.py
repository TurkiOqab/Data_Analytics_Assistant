"""Chat service for Q&A about datasets using Groq."""

from .groq_client import GroqClient
from .dataset_analyzer import DatasetAnalyzer


class ChatService:
    """Service for asking questions about a dataset using AI."""

    SYSTEM_PROMPT_TEMPLATE = """You are a helpful data analytics assistant. You have access to information about a dataset that the user has uploaded. Use this information to answer their questions accurately and helpfully.

When answering questions:
1. Base your answers on the actual data provided in the summary
2. If you're not sure about something, say so
3. Provide specific numbers and statistics when relevant
4. Suggest additional analyses the user might find useful
5. Be concise but thorough

Here is the information about the current dataset:

{dataset_summary}
"""

    def __init__(self, analyzer: DatasetAnalyzer, model: str = None):
        """
        Initialize the chat service.

        Args:
            analyzer: A DatasetAnalyzer instance for the current dataset.
            model: Optional model override for Groq.
        """
        self.analyzer = analyzer
        self.client = GroqClient(model=model)
        self.conversation_history = []

    def _get_system_prompt(self) -> str:
        """Generate the system prompt with dataset context."""
        return self.SYSTEM_PROMPT_TEMPLATE.format(
            dataset_summary=self.analyzer.get_summary_text()
        )

    def ask(self, question: str, include_history: bool = True) -> str:
        """
        Ask a question about the dataset.

        Args:
            question: The user's question.
            include_history: Whether to include conversation history for context.

        Returns:
            The AI's response.
        """
        history = self.conversation_history if include_history else None
        
        response = self.client.chat(
            user_message=question,
            system_prompt=self._get_system_prompt(),
            conversation_history=history,
        )

        # Update conversation history
        self.conversation_history.append({"role": "user", "content": question})
        self.conversation_history.append({"role": "assistant", "content": response})

        return response

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []

    def get_history(self) -> list:
        """Get the current conversation history."""
        return self.conversation_history.copy()
