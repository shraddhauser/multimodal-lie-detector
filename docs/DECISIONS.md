# Architecture decision records

## ADR-001: Compare each speaker to their own baseline, not to population thresholds

- **Context:** Blink rate, gaze, pitch and pause behaviour vary a lot between people, cultures, neurotypes and recording setups. A fixed threshold such as "more than 20 blinks per minute is suspicious" would flag people for being who they are.
- **Options considered:** (A) population thresholds from the literature; (B) a model trained on labelled recordings; (C) a per-speaker baseline from the start of the same recording.
- **Decision:** C. The first 20 seconds of a recording are the baseline. Every signal is reported as a deviation from it.
- **Why:** It needs no external data and it measures change within one person rather than differences between people. The output also reads naturally as "how much did this change?".
- **Trade-off accepted:** The baseline period is assumed to be "normal" for the speaker. Recordings shorter than about 25 seconds give no comparison at all, and a stressful opening distorts the baseline.

## ADR-002: MediaPipe Face Mesh for landmarks, Haar cascade kept only for face boxes

- **Context:** The original version of this repository used only an OpenCV Haar cascade, which only returns a face bounding box. Blink, gaze and head-movement signals need eye contour, iris and nose landmarks.
- **Options considered:** (A) Haar cascade plus a separate eye cascade; (B) dlib 68-point landmarks; (C) MediaPipe Face Mesh with refined iris landmarks.
- **Decision:** C, pinned to `mediapipe==0.10.21`. The Haar cascade stays for `detect_faces()`.
- **Why:** It gives 478 landmarks including the iris centres, runs on CPU, and installs from pip wheels with no compiler step (dlib needs one on Windows).
- **Trade-off accepted:** MediaPipe 0.10.30+ removed the legacy `solutions` API, so the version is pinned, and that pin forces `numpy<2`. If a newer MediaPipe is installed, the detector reports landmarks as unavailable instead of crashing, and only audio signals are produced.

## ADR-003: No supervised "deception classifier"

- **Context:** A lie/truth classifier would need labelled data. There is no valid, consented, ground-truth deception dataset that generalises, and research consensus is that no reliable behavioural lie signature exists.
- **Options considered:** (A) train a classifier on a public "deception" dataset; (B) keep the original hard-coded score of 0.5; (C) report signal deviations only, with no verdict.
- **Decision:** C. The pipeline never outputs "lie", "truth" or a deception probability, and tests enforce this. `micro_expression.py` and `emotion_analysis.py` are labelled simulated and are not used in the report.
- **Why:** A classifier would produce confident-looking numbers with no validity, and could cause real harm if used for hiring, policing or legal decisions.
- **Trade-off accepted:** The tool cannot answer "is this person lying?". That is intended.

## ADR-004: Windowed baseline for real z-scores, with a labelled fallback

- **Context:** A first version divided each change by the baseline value, `(segment − baseline) / |baseline|`. That is a relative change, not a z-score, and it treats a 10 % change in a noisy signal the same as in a stable one.
- **Options considered:** (A) relative change only; (B) z-scores against a baseline split into windows; (C) z-scores against published population spreads.
- **Decision:** B. The baseline and the rest of the recording are split into 5-second windows, and each signal's deviation is `(segment mean − baseline mean) / baseline std`. When the baseline has fewer than 2 windows, or zero spread, the code falls back to relative change and labels it in `methods`.
- **Why:** It keeps the per-speaker idea from ADR-001 and accounts for how much each signal naturally fluctuates for that person.
- **Trade-off accepted:** A 20-second baseline gives only 4 windows, so the standard deviation estimate is noisy. Signals that are steady in the baseline (zero spread) cannot be z-scored.

## ADR-005: The analyze endpoint accepts server-issued upload IDs, never file paths

- **Context:** The original version of this repository saved uploads under the raw client filename and let `/api/analyze` open any path sent in the JSON body. That allowed path traversal and arbitrary file reads.
- **Options considered:** (A) validate client paths; (B) return opaque upload IDs and resolve them on the server.
- **Decision:** B. Files are saved as `secure_filename()` with a UUID prefix. `/api/upload` returns a random `upload_id`, and `/api/analyze` resolves it to a path inside `UPLOAD_FOLDER` and checks it stays there.
- **Why:** The client never controls a path, so there is nothing to validate.
- **Trade-off accepted:** The ID registry is in memory, so IDs are lost when the server restarts and it only works as a single process. That is acceptable for a prototype.
