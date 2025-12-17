#!/usr/bin/env python3
"""
Data Analytics Assistant - Main Entry Point

A tool for analyzing datasets and asking questions about them using AI.
"""

import sys
import json

from src.dataset_handler import load_dataset, DatasetError
from src.dataset_analyzer import DatasetAnalyzer
from src.chat_service import ChatService


def print_summary(analyzer: DatasetAnalyzer):
    """Print the dataset summary in a formatted way."""
    summary = analyzer.get_summary()
    
    print("\n" + "=" * 60)
    print("📊 DATASET SUMMARY")
    print("=" * 60)
    print(f"📁 Rows: {summary['row_count']:,}")
    print(f"📋 Columns: {summary['column_count']}")
    
    print("\n📝 Column Details:")
    print("-" * 60)
    for col, dtype in summary["column_types"].items():
        empty_info = summary["empty_data"][col]
        empty_str = f"{empty_info['total_empty']} empty ({empty_info['percentage']}%)"
        print(f"  • {col}")
        print(f"    Type: {dtype} | Empty: {empty_str}")
    
    print("\n" + "=" * 60)


def interactive_chat(chat_service: ChatService):
    """Run an interactive Q&A session."""
    print("\n💬 Chat Mode - Ask questions about your dataset")
    print("   Type 'quit' or 'exit' to end the session")
    print("   Type 'clear' to clear conversation history")
    print("-" * 60)
    
    while True:
        try:
            question = input("\n🙋 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break
        
        if not question:
            continue
        
        if question.lower() in ("quit", "exit", "q"):
            print("\nGoodbye!")
            break
        
        if question.lower() == "clear":
            chat_service.clear_history()
            print("✓ Conversation history cleared.")
            continue
        
        try:
            print("\n🤖 Assistant: ", end="", flush=True)
            response = chat_service.ask(question)
            print(response)
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


def main():
    """Main entry point for the application."""
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_dataset>")
        print("\nSupported formats: CSV, Excel (.xlsx, .xls), JSON")
        print("\nExample:")
        print("  python main.py data.csv")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Load the dataset
    print(f"\n📂 Loading dataset: {file_path}")
    try:
        df = load_dataset(file_path)
        print(f"✓ Dataset loaded successfully!")
    except DatasetError as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    
    # Analyze the dataset
    analyzer = DatasetAnalyzer(df)
    print_summary(analyzer)
    
    # Check if Groq API is configured
    try:
        chat_service = ChatService(analyzer)
        interactive_chat(chat_service)
    except ValueError as e:
        # API key not configured
        print(f"\n⚠️  {str(e)}")
        print("\nDataset summary is available above.")
        print("Configure your API key to enable Q&A functionality.")


if __name__ == "__main__":
    main()
