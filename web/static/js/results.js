/* ============================================
   Results Page JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    loadResults();
    initializeChart();
});

function loadResults() {
    // Simulate loading results (in production, fetch from server)
    const mockResults = {
        deception_score: 0.65,
        assessment: 'Moderate indicators of potential inconsistency detected',
        facial_analysis: {
            micro_expressions: 'Detected 3 inconsistencies',
            expression_consistency: '78%',
            detected_emotions: 'Neutral, slight concern'
        },
        eye_tracking: {
            gaze_pattern: 'Avoidance noted',
            pupil_dilation: '+12% increase',
            blink_rate: 'Elevated (25 blinks/min)'
        },
        audio_analysis: {
            speech_emotion: 'Anxiety detected',
            pitch_variation: '+8% higher variance',
            pause_patterns: 'Longer hesitation pauses'
        },
        behavioral_consistency: {
            multimodal_alignment: '72%',
            cognitive_load: 'High',
            behavioral_score: 6.8
        },
        evidence: [
            'Eye contact avoidance during specific questions',
            'Micro-expressions conflicting with spoken content',
            'Increased vocal pitch and speech rate',
            'Elevated pupil dilation response',
            'Increased pause duration before responses'
        ],
        recommendations: [
            'Further investigation recommended',
            'Consult with behavioral experts',
            'Review context and baseline behavior',
            'Consider environmental factors'
        ]
    };

    // Update score
    document.getElementById('scoreValue').textContent = (mockResults.deception_score * 100).toFixed(0) + '%';
    document.getElementById('overallAssessment').textContent = mockResults.assessment;

    // Update facial analysis
    document.getElementById('microExpressions').textContent = mockResults.facial_analysis.micro_expressions;
    document.getElementById('expressionConsistency').textContent = mockResults.facial_analysis.expression_consistency;
    document.getElementById('detectedEmotions').textContent = mockResults.facial_analysis.detected_emotions;

    // Update eye tracking
    document.getElementById('gazePattern').textContent = mockResults.eye_tracking.gaze_pattern;
    document.getElementById('pupilDilation').textContent = mockResults.eye_tracking.pupil_dilation;
    document.getElementById('blinkRate').textContent = mockResults.eye_tracking.blink_rate;

    // Update audio analysis
    document.getElementById('speechEmotion').textContent = mockResults.audio_analysis.speech_emotion;
    document.getElementById('pitchVariation').textContent = mockResults.audio_analysis.pitch_variation;
    document.getElementById('pausePatterns').textContent = mockResults.audio_analysis.pause_patterns;

    // Update behavioral consistency
    document.getElementById('multimodalAlignment').textContent = mockResults.behavioral_consistency.multimodal_alignment;
    document.getElementById('cognitiveLoad').textContent = mockResults.behavioral_consistency.cognitive_load;
    document.getElementById('behavioralScore').textContent = mockResults.behavioral_consistency.behavioral_score;

    // Update evidence
    const evidenceList = document.getElementById('evidenceList');
    evidenceList.innerHTML = mockResults.evidence.map(e => 
        `<div class="evidence-item"><strong>▸</strong> ${e}</div>`
    ).join('');

    // Update recommendations
    const recList = document.getElementById('recommendationsList');
    recList.innerHTML = mockResults.recommendations.map(r => 
        `<div class="recommendation-item"><strong>▸</strong> ${r}</div>`
    ).join('');
}

function initializeChart() {
    const ctx = document.getElementById('timelineChart');
    if (!ctx) return;

    // Read theme colors from CSS variables
    const css = getComputedStyle(document.documentElement);
    const primary = css.getPropertyValue('--primary-color').trim() || '#6366f1';
    const primaryDark = css.getPropertyValue('--primary-dark').trim() || '#4f46e5';
    const secondary = css.getPropertyValue('--secondary-color').trim() || '#10b981';

    function hexToRgba(hex, alpha) {
        if (!hex) return `rgba(255,255,255,${alpha})`;
        const h = hex.replace('#', '').trim();
        const bigint = parseInt(h.length === 3 ? h.split('').map(c=>c+c).join('') : h, 16);
        const r = (bigint >> 16) & 255;
        const g = (bigint >> 8) & 255;
        const b = bigint & 255;
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['0s', '10s', '20s', '30s', '40s', '50s', '60s'],
            datasets: [
                {
                    label: 'Deception Score',
                    data: [0.3, 0.4, 0.65, 0.7, 0.65, 0.6, 0.55],
                    borderColor: primary,
                    backgroundColor: hexToRgba(primary, 0.12),
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Cognitive Load',
                    data: [0.4, 0.5, 0.75, 0.8, 0.7, 0.6, 0.5],
                    borderColor: primaryDark,
                    backgroundColor: hexToRgba(primaryDark, 0.12),
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Consistency Score',
                    data: [0.8, 0.75, 0.65, 0.6, 0.65, 0.7, 0.75],
                    borderColor: secondary,
                    backgroundColor: hexToRgba(secondary, 0.12),
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: css.getPropertyValue('--text-secondary').trim() || '#cbd5e1'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    grid: {
                        color: css.getPropertyValue('--surface-light').trim() || '#334155'
                    },
                    ticks: {
                        color: css.getPropertyValue('--text-secondary').trim() || '#cbd5e1'
                    }
                },
                x: {
                    grid: {
                        color: css.getPropertyValue('--surface-light').trim() || '#334155'
                    },
                    ticks: {
                        color: css.getPropertyValue('--text-secondary').trim() || '#cbd5e1'
                    }
                }
            }
        }
    });
}

function downloadReport() {
    alert('Report download feature coming soon!');
    // TODO: Implement report generation and download
}

function startNewAnalysis() {
    window.location.href = '/upload';
}
