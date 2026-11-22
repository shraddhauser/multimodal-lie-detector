# HTTP API

All API responses are JSON, including errors (`{"error": "..."}`).

## `POST /api/upload`

Upload one media file. Multipart form fields:

| Field | Required | Values |
|---|---|---|
| `file` | yes | Video: `mp4 avi mov mkv flv wmv`. Audio: `mp3 wav m4a flac aac` |
| `type` | no (default `video`) | `video` or `audio` |

**200**

```json
{ "success": true, "message": "File uploaded successfully", "upload_id": "3f2c…", "file_type": "video" }
```

**400**: no file, empty filename, wrong extension, or bad `type`. **413**: larger than 500 MB.

The file is stored as `<uuid>_<secure_filename>` in `web/uploads/`. It is deleted after analysis, or after `UPLOAD_RETENTION_MINUTES` (default 30) if it is never analysed.

## `POST /api/analyze`

```json
{ "video_upload_id": "3f2c…", "audio_upload_id": "9ab1…" }
```

`audio_upload_id` is optional. Without it, the video's own audio track is used when it can be decoded (this needs ffmpeg on the machine). Only IDs returned by `/api/upload` are accepted; file paths are rejected with 400.

**200**

```json
{
  "success": true,
  "timestamp": "2026-11-22T10:00:00",
  "result": {
    "title": "Multimodal Behavioral-Signal Analysis Report",
    "analysis": {
      "video_duration_s": 45.0, "fps": 30.0,
      "frames_with_face": 1320, "total_frames": 1350,
      "baseline_seconds": 20, "window_seconds": 5,
      "baseline_windows": {"face": 4, "audio": 4},
      "segment_windows": {"face": 5, "audio": 5},
      "audio_source": "video_track",
      "face_landmarks_backend": "mediapipe_face_mesh",
      "transcript": null
    },
    "deviation_report": {
      "per_signal": {"pitch_mean": 1.8, "blinks_per_minute": -0.4},
      "methods": {"pitch_mean": "z_score", "blinks_per_minute": "z_score"},
      "baseline_values": {"pitch_mean": 182.4, "blinks_per_minute": 16.0},
      "segment_values": {"pitch_mean": 195.1, "blinks_per_minute": 14.2},
      "weights": {"pitch_mean": 0.5, "blinks_per_minute": 0.5},
      "deviation_index": 1.1,
      "available_signals": ["blinks_per_minute", "pitch_mean"],
      "explanation": "Aggregate deviation index: 1.10. …"
    },
    "ai_summary": null,
    "caveat": "IMPORTANT: There is no scientifically validated …"
  }
}
```

The values above only show the shape of the response; they are not measured results.

**400**: missing or invalid body or ID. **500**: the file could not be analysed (for example, it is not a readable video). The uploaded media is deleted in both the success and failure cases.

## `GET /api/status`

```json
{ "status": "healthy", "version": "1.0.0", "timestamp": "…" }
```
