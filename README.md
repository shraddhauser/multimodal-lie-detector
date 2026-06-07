Multimodal Lie Detector

An AI-powered multimodal behavioral analysis system that combines facial expressions, eye movement patterns, and vocal characteristics to estimate behavioral consistency during human communication.

 Project Overview

The system analyzes multiple behavioral signals simultaneously:

Facial Micro-Expression Analysis
Eye Tracking & Ocular Behavior Monitoring
Speech & Vocal Acoustic Analysis
Multimodal AI Reasoning using Gemini

Instead of relying solely on spoken words, the system focuses on behavioral indicators and multimodal signal consistency.


Project Structure
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
│   ├── test_face.py
│   ├── test_audio.py
│   └── test_fusion.py
│
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
\## Features



\- Real-time face analysis

\- Eye movement tracking

\- Speech transcription

\- Vocal emotion analysis

\- Multimodal fusion

\- Behavioral consistency scoring



\## Technology Stack



\### Computer Vision

\- OpenCV

\- Vision Transformers (ViT)



\### Audio Processing

\- Whisper ASR

\- Librosa



\### AI Models

\- Google Gemini API

\- PyTorch

\- TensorFlow



\### Programming Language

\- Python



\## System Architecture



Input Video

↓

Face Detection

↓

Micro-expression Analysis

↓

Eye Tracking

↓

Speech Processing

↓

Feature Fusion

↓

Gemini Reasoning

↓

Behavior Consistency Score



\## Future Improvements



\- Live webcam support

\- Improved emotion recognition

\- Advanced temporal modeling

\- Mobile deployment



\## Achievements



🏆 Winner – GDG TechSprint 2025



Selected for live demonstration at a Google Developer Group showcase.



\## Authors



Shraddha Pardeshi
Syed Fatema Zohra
Zaid Ali Syyed
