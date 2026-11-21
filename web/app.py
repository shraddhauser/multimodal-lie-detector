"""
Flask Web Application for Multimodal Behavioral-Signal Analysis
Main application server with API endpoints for video/audio processing.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
import json
from datetime import datetime
import sys

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from main import LieDetectionPipeline

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac', 'aac'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-only-change-me')

# Initialize pipeline
pipeline = LieDetectionPipeline()

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory store for upload IDs → filenames (production would use a DB)
_upload_registry = {}


def _safe_filename(original_name):
    """Generate a safe, unique filename."""
    safe = secure_filename(original_name)
    if not safe:
        safe = 'upload'
    unique = f"{uuid.uuid4().hex[:12]}_{safe}"
    return unique


def _resolve_upload(upload_id):
    """Resolve an upload ID to a full path inside UPLOAD_FOLDER, or None."""
    filename = _upload_registry.get(upload_id)
    if not filename:
        return None
    path = os.path.join(UPLOAD_FOLDER, filename)
    # Ensure the resolved path is inside UPLOAD_FOLDER
    real = os.path.realpath(path)
    if not real.startswith(os.path.realpath(UPLOAD_FOLDER)):
        return None
    if not os.path.isfile(real):
        return None
    return real


@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')


@app.route('/upload')
def upload_page():
    """Upload page for video/audio files."""
    return render_template('upload.html')


@app.route('/results')
def results():
    """Results dashboard page."""
    return render_template('results.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    API endpoint for uploading video/audio files.

    Expected request:
    - file: Video or audio file
    - type: 'video' or 'audio'

    Returns:
    - JSON with upload_id and processing status
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        file_type = request.form.get('type', 'video')

        if file.filename == '' or file.filename is None:
            return jsonify({'error': 'No file selected'}), 400

        # Validate file extension
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

        if file_type == 'video' and file_ext not in ALLOWED_VIDEO_EXTENSIONS:
            return jsonify({'error': f'Invalid video format. Allowed: {", ".join(ALLOWED_VIDEO_EXTENSIONS)}'}), 400

        if file_type == 'audio' and file_ext not in ALLOWED_AUDIO_EXTENSIONS:
            return jsonify({'error': f'Invalid audio format. Allowed: {", ".join(ALLOWED_AUDIO_EXTENSIONS)}'}), 400

        # Save file with safe name
        filename = _safe_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Register the upload
        upload_id = uuid.uuid4().hex
        _upload_registry[upload_id] = filename

        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'upload_id': upload_id,
            'file_type': file_type,
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    API endpoint for analyzing uploaded files.

    Expected request (JSON):
    - video_upload_id: Upload ID returned by /api/upload
    - audio_upload_id: Upload ID (optional)

    Returns:
    - JSON with analysis results (deviation report)
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON body required'}), 400

        video_upload_id = data.get('video_upload_id') or data.get('video_file')
        audio_upload_id = data.get('audio_upload_id') or data.get('audio_file')

        if not video_upload_id:
            return jsonify({'error': 'video_upload_id is required'}), 400

        # Resolve upload IDs to paths (never accept raw paths from client)
        video_path = _resolve_upload(video_upload_id)
        if not video_path:
            return jsonify({'error': 'Invalid or expired video_upload_id'}), 400

        audio_path = _resolve_upload(audio_upload_id) if audio_upload_id else None

        # Process files with pipeline
        result = pipeline.process_interview(video_path, audio_path)

        # Clean up uploaded files after analysis
        try:
            os.remove(video_path)
            _upload_registry.pop(video_upload_id, None)
            if audio_path:
                os.remove(audio_path)
                _upload_registry.pop(audio_upload_id, None)
        except OSError:
            pass

        if result:
            return jsonify({
                'success': True,
                'result': result,
                'timestamp': datetime.now().isoformat(),
            }), 200
        else:
            return jsonify({'error': 'Analysis failed'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status', methods=['GET'])
def status():
    """Get application status and information."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Page not found'}), 404


@app.errorhandler(413)
def too_large(error):
    """Handle file too large errors."""
    return jsonify({'error': f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)} MB'}), 413


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Development server — set debug=False in production
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=5000)
