"""
Flask server for Data Analytics Assistant.
A modern API backend for the data analytics web application.
"""

import os
import tempfile
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from src.dataset_handler import load_dataset, DatasetError
from src.dataset_analyzer import DatasetAnalyzer
from src.chat_service import ChatService
from src.chart_generator import ChartGenerator
from src.config import validate_config, SUPPORTED_EXTENSIONS

app = Flask(__name__, static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Session storage (in-memory for simplicity)
session_data = {
    'analyzer': None,
    'chat_service': None,
    'filename': None,
    'df': None
}


def is_api_configured():
    """Check if the API is properly configured."""
    try:
        validate_config()
        return True
    except ValueError:
        return False


@app.route('/')
def index():
    """Serve the main application page."""
    return send_from_directory('static', 'index.html')


@app.route('/api/status')
def status():
    """Get current application status."""
    return jsonify({
        'api_configured': is_api_configured(),
        'dataset_loaded': session_data['analyzer'] is not None,
        'filename': session_data['filename']
    })


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and analyze a dataset."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file extension
    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in SUPPORTED_EXTENSIONS:
        return jsonify({
            'error': f'Unsupported file type: {ext}. Supported: CSV, Excel, JSON'
        }), 400
    
    try:
        # Save to temp file and load
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            file.save(tmp.name)
            df = load_dataset(tmp.name)
            os.unlink(tmp.name)  # Clean up temp file
        
        # Create analyzer and chat service
        session_data['analyzer'] = DatasetAnalyzer(df)
        session_data['filename'] = filename
        session_data['df'] = df
        
        if is_api_configured():
            session_data['chat_service'] = ChatService(session_data['analyzer'])
        
        # Get summary
        summary = session_data['analyzer'].get_summary()
        
        # Calculate total empty values
        total_empty = sum(s['total_empty'] for s in summary['empty_data'].values())
        
        # Get preview data (first 10 rows)
        preview = df.head(10).to_dict('records')
        columns = list(df.columns)
        
        # Generate AI-suggested charts
        charts = []
        if is_api_configured():
            try:
                chart_gen = ChartGenerator(df, session_data['analyzer'])
                charts = chart_gen.generate_charts()
            except Exception as e:
                print(f"Chart generation error: {e}")
        
        return jsonify({
            'success': True,
            'filename': filename,
            'summary': {
                'rows': summary['row_count'],
                'columns': summary['column_count'],
                'empty_values': total_empty,
                'column_types': summary['column_types'],
                'empty_data': summary['empty_data'],
                'basic_stats': summary['basic_stats']
            },
            'preview': {
                'columns': columns,
                'data': preview
            },
            'charts': charts
        })
        
    except DatasetError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to process file: {str(e)}'}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Send a message to the AI."""
    if session_data['chat_service'] is None:
        return jsonify({'error': 'Please upload a dataset first'}), 400
    
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        response = session_data['chat_service'].ask(data['message'])
        return jsonify({
            'success': True,
            'response': response
        })
    except Exception as e:
        return jsonify({'error': f'AI error: {str(e)}'}), 500


@app.route('/api/clear', methods=['POST'])
def clear():
    """Clear the current session."""
    session_data['analyzer'] = None
    session_data['chat_service'] = None
    session_data['filename'] = None
    return jsonify({'success': True})


if __name__ == '__main__':
    print("\n📊 Data Analytics Assistant")
    print("=" * 40)
    
    if is_api_configured():
        print("✅ API key configured")
    else:
        print("⚠️  API key not configured - chat will be disabled")
        print("   Add your GEMINI_API_KEY to .env file")
    
    print("\n🚀 Starting server at http://localhost:5000")
    print("=" * 40 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
