# Troubleshooting

### `AttributeError: module 'mediapipe' has no attribute 'solutions'`, or the report says landmarks are "unavailable"

MediaPipe 0.10.30 and later removed the legacy Face Mesh API. Install the pinned version:

```bash
pip install "mediapipe==0.10.21" "numpy==1.26.4"
```

Without it the app still runs, but it produces audio signals only.

### `numpy` version conflicts during install

`mediapipe==0.10.21` needs `numpy<2`. Install from `requirements.txt` into a fresh virtual environment rather than on top of an existing one that has numpy 2.x, OpenCV 5.x or pandas 3.x.

### No audio signals when only a video is uploaded

The audio track is read from the video through ffmpeg. Install it (`sudo apt-get install ffmpeg`, `brew install ffmpeg`, or `winget install ffmpeg` on Windows), or upload a separate WAV file.

### `UserWarning: PySoundFile failed. Trying audioread instead.`

This is expected for video containers such as `.mp4`. librosa falls back to audioread and ffmpeg.

### The report has no signals

The recording has to be longer than the 20-second baseline, ideally 30 seconds or more, with a face visible in at least half of each 5-second window.

### Upload returns 413

The limit is 500 MB (`MAX_FILE_SIZE` in `web/app.py`).

### `analyze` returns 400 "Invalid or expired video_upload_id"

Upload IDs live in memory: they are lost when the server restarts, and each one is single-use, because the file is deleted after analysis. Upload the file again.

### Port 5000 already in use

On macOS, AirPlay Receiver uses port 5000. Turn it off, or change the port in the `app.run(...)` call at the bottom of `web/app.py`.
