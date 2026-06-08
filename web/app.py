"""
Flask Web Application for Multimodal Lie Detector
Main application server with API endpoints for video/audio processing.
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
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

# Initialize pipeline
pipeline = LieDetectionPipeline()

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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
    - JSON with file info and processing status
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        file_type = request.form.get('type', 'video')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file extension
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_type == 'video' and file_ext not in ALLOWED_VIDEO_EXTENSIONS:
            return jsonify({'error': f'Invalid video format. Allowed: {", ".join(ALLOWED_VIDEO_EXTENSIONS)}'}), 400
        
        if file_type == 'audio' and file_ext not in ALLOWED_AUDIO_EXTENSIONS:
            return jsonify({'error': f'Invalid audio format. Allowed: {", ".join(ALLOWED_AUDIO_EXTENSIONS)}'}), 400
        
        # Save file
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'filename': filename,
            'filepath': filepath,
            'file_type': file_type
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    API endpoint for analyzing uploaded files.
    
    Expected request:
    - video_file: Path to video file
    - audio_file: Path to audio file (optional)
    
    Returns:
    - JSON with analysis results
    """
    try:
        data = request.get_json()
        video_file = data.get('video_file')
        audio_file = data.get('audio_file')
        
        if not video_file:
            return jsonify({'error': 'Video file is required'}), 400
        
        # Process files with pipeline
        result = pipeline.process_interview(video_file, audio_file)
        
        if result:
            return jsonify({
                'success': True,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({'error': 'Analysis failed'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/results/<result_id>', methods=['GET'])
def get_results(result_id):
    """Get analysis results by ID."""
    try:
        # TODO: Implement results retrieval from database
        return jsonify({'error': 'Not implemented'}), 501
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status', methods=['GET'])
def status():
    """Get application status and information."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Page not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Development server
    app.run(debug=True, host='0.0.0.0', port=5000)
