"""
Flask Web Application for Multimodal Behavioral-Signal Analysis
Main application server with API endpoints for video/audio processing.
"""

import logging
import os
import sys
import time
import uuid
from datetime import datetime

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename

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
# Uploaded media is deleted right after analysis; files that are never
# analysed are deleted after this many minutes.
UPLOAD_RETENTION_MINUTES = int(os.environ.get('UPLOAD_RETENTION_MINUTES', '30'))

logger = logging.getLogger(__name__)

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
    root = os.path.realpath(app.config['UPLOAD_FOLDER'])
    real = os.path.realpath(os.path.join(root, filename))
    # Ensure the resolved path is inside UPLOAD_FOLDER
    if os.path.commonpath([root, real]) != root:
        return None
    if not os.path.isfile(real):
        return None
    return real


def _delete_upload(upload_id):
    """Delete an uploaded file and forget its ID."""
    path = _resolve_upload(upload_id) if upload_id else None
    _upload_registry.pop(upload_id, None)
    if path:
        try:
            os.remove(path)
        except OSError:
            logger.warning("Could not delete upload %s", upload_id)


def _purge_stale_uploads():
    """Delete uploads older than UPLOAD_RETENTION_MINUTES."""
    cutoff = time.time() - UPLOAD_RETENTION_MINUTES * 60
    folder = app.config['UPLOAD_FOLDER']
    for name in os.listdir(folder):
        if name.startswith('.'):
            continue
        path = os.path.join(folder, name)
        try:
            if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
                os.remove(path)
        except OSError:
            continue
    live = set(os.listdir(folder))
    for uid, fname in list(_upload_registry.items()):
        if fname not in live:
            _upload_registry.pop(uid, None)


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
        if file_type not in ('video', 'audio'):
            return jsonify({'error': "type must be 'video' or 'audio'"}), 400

        if file.filename == '' or file.filename is None:
            return jsonify({'error': 'No file selected'}), 400

        # Validate file extension
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

        if file_type == 'video' and file_ext not in ALLOWED_VIDEO_EXTENSIONS:
            return jsonify({'error': f'Invalid video format. Allowed: {", ".join(ALLOWED_VIDEO_EXTENSIONS)}'}), 400

        if file_type == 'audio' and file_ext not in ALLOWED_AUDIO_EXTENSIONS:
            return jsonify({'error': f'Invalid audio format. Allowed: {", ".join(ALLOWED_AUDIO_EXTENSIONS)}'}), 400

        _purge_stale_uploads()

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

    except HTTPException:
        raise  # e.g. 413 Request Entity Too Large -> JSON via the error handler
    except Exception:
        logger.exception("Upload failed")
        return jsonify({'error': 'Upload failed'}), 500


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
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'error': 'JSON body required'}), 400

        video_upload_id = data.get('video_upload_id') or data.get('video_file')
        audio_upload_id = data.get('audio_upload_id') or data.get('audio_file')

        if not isinstance(video_upload_id, str) or not video_upload_id:
            return jsonify({'error': 'video_upload_id is required'}), 400

        # Resolve upload IDs to paths (never accept raw paths from client)
        video_path = _resolve_upload(video_upload_id)
        if not video_path:
            return jsonify({'error': 'Invalid or expired video_upload_id'}), 400

        audio_path = None
        if audio_upload_id:
            if not isinstance(audio_upload_id, str):
                return jsonify({'error': 'Invalid audio_upload_id'}), 400
            audio_path = _resolve_upload(audio_upload_id)
            if not audio_path:
                return jsonify({'error': 'Invalid or expired audio_upload_id'}), 400

        try:
            result = pipeline.process_interview(video_path, audio_path)
        finally:
            # Privacy: never keep media after analysis, even if it failed
            _delete_upload(video_upload_id)
            if audio_upload_id:
                _delete_upload(audio_upload_id)

        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat(),
        }), 200

    except Exception:
        logger.exception("Analysis failed")
        return jsonify({'error': 'Analysis failed. Check that the file is a readable video.'}), 500


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
