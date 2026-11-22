# Testing

```bash
pip install -r requirements-dev.txt
pytest                                       # all default tests
pytest --cov=src --cov=web --cov-report=term # with coverage
```

The suite runs on a CPU-only laptop with no internet, no GPU and no API keys. Every input is synthetic and generated into pytest's `tmp_path` by `tests/conftest.py`: sine-wave and silent WAVs, a 44.1 kHz WAV, a pitch-shift WAV, and a 2-second video of a drawn cartoon face. No recording of a real person is used or committed. Gemini is always mocked.

Tests marked `slow` or `requires_weights` are skipped by default (see `pytest.ini`). There are none yet.

## Last measured run

| Metric | Value | Source |
|---|---|---|
| Tests | 58 passed | `pytest` |
| Line coverage (`src/` + `web/`) | 85 % | `pytest --cov=src --cov=web --cov-report=term` |
| Wall time | 22–90 s on Windows 11, Python 3.11, CPU (the first run is slower while librosa compiles its numba functions) | `pytest` |

Re-run the commands above to update these numbers. Coverage is reported, not targeted.

## What each file covers

| File | Tests | What it checks | Why it matters |
|---|---|---|---|
| `tests/unit/test_audio.py` | 7 | A 220 Hz sine gives pitch within ±5 Hz; silence gives pause ratio ≈ 1 and `None` pitch (NaN-safe); stereo becomes mono; 44.1 kHz input is resampled to 16 kHz; all feature keys are present | Audio features are the most numeric part of the pipeline; known synthetic inputs give known answers |
| `tests/unit/test_face.py` | 8 | A blank or `None` frame gives 0 faces without crashing; EAR is lower for closed-eye landmarks than open ones; 3 synthetic EAR dips count as 3 blinks; the rule-based micro-expression detector flags a large jump and ignores still frames | Blink counting drives a headline signal; it must count exactly |
| `tests/unit/test_fusion.py` | 8 | Identical baseline and segment give 0 deviation; a pitch shift raises the deviation; windowed baselines give true z-scores ((230−200)/10 = 3); a single baseline value falls back to labelled relative change; a missing modality is dropped and the weights renormalise to 1; empty input is handled; the output has no lie/truth label or score | The fusion maths is the core claim of the project, and the "no verdict" rule is an ethics requirement |
| `tests/unit/test_gemini.py` | 5 | No API key gives no summary; the prompt contains the full caveat; a mocked client returns its text; an API error degrades to no summary; the report always carries the caveat | The optional AI layer must never be required and never drop the caveat |
| `tests/unit/test_pipeline.py` | 5 | End to end on the drawn-face video with audio: report shape and JSON-serialisability; steady audio gives ≈ 0 pitch deviation; a 220 → 330 Hz shift after the baseline is detected with the right baseline and segment values; no lie/truth label; an unreadable video raises | Shows that baseline splitting and windowing work together, not just in isolation |
| `tests/integration/test_web.py` | 25 | All pages return 200 and never show "deception score" or "lie detector"; JSON 404; upload: no file / empty name / wrong extension / bad type → 400, valid file → 200 with no server path exposed, a `../` filename is sanitised and stays inside the upload folder, an over-size upload → JSON 413, stale uploads are purged; analyze: no body / no ID / unknown ID / non-string ID → 400, raw paths (`../../etc/passwd`, absolute paths) → 400, full upload → analyze → 200 and the media is deleted, a corrupt video → JSON 500 and the media is still deleted | Covers the security and privacy fixes: path traversal, arbitrary file read, retention, error format |

## Not covered

- Real recordings. Accuracy of blink, gaze or pitch on real faces and voices has not been measured. `TODO(measure)`: needs a consented sample set; nothing in this repo produces such a number.
- MediaPipe landmark quality: the drawn cartoon face is not expected to be detected as a real face; the tests check the pipeline runs either way.
- Whisper transcription (optional dependency, not installed in CI).
- The JavaScript front end (no browser tests).
