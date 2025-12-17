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

## 🚀 Deploy to Vercel

### Prerequisites
- [Vercel CLI](https://vercel.com/docs/cli) installed (`npm i -g vercel`)
- A Vercel account

### Deployment Steps

1. **Install Vercel CLI** (if not installed):
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   cd /path/to/Data_Analytics_Assistant
   vercel
   ```

4. **Set Environment Variables**:
   In the Vercel dashboard, go to your project → Settings → Environment Variables and add:
   - `GEMINI_API_KEY` = your Gemini API key

5. **Redeploy** (to apply environment variables):
   ```bash
   vercel --prod
   ```

### Project Structure for Vercel
```
├── api/
│   └── index.py      # Serverless function entry point
├── static/           # Frontend assets
├── src/              # Backend modules
├── vercel.json       # Vercel configuration
└── requirements.txt  # Python dependencies
```
