# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-11-22

The first version with a real signal pipeline. Earlier versions were a scaffold with placeholder outputs.

### Added
- MediaPipe Face Mesh landmarks with eye-aspect-ratio blink counting, a gaze-aversion ratio and head-movement variance.
- librosa audio features: pyin pitch mean and std, jitter, shimmer, speech rate, pause ratio. Optional Whisper transcription.
- Per-speaker baseline fusion: 5-second windows, z-scores against the first 20 seconds, and an aggregate deviation index.
- An optional Gemini summary with a fixed ethics caveat, which degrades gracefully without a key or on API errors.
- A results page that renders the real API response (per-signal chart and table, downloadable JSON).
- A pytest suite (58 tests, synthetic fixtures only), ruff, pre-commit, and GitHub Actions CI.
- Documentation: architecture, decisions, API, testing, troubleshooting, contributors.

### Changed
- The project is reframed as behavioral-signal analysis. The output is never labeled "lie" or "truth".
- Dependencies are pinned. `mediapipe==0.10.21` is required for Face Mesh, which needs `numpy<2`.

### Removed
- The hard-coded deception score (always 0.5) and the mock results page.
- The unused `tensorflow` and `torch` dependencies, and `web/requirements.txt`.
- Empty placeholder folders (`data/`, `models/`, `reports/`) and the empty `notebooks/experiments.ipynb`.

### Security
- Uploads are saved as `secure_filename()` with a UUID prefix. `/api/analyze` accepts only server-issued upload IDs, never paths.
- Over-size uploads return a JSON 413, and internal errors no longer leak exception text.
- Uploaded media is deleted after analysis (also on failure), and unanalysed uploads after 30 minutes.
- `debug` is off by default, and `SECRET_KEY` is read from the environment.
