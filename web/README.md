# Web Application - Multimodal Lie Detector

A modern, user-friendly web interface for the Multimodal Lie Detector system.

## Features

- **Modern UI/UX**: Clean, intuitive interface with dark theme
- **Drag & Drop Upload**: Easy file upload with drag and drop support
- **Real-time Progress**: Visual feedback during analysis
- **Comprehensive Results**: Detailed analysis dashboard with charts
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Directory Structure

```
web/
├── app.py                 # Flask application main server
├── static/
│   ├── css/
│   │   ├── style.css     # Global styles
│   │   ├── home.css      # Home page styles
│   │   ├── upload.css    # Upload page styles
│   │   ├── results.css   # Results page styles
│   │   └── about.css     # About page styles
│   ├── js/
│   │   ├── upload.js     # Upload page logic
│   │   └── results.js    # Results page logic
│   └── images/           # Image assets
├── templates/
│   ├── index.html        # Home page
│   ├── upload.html       # Upload interface
│   ├── results.html      # Results dashboard
│   └── about.html        # About page
└── uploads/              # User uploaded files (temporary)
```

## Installation

1. Install web dependencies:
```bash
pip install flask flask-cors
```

2. Install all project dependencies:
```bash
pip install -r ../requirements.txt
```

## Running the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

## Pages

### Home (`/`)
- Landing page with project overview
- Feature highlights
- Call to action buttons

### Upload (`/upload`)
- Video file upload interface
- Optional audio file upload
- File validation and size checks
- Analysis options configuration

### Results (`/results`)
- Comprehensive analysis dashboard
- Deception score visualization
- Detailed results by modality:
  - Facial analysis
  - Eye tracking
  - Audio analysis
  - Behavioral consistency
- Timeline chart of metrics
- Evidence summary
- Recommendations
- Download report functionality

### About (`/about`)
- Project overview and goals
- Technology stack information
- How it works explanation
- Key features description
- Important disclaimers

## API Endpoints

### Upload Endpoint
**POST** `/api/upload`
- Upload video or audio files
- Parameters:
  - `file`: The media file to upload
  - `type`: 'video' or 'audio'
- Response: File info and path

### Analysis Endpoint
**POST** `/api/analyze`
- Start analysis on uploaded files
- Request body:
  ```json
  {
    "video_file": "/path/to/video",
    "audio_file": "/path/to/audio"
  }
  ```
- Response: Analysis results

### Status Endpoint
**GET** `/api/status`
- Check application health
- Response: Status information

## Configuration

Key settings in `app.py`:
- `UPLOAD_FOLDER`: Directory for uploaded files
- `MAX_FILE_SIZE`: Maximum upload size (default: 500MB)
- `ALLOWED_VIDEO_EXTENSIONS`: Supported video formats
- `ALLOWED_AUDIO_EXTENSIONS`: Supported audio formats

## File Size Limits

- Maximum upload size: 500 MB
- Supported formats:
  - **Video**: MP4, AVI, MOV, MKV, FLV, WMV
  - **Audio**: MP3, WAV, M4A, FLAC, AAC

## Browser Compatibility

- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development

### Adding New Pages

1. Create HTML template in `templates/`
2. Create route in `app.py`
3. Add CSS if needed in `static/css/`
4. Add JavaScript if needed in `static/js/`

### Styling Guidelines

- Use CSS variables defined in `style.css`
- Follow the color scheme:
  - Primary: `#6366f1`
  - Secondary: `#10b981`
  - Background: `#0f172a`
- Maintain responsive design with media queries

## Security Considerations

- File upload validation on both client and server
- File type verification
- Size limit enforcement
- CORS enabled for API endpoints
- Input sanitization for all user inputs

## Future Enhancements

- User authentication and accounts
- Analysis history and saved results
- Report generation and export (PDF, CSV)
- Real-time streaming analysis
- Advanced filtering and search
- API rate limiting
- Database integration

## Troubleshooting

### Port Already in Use
```bash
# Change port in app.py
app.run(port=5001)
```

### Upload Fails
- Check file format
- Verify file size < 500MB
- Check `uploads/` directory permissions

### CSS Not Loading
- Clear browser cache (Ctrl+Shift+Delete)
- Restart Flask server

## License

See LICENSE file in project root.
