# Data Analytics Assistant

A Python-based data analytics assistant that allows users to upload datasets, get automatic summaries, AI-generated charts, and ask questions about their data using Google's Gemini API.

## Features

- **Dataset Loading**: Support for CSV, Excel (.xlsx, .xls), and JSON files
- **Automatic Summary**: Get row/column counts, data types, and empty value statistics
- **AI-Generated Charts**: Automatically generates relevant visualizations for your data
- **AI-Powered Q&A**: Ask natural language questions about your dataset

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Key**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

3. **Get a Gemini API Key**:
   - Visit [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
   - Create an account and generate an API key
   - Add it to your `.env` file

## Running Locally

**Web Application (Flask)**:
```bash
python server.py
```
Then open http://localhost:5000 in your browser.

---

## 🚀 Deploy to Railway (Recommended)

Railway supports large Python dependencies like pandas and matplotlib without size limits.

### Deployment Steps

1. **Go to [railway.app](https://railway.app)** and sign up/login

2. **Create New Project** → "Deploy from GitHub repo"

3. **Connect your GitHub** and select `Data_Analytics_Assistant`

4. **Add Environment Variable**:
   - Go to Variables tab
   - Add: `GEMINI_API_KEY` = your API key

5. **Deploy!** Railway will auto-detect the Python project and deploy.

---

### Project Structure
```
├── static/           # Frontend assets (HTML, CSS, JS)
├── src/              # Backend modules
├── server.py         # Flask application entry point
├── railway.toml      # Railway configuration
└── requirements.txt  # Python dependencies
```
