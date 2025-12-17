# Data Analytics Assistant

A Python-based data analytics assistant that allows users to upload datasets, get automatic summaries, and ask questions about their data using the Groq API.

## Features

- **Dataset Loading**: Support for CSV, Excel (.xlsx, .xls), and JSON files
- **Automatic Summary**: Get row/column counts, data types, and empty value statistics
- **AI-Powered Q&A**: Ask natural language questions about your dataset

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Key**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Groq API key
   ```

3. **Get a Groq API Key**:
   - Visit [console.groq.com](https://console.groq.com)
   - Create an account and generate an API key
   - Add it to your `.env` file

## Usage

```python
from src.dataset_handler import load_dataset
from src.dataset_analyzer import DatasetAnalyzer
from src.chat_service import ChatService

# Load a dataset
df = load_dataset("your_data.csv")

# Get summary
analyzer = DatasetAnalyzer(df)
print(analyzer.get_summary())

# Ask questions
chat = ChatService(analyzer)
response = chat.ask("What are the main trends in this data?")
print(response)
```

## Running the Demo

```bash
python main.py path/to/your/dataset.csv
```
