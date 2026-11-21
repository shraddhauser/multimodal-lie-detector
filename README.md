# Multimodal Lie Detector

An AI-powered multimodal behavioral analysis system that combines facial expressions, eye movement patterns, and vocal characteristics to estimate behavioral consistency during human communication.

---

##  Project Overview

The system analyzes multiple behavioral signals simultaneously:

* Facial Micro-Expression Analysis
* Eye Tracking & Ocular Behavior Monitoring
* Speech & Vocal Acoustic Analysis
* Multimodal AI Reasoning using Gemini

Instead of relying solely on spoken words, the system focuses on behavioral indicators and multimodal signal consistency.

---

##  Features

*  Facial micro-expression detection
*  Eye movement tracking
*  Speech transcription
*  Vocal emotion & acoustic analysis
*  Gemini-powered multimodal reasoning
*  Behavioral consistency scoring
*  Detailed analysis reports

---

##  Technology Stack

### Computer Vision

* OpenCV (Haar cascade face detection)
* MediaPipe Face Mesh (blink / EAR, gaze aversion, head movement)

### Audio Processing

* Librosa (pitch, jitter, shimmer, pause analysis)
* Whisper ASR (optional, offline transcription)

### Fusion & Reasoning

* Per-speaker baseline z-score fusion (NumPy / SciPy)
* Google Gemini API (optional natural-language summary)

### Web

* Flask

---

##  Getting Started

```bash
python -m venv .venv
.venv\Scriptsctivate        # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
cp .env.example .env           # optionally set GEMINI_API_KEY and SECRET_KEY
```

Run the web app:

```bash
python web/app.py              # http://localhost:5000
```

Optional extras:

* `pip install openai-whisper` for speech transcription
* `pip install "mediapipe<0.10.30"` for full Face Mesh landmarks (needs numpy<2); otherwise the Haar cascade fallback is used

Without a Gemini API key the pipeline still runs; only the AI summary is skipped.

---

##  Running Tests

```bash
pytest
```

The suite uses synthetic fixtures only (no real data, network or GPU). Tests marked `slow` or `requires_weights` are skipped by default; run them with `pytest -m slow` or `pytest -m requires_weights`.

---

## Project Structure

```text
multimodal-lie-detector/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── samples/
│
├── models/
│   ├── face_model/
│   ├── eye_tracking_model/
│   ├── voice_model/
│   └── fusion_model/
│
├── src/
│   ├── face_analysis/
│   │   ├── micro_expression.py
│   │   └── face_detector.py
│   │
│   ├── eye_tracking/
│   │   ├── eye_tracker.py
│   │   └── pupil_analysis.py
│   │
│   ├── audio_analysis/
│   │   ├── speech_to_text.py
│   │   ├── emotion_analysis.py
│   │   └── acoustic_features.py
│   │
│   ├── fusion/
│   │   └── multimodal_fusion.py
│   │
│   ├── gemini/
│   │   └── gemini_reasoning.py
│   │
│   └── main.py
│
├── notebooks/
│   └── experiments.ipynb
│
├── reports/
│   ├── screenshots/
│   └── outputs/
│
├── docs/
│   ├── architecture.png
│   ├── workflow.png
│   └── project_report.pdf
│
├── tests/
│   ├── conftest.py
│   ├── test_face.py
│   ├── test_audio.py
│   ├── test_fusion.py
│   ├── test_gemini.py
│   └── test_web.py
│
├── web/
│   ├── app.py
│   ├── templates/
│   └── static/
│
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

##  System Architecture

```text
Input Video
      │
      ▼
 Face Detection
      │
      ▼
Micro-expression Analysis
      │
      ▼
Eye Tracking
      │
      ▼
Speech Processing
      │
      ▼
Feature Fusion
      │
      ▼
Gemini Reasoning
      │
      ▼
Behavior Consistency Score
```

---

##  Future Improvements

* Live webcam support
* Advanced emotion recognition
* Temporal behavior modeling
* Mobile application deployment
* Wearable device integration
* Real-time dashboard analytics

---

##  Achievements

**Winner – GDG TechSprint 2025**

Selected for live demonstration at a Google Developer Group showcase.

---

##  Team Cloud Sprint

* Shraddha Pardeshi (Team Lead)
* Syed Fatema Zohra
* Zaid Ali Syyed

---

##  License

This project is intended for educational and research purposes only.

---

##  Support

If you find this project useful, consider giving it a star on GitHub.
