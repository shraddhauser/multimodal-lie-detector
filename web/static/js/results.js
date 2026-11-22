/* ============================================
   Results Page JavaScript
   Renders the report returned by POST /api/analyze.
   Nothing on this page is hard-coded: every number comes from the API
   response, which upload.js stores in sessionStorage.
   ============================================ */

const SIGNAL_LABELS = {
    blinks_per_minute: 'Blink rate (blinks/min)',
    aversion_ratio: 'Gaze-aversion ratio',
    head_movement_variance: 'Head-movement variance (px²)',
    pitch_mean: 'Pitch mean (Hz)',
    pitch_std: 'Pitch variability (Hz)',
    speech_rate: 'Speech rate (onsets/s)',
    pause_ratio: 'Pause ratio',
};

let currentReport = null;

document.addEventListener('DOMContentLoaded', function () {
    let stored = null;
    try {
        stored = JSON.parse(sessionStorage.getItem('analysisResult') || 'null');
    } catch (e) {
        stored = null;
    }

    if (!stored || !stored.result) {
        document.getElementById('emptyState').style.display = 'block';
        return;
    }

    currentReport = stored;
    renderReport(stored.result);
});

function fmt(value, digits = 2) {
    if (value === null || value === undefined || Number.isNaN(value)) return '—';
    return Number(value).toFixed(digits);
}

function renderReport(report) {
    const dev = report.deviation_report || {};
    const meta = report.analysis || {};

    document.getElementById('reportBody').style.display = 'block';
    if (report.caveat) {
        document.getElementById('caveatText').textContent = report.caveat;
    }

    document.getElementById('deviationIndex').textContent = fmt(dev.deviation_index);
    document.getElementById('explanation').textContent = dev.explanation || '';
    document.getElementById('aiSummary').textContent =
        report.ai_summary || 'No AI summary (GEMINI_API_KEY not set, or no signals to summarise).';

    renderSignalTable(dev);
    renderChart(dev);
    renderMeta(meta);
}

function renderSignalTable(dev) {
    const tbody = document.getElementById('signalRows');
    tbody.textContent = '';
    const signals = dev.available_signals || [];

    if (signals.length === 0) {
        const row = tbody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 5;
        cell.textContent = 'No signals could be compared. The video may be shorter than the baseline period, have no detectable face, or have no decodable audio.';
        return;
    }

    signals.forEach((key) => {
        const row = tbody.insertRow();
        const method = (dev.methods || {})[key];
        [
            SIGNAL_LABELS[key] || key,
            fmt((dev.baseline_values || {})[key], 3),
            fmt((dev.segment_values || {})[key], 3),
            method === 'z_score' ? 'z = ' + fmt(dev.per_signal[key]) : fmt(dev.per_signal[key] * 100, 0) + ' %',
            method === 'z_score' ? 'z-score' : 'relative change',
        ].forEach((text) => {
            row.insertCell().textContent = text;
        });
    });
}

function renderChart(dev) {
    const ctx = document.getElementById('signalChart');
    const signals = dev.available_signals || [];
    if (!ctx || typeof Chart === 'undefined' || signals.length === 0) return;

    const values = signals.map((k) => dev.per_signal[k]);
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: signals.map((k) => SIGNAL_LABELS[k] || k),
            datasets: [{
                label: 'Deviation from baseline',
                data: values,
                backgroundColor: values.map((v) => (v >= 0 ? 'rgba(244, 114, 182, 0.7)' : 'rgba(99, 102, 241, 0.7)')),
                borderWidth: 0,
            }],
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: '#334155' }, ticks: { color: '#cbd5e1' } },
                y: { grid: { color: '#334155' }, ticks: { color: '#cbd5e1' } },
            },
        },
    });
}

function renderMeta(meta) {
    const box = document.getElementById('analysisMeta');
    box.textContent = '';
    const rows = [
        ['Video duration (s)', fmt(meta.video_duration_s, 1)],
        ['Frames with a face / total', `${meta.frames_with_face ?? '—'} / ${meta.total_frames ?? '—'}`],
        ['Baseline period (s)', meta.baseline_seconds ?? '—'],
        ['Window length (s)', meta.window_seconds ?? '—'],
        ['Baseline windows (face / audio)', meta.baseline_windows ? `${meta.baseline_windows.face} / ${meta.baseline_windows.audio}` : '—'],
        ['Compared windows (face / audio)', meta.segment_windows ? `${meta.segment_windows.face} / ${meta.segment_windows.audio}` : '—'],
        ['Audio source', meta.audio_source || 'none'],
        ['Face landmarks', meta.face_landmarks_backend || '—'],
    ];
    if (meta.transcript) rows.push(['Transcript', meta.transcript]);

    rows.forEach(([label, value]) => {
        const item = document.createElement('div');
        item.className = 'result-item';
        const l = document.createElement('span');
        l.className = 'label';
        l.textContent = label;
        const v = document.createElement('span');
        v.className = 'value';
        v.textContent = String(value);
        item.append(l, v);
        box.appendChild(item);
    });
}

function downloadReport() {
    if (!currentReport) return;
    const blob = new Blob([JSON.stringify(currentReport, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'signal-report.json';
    a.click();
    URL.revokeObjectURL(url);
}

function startNewAnalysis() {
    window.location.href = '/upload';
}
