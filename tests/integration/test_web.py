"""
Integration tests for the Flask web application (web/app.py).
Uses Flask's test client; uploads go to a per-test temporary folder.
"""

import io
import json
import os
import time

import pytest

import app as web_app
from app import app


@pytest.fixture
def upload_dir(tmp_path):
    """An empty upload folder, separate from where fixtures are generated."""
    path = tmp_path / 'uploads'
    path.mkdir()
    return path


@pytest.fixture
def client(upload_dir):
    """Flask test client with an isolated upload folder."""
    original_folder = app.config['UPLOAD_FOLDER']
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = str(upload_dir)
    web_app._upload_registry.clear()
    with app.test_client() as test_client:
        yield test_client
    app.config['UPLOAD_FOLDER'] = original_folder
    web_app._upload_registry.clear()


def _upload(client, data_bytes, filename, file_type='video'):
    return client.post(
        '/api/upload',
        data={'file': (io.BytesIO(data_bytes), filename), 'type': file_type},
        content_type='multipart/form-data',
    )


class TestPages:
    """Every page renders."""

    @pytest.mark.parametrize('path', ['/', '/about', '/upload', '/results'])
    def test_page_returns_200(self, client, path):
        assert client.get(path).status_code == 200

    def test_pages_never_label_lie_or_deception_score(self, client):
        for path in ['/', '/about', '/upload', '/results']:
            html = client.get(path).get_data(as_text=True).lower()
            assert 'deception score' not in html
            assert 'lie detector' not in html

    def test_status_api(self, client):
        resp = client.get('/api/status')
        assert resp.status_code == 200
        assert resp.get_json()['status'] == 'healthy'

    def test_unknown_route_is_json_404(self, client):
        resp = client.get('/does-not-exist')
        assert resp.status_code == 404
        assert resp.is_json


class TestUpload:
    """POST /api/upload."""

    def test_upload_no_file(self, client):
        assert client.post('/api/upload').status_code == 400

    def test_upload_empty_filename(self, client):
        assert _upload(client, b'x', '').status_code == 400

    def test_upload_wrong_extension(self, client):
        assert _upload(client, b'fake data', 'test.txt').status_code == 400

    def test_upload_bad_type_field(self, client):
        assert _upload(client, b'x', 'clip.mp4', file_type='image').status_code == 400

    def test_upload_valid_video(self, client, upload_dir):
        resp = _upload(client, b'\x00' * 100, 'test.mp4')
        assert resp.status_code == 200
        body = resp.get_json()
        assert body['success'] is True
        assert 'upload_id' in body
        assert 'filepath' not in body  # server paths are never exposed
        assert len(os.listdir(upload_dir)) == 1

    def test_upload_path_traversal_sanitised(self, client, upload_dir):
        """A ../ filename is sanitised and saved inside the upload folder."""
        resp = _upload(client, b'\x00' * 100, '../../../etc/passwd.mp4')
        assert resp.status_code == 200
        saved = os.listdir(upload_dir)
        assert len(saved) == 1
        assert '..' not in saved[0] and '/' not in saved[0] and '\\' not in saved[0]
        assert saved[0].endswith('etc_passwd.mp4')
        assert not (upload_dir.parent / 'etc').exists()

    def test_oversize_upload_returns_json_413(self, client):
        app.config['MAX_CONTENT_LENGTH'] = 1024
        try:
            resp = _upload(client, b'\x00' * 4096, 'big.mp4')
        finally:
            app.config['MAX_CONTENT_LENGTH'] = web_app.MAX_FILE_SIZE
        assert resp.status_code == 413
        assert resp.is_json
        assert 'error' in resp.get_json()

    def test_stale_uploads_are_purged(self, client, upload_dir):
        old = upload_dir / 'abc_old.mp4'
        old.write_bytes(b'\x00')
        an_hour_ago = time.time() - 3600
        os.utime(old, (an_hour_ago, an_hour_ago))
        _upload(client, b'\x00' * 10, 'new.mp4')
        assert not old.exists()


class TestAnalyze:
    """POST /api/analyze."""

    def _analyze(self, client, payload):
        return client.post('/api/analyze', data=json.dumps(payload), content_type='application/json')

    def test_analyze_no_body(self, client):
        assert client.post('/api/analyze').status_code == 400

    def test_analyze_no_video(self, client):
        assert self._analyze(client, {}).status_code == 400

    def test_analyze_invalid_upload_id(self, client):
        assert self._analyze(client, {'video_upload_id': 'nonexistent'}).status_code == 400

    @pytest.mark.parametrize('outside_path', [
        '../../etc/passwd',
        '/etc/passwd',
        'C:\\Windows\\win.ini',
        os.path.abspath(__file__),
    ])
    def test_analyze_outside_path_rejected(self, client, outside_path):
        """Raw file paths from the client are never accepted."""
        resp = self._analyze(client, {'video_file': outside_path})
        assert resp.status_code == 400
        resp = self._analyze(client, {'video_upload_id': outside_path})
        assert resp.status_code == 400

    def test_analyze_non_string_id_rejected(self, client):
        assert self._analyze(client, {'video_upload_id': ['a', 'b']}).status_code == 400

    def test_end_to_end_and_media_deleted(self, client, upload_dir, synthetic_face_video_path):
        """Upload a synthetic video, analyze it, and check the upload is deleted afterwards."""
        with open(synthetic_face_video_path, 'rb') as fh:
            upload = _upload(client, fh.read(), 'drawn_face.mp4')
        assert upload.status_code == 200
        upload_id = upload.get_json()['upload_id']

        resp = self._analyze(client, {'video_upload_id': upload_id})
        assert resp.status_code == 200
        result = resp.get_json()['result']
        assert 'deviation_report' in result
        assert 'caveat' in result

        assert os.listdir(upload_dir) == []  # privacy: media removed after analysis
        assert self._analyze(client, {'video_upload_id': upload_id}).status_code == 400

    def test_failed_analysis_still_deletes_media(self, client, upload_dir):
        upload = _upload(client, b'\x00' * 100, 'corrupt.mp4')
        upload_id = upload.get_json()['upload_id']
        resp = self._analyze(client, {'video_upload_id': upload_id})
        assert resp.status_code == 500
        assert resp.is_json
        assert os.listdir(upload_dir) == []
