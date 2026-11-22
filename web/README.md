# Web application

Flask front end for the behavioral-signal analysis pipeline. See the [project README](../README.md) for setup, and [docs/API.md](../docs/API.md) for the HTTP endpoints.

```bash
pip install -r ../requirements.txt
python app.py            # http://localhost:5000
```

## Pages

| Route | What it shows |
|---|---|
| `/` | Project overview |
| `/upload` | Upload a video (required) and a separate audio file (optional) |
| `/results` | The signal-consistency report from the last analysis in this browser tab: deviation index, per-signal chart and table, optional Gemini summary, analysis details. Downloadable as JSON. |
| `/about` | How it works, ethics and limitations |

Every number on the results page comes from the `/api/analyze` response. The report is kept only in the tab's `sessionStorage`.

## Layout

```
web/
├── app.py            # routes, upload handling, privacy clean-up
├── templates/        # index, upload, results, about
├── static/css/       # page styles
├── static/js/        # upload.js (upload + analyze), results.js (renders the report)
└── uploads/          # temporary; deleted after analysis, never committed
```

## Configuration (environment variables)

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | `dev-only-change-me` | Flask secret; set a random value in production |
| `FLASK_DEBUG` | `false` | Debug mode; keep off outside local development |
| `GEMINI_API_KEY` | unset | Optional AI summary |
| `UPLOAD_RETENTION_MINUTES` | `30` | Uploads that are never analysed are deleted after this time |

The maximum upload size is 500 MB. Larger uploads get a JSON `413` response.
