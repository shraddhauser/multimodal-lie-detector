"""
Unit tests for the Flask web application.
Uses Flask's test client — no real server needed.
"""

import sys
import os
import io
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../web')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from app import app


@pytest.fixture
def client():
    """Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestPages:
    """Test that pages return 200."""

    def test_home(self, client):
        resp = client.get('/')
        assert resp.status_code == 200

    def test_about(self, client):
        resp = client.get('/about')
        assert resp.status_code == 200

    def test_upload_page(self, client):
        resp = client.get('/upload')
        assert resp.status_code == 200

    def test_results_page(self, client):
        resp = client.get('/results')
        assert resp.status_code == 200

    def test_status_api(self, client):
        resp = client.get('/api/status')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['status'] == 'healthy'


class TestUpload:
    """Test /api/upload endpoint."""

    def test_upload_no_file(self, client):
        """Upload with no file should return 400."""
        resp = client.post('/api/upload')
        assert resp.status_code == 400

    def test_upload_wrong_extension(self, client):
        """Upload with wrong extension should return 400."""
        data = {
            'file': (io.BytesIO(b'fake data'), 'test.txt'),
            'type': 'video',
        }
        resp = client.post('/api/upload', data=data, content_type='multipart/form-data')
        assert resp.status_code == 400

    def test_upload_valid_video(self, client):
        """Upload a valid small file should return 200."""
        data = {
            'file': (io.BytesIO(b'\x00' * 100), 'test.mp4'),
            'type': 'video',
        }
        resp = client.post('/api/upload', data=data, content_type='multipart/form-data')
        assert resp.status_code == 200
        result = json.loads(resp.data)
        assert result['success'] is True
        assert 'upload_id' in result

    def test_upload_path_traversal_sanitised(self, client):
        """A ../filename should be sanitised (no path traversal)."""
        data = {
            'file': (io.BytesIO(b'\x00' * 100), '../../../etc/passwd.mp4'),
            'type': 'video',
        }
        resp = client.post('/api/upload', data=data, content_type='multipart/form-data')
        assert resp.status_code == 200
        result = json.loads(resp.data)
        assert result['success'] is True
        # The saved filename should not contain '..'
        assert '..' not in result.get('upload_id', '')


class TestAnalyze:
    """Test /api/analyze endpoint."""

    def test_analyze_no_video(self, client):
        """Analyze with no video_upload_id should return 400."""
        resp = client.post(
            '/api/analyze',
            data=json.dumps({}),
            content_type='application/json',
        )
        assert resp.status_code == 400

    def test_analyze_invalid_upload_id(self, client):
        """Analyze with an invalid upload ID should return 400."""
        resp = client.post(
            '/api/analyze',
            data=json.dumps({'video_upload_id': 'nonexistent'}),
            content_type='application/json',
        )
        assert resp.status_code == 400


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
