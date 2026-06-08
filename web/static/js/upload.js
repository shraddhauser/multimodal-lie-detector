/* ============================================
   Upload Page JavaScript
   ============================================ */

let videoFile = null;
let audioFile = null;

// Initialize drag and drop
document.addEventListener('DOMContentLoaded', function() {
    const videoArea = document.getElementById('videoUploadArea');
    const audioArea = document.getElementById('audioUploadArea');
    const videoInput = document.getElementById('videoInput');
    const audioInput = document.getElementById('audioInput');

    // Video Upload
    videoArea.addEventListener('click', () => videoInput.click());
    videoInput.addEventListener('change', (e) => handleVideoSelect(e.target.files[0]));
    
    videoArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        videoArea.classList.add('dragover');
    });
    
    videoArea.addEventListener('dragleave', () => {
        videoArea.classList.remove('dragover');
    });
    
    videoArea.addEventListener('drop', (e) => {
        e.preventDefault();
        videoArea.classList.remove('dragover');
        handleVideoSelect(e.dataTransfer.files[0]);
    });

    // Audio Upload
    audioArea.addEventListener('click', () => audioInput.click());
    audioInput.addEventListener('change', (e) => handleAudioSelect(e.target.files[0]));
    
    audioArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        audioArea.classList.add('dragover');
    });
    
    audioArea.addEventListener('dragleave', () => {
        audioArea.classList.remove('dragover');
    });
    
    audioArea.addEventListener('drop', (e) => {
        e.preventDefault();
        audioArea.classList.remove('dragover');
        handleAudioSelect(e.dataTransfer.files[0]);
    });

    updateAnalyzeButton();
});

function handleVideoSelect(file) {
    if (!file) return;

    if (!['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska', 
          'video/x-flv', 'video/x-ms-wmv'].includes(file.type)) {
        showError('Invalid video format. Please select a valid video file.');
        return;
    }

    if (file.size > 500 * 1024 * 1024) {
        showError('File size exceeds 500MB limit.');
        return;
    }

    videoFile = file;
    displayVideoFile(file);
    updateAnalyzeButton();
    clearError();
}

function handleAudioSelect(file) {
    if (!file) return;

    if (!['audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/flac', 'audio/aac'].includes(file.type)) {
        showError('Invalid audio format. Please select a valid audio file.');
        return;
    }

    if (file.size > 500 * 1024 * 1024) {
        showError('File size exceeds 500MB limit.');
        return;
    }

    audioFile = file;
    displayAudioFile(file);
    clearError();
}

function displayVideoFile(file) {
    document.getElementById('videoFileName').textContent = `✓ ${file.name} (${formatFileSize(file.size)})`;
    document.getElementById('videoInfo').style.display = 'flex';
    document.getElementById('videoUploadArea').style.display = 'none';
}

function displayAudioFile(file) {
    document.getElementById('audioFileName').textContent = `✓ ${file.name} (${formatFileSize(file.size)})`;
    document.getElementById('audioInfo').style.display = 'flex';
    document.getElementById('audioUploadArea').style.display = 'none';
}

function clearVideoUpload() {
    videoFile = null;
    document.getElementById('videoInput').value = '';
    document.getElementById('videoInfo').style.display = 'none';
    document.getElementById('videoUploadArea').style.display = 'block';
    updateAnalyzeButton();
}

function clearAudioUpload() {
    audioFile = null;
    document.getElementById('audioInput').value = '';
    document.getElementById('audioInfo').style.display = 'none';
    document.getElementById('audioUploadArea').style.display = 'block';
}

function updateAnalyzeButton() {
    const btn = document.getElementById('analyzeBtn');
    btn.disabled = !videoFile;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

async function startAnalysis() {
    if (!videoFile) {
        showError('Please select a video file to analyze.');
        return;
    }

    clearError();
    showProgress();

    try {
        // Upload video
        const videoFormData = new FormData();
        videoFormData.append('file', videoFile);
        videoFormData.append('type', 'video');

        const videoResponse = await fetch('/api/upload', {
            method: 'POST',
            body: videoFormData
        });

        if (!videoResponse.ok) {
            throw new Error('Video upload failed');
        }

        const videoData = await videoResponse.json();
        updateProgress(33, 'Processing video...');

        // Upload audio if exists
        let audioPath = null;
        if (audioFile) {
            const audioFormData = new FormData();
            audioFormData.append('file', audioFile);
            audioFormData.append('type', 'audio');

            const audioResponse = await fetch('/api/upload', {
                method: 'POST',
                body: audioFormData
            });

            if (audioResponse.ok) {
                const audioData = await audioResponse.json();
                audioPath = audioData.filepath;
            }
        }

        updateProgress(66, 'Analyzing multimodal data...');

        // Start analysis
        const analysisResponse = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                video_file: videoData.filepath,
                audio_file: audioPath
            })
        });

        if (!analysisResponse.ok) {
            throw new Error('Analysis failed');
        }

        updateProgress(100, 'Analysis complete!');

        // Redirect to results
        setTimeout(() => {
            window.location.href = '/results';
        }, 1000);

    } catch (error) {
        hideProgress();
        showError('Analysis failed: ' + error.message);
    }
}

function showProgress() {
    document.getElementById('progressSection').style.display = 'block';
    document.getElementById('progressFill').style.width = '0%';
}

function updateProgress(percent, text) {
    document.getElementById('progressFill').style.width = percent + '%';
    document.getElementById('progressText').textContent = text;
}

function hideProgress() {
    document.getElementById('progressSection').style.display = 'none';
}

function showError(message) {
    const alert = document.getElementById('errorAlert');
    document.getElementById('errorMessage').textContent = message;
    alert.style.display = 'block';
}

function clearError() {
    document.getElementById('errorAlert').style.display = 'none';
}
