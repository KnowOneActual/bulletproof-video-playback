// Bulletproof Video Dashboard - JavaScript

const API_BASE = '/api/v1';
const WS_URL = `ws://${window.location.host}/api/v1/stream`;

let ws = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
let currentJobs = [];

// DOM elements
const monitorStatusEl = document.getElementById('monitor-status');
const watchDirEl = document.getElementById('watch-dir');
const outputDirEl = document.getElementById('output-dir');
const totalJobsEl = document.getElementById('total-jobs');
const pendingJobsEl = document.getElementById('pending-jobs');
const processingJobsEl = document.getElementById('processing-jobs');
const completeJobsEl = document.getElementById('complete-jobs');
const errorJobsEl = document.getElementById('error-jobs');
const jobTableBodyEl = document.getElementById('job-table-body');
const websocketStatusEl = document.getElementById('websocket-status');
const lastUpdateEl = document.getElementById('last-update');
const pauseBtn = document.getElementById('pause-btn');
const resumeBtn = document.getElementById('resume-btn');
const clearBtn = document.getElementById('clear-btn');
const reconnectBtn = document.getElementById('reconnect-btn');
const versionEl = document.getElementById('version');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    fetchVersion();
    fetchMonitorStatus();
    fetchQueue();
    connectWebSocket();
    setupEventListeners();
});

// Fetch version from root endpoint
async function fetchVersion() {
    try {
        const response = await fetch('/');
        if (response.ok) {
            const data = await response.json();
            versionEl.textContent = data.version || '3.2.1';
        }
    } catch (err) {
        console.error('Failed to fetch version:', err);
    }
}

// Fetch monitor status
async function fetchMonitorStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        if (response.ok) {
            const data = await response.json();
            updateMonitorStatus(data);
        }
    } catch (err) {
        console.error('Failed to fetch monitor status:', err);
        monitorStatusEl.textContent = 'Error';
        monitorStatusEl.className = 'tag is-danger';
    }
}

// Update monitor status UI
function updateMonitorStatus(data) {
    watchDirEl.textContent = data.watch_directory;
    outputDirEl.textContent = data.output_directory;
    monitorStatusEl.textContent = data.running ? (data.paused ? 'Paused' : 'Running') : 'Stopped';
    monitorStatusEl.className = data.running ? (data.paused ? 'tag is-warning' : 'tag is-success') : 'tag is-danger';
}

// Fetch queue data
async function fetchQueue() {
    try {
        const response = await fetch(`${API_BASE}/queue`);
        if (response.ok) {
            const data = await response.json();
            updateQueueStats(data);
            updateJobTable(data);
        }
    } catch (err) {
        console.error('Failed to fetch queue:', err);
    }
}

// Update queue statistics
function updateQueueStats(data) {
    totalJobsEl.textContent = data.total_jobs;
    pendingJobsEl.textContent = data.pending_jobs;
    processingJobsEl.textContent = data.processing_jobs;
    completeJobsEl.textContent = data.complete_jobs;
    errorJobsEl.textContent = data.error_jobs;
}

// Update job table
function updateJobTable(data) {
    const jobs = data.jobs || [];
    const currentJob = data.current_job;

    // Combine current job with pending jobs
    const allJobs = currentJob ? [currentJob, ...jobs.filter(j => j.id !== currentJob.id)] : jobs;
    currentJobs = allJobs;

    if (allJobs.length === 0) {
        jobTableBodyEl.innerHTML = `
            <tr>
                <td colspan="6" class="has-text-centered">No jobs in queue</td>
            </tr>
        `;
        return;
    }

    const rows = allJobs.map(job => createJobRow(job));
    jobTableBodyEl.innerHTML = rows.join('');
}

// Create a single job row HTML
function createJobRow(job) {
    const statusClass = `job-status-${job.status}`;
    const statusTag = getStatusTag(job.status);
    const progressBar = job.status === 'processing' ? createProgressBar(job.progress) : '';

    return `
        <tr class="${statusClass}">
            <td><code>${job.id.substring(0, 8)}</code></td>
            <td class="is-family-monospace">${job.input_file.split('/').pop()}</td>
            <td><span class="tag is-light">${job.profile_name}</span></td>
            <td>${statusTag}</td>
            <td>
                ${progressBar}
                <span class="is-size-7">${job.progress.toFixed(1)}%</span>
            </td>
            <td>
                ${createActionButtons(job)}
            </td>
        </tr>
    `;
}

// Get status tag HTML
function getStatusTag(status) {
    const map = {
        'pending': { text: 'Pending', class: 'is-info' },
        'processing': { text: 'Processing', class: 'is-warning' },
        'complete': { text: 'Complete', class: 'is-success' },
        'error': { text: 'Error', class: 'is-danger' },
        'cancelled': { text: 'Cancelled', class: 'is-light' }
    };
    const info = map[status] || { text: status, class: 'is-light' };
    return `<span class="tag ${info.class}">${info.text}</span>`;
}

// Create progress bar HTML
function createProgressBar(progress) {
    return `
        <progress class="progress is-small is-warning" value="${progress}" max="100">
            ${progress}%
        </progress>
    `;
}

// Create action buttons for a job
function createActionButtons(job) {
    const buttons = [];
    // Details button for all jobs
    buttons.push(`
        <button class="button is-small is-info" onclick="showJobDetails('${job.id}')">
            <span class="icon is-small"><i class="fas fa-info-circle"></i></span>
            <span>Details</span>
        </button>
    `);
    if (job.status === 'pending' || job.status === 'processing') {
        buttons.push(`
            <button class="button is-small is-danger" onclick="cancelJob('${job.id}')">
                <span class="icon is-small"><i class="fas fa-ban"></i></span>
                <span>Cancel</span>
            </button>
        `);
    }
    if (job.status === 'error') {
        buttons.push(`
            <button class="button is-small is-warning" onclick="retryJob('${job.id}')">
                <span class="icon is-small"><i class="fas fa-redo"></i></span>
                <span>Retry</span>
            </button>
        `);
    }
    return buttons.join(' ');
}

// WebSocket connection
function connectWebSocket() {
    try {
        ws = new WebSocket(WS_URL);
        ws.onopen = onWebSocketOpen;
        ws.onmessage = onWebSocketMessage;
        ws.onclose = onWebSocketClose;
        ws.onerror = onWebSocketError;
    } catch (err) {
        console.error('WebSocket connection error:', err);
        updateWebSocketStatus('error', 'Connection failed');
    }
}

function onWebSocketOpen() {
    reconnectAttempts = 0;
    updateWebSocketStatus('connected', 'Connected');
}

function onWebSocketMessage(event) {
    const message = JSON.parse(event.data);
    handleWebSocketEvent(message);
    lastUpdateEl.textContent = new Date().toLocaleTimeString();
}

function onWebSocketClose() {
    updateWebSocketStatus('disconnected', 'Disconnected');
    // Attempt reconnect with exponential backoff
    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 10000);
        setTimeout(connectWebSocket, delay);
    }
}

function onWebSocketError(err) {
    console.error('WebSocket error:', err);
    updateWebSocketStatus('error', 'Error');
}

function updateWebSocketStatus(status, text) {
    websocketStatusEl.textContent = text;
    websocketStatusEl.className = 'tag';
    if (status === 'connected') {
        websocketStatusEl.classList.add('is-success');
    } else if (status === 'disconnected') {
        websocketStatusEl.classList.add('is-light');
    } else {
        websocketStatusEl.classList.add('is-danger');
    }
}

// Handle WebSocket events
function handleWebSocketEvent(message) {
    switch (message.type) {
        case 'status':
            // Update queue stats
            fetchQueue();
            break;
        case 'job_update':
            // Update specific job
            fetchQueue();
            break;
        case 'error':
            console.error('WebSocket error event:', message.data);
            break;
        default:
            console.log('Unhandled WebSocket event:', message);
    }
}

// Event listeners for buttons
function setupEventListeners() {
    pauseBtn.addEventListener('click', pauseQueue);
    resumeBtn.addEventListener('click', resumeQueue);
    clearBtn.addEventListener('click', clearQueue);
    reconnectBtn.addEventListener('click', reconnectWebSocket);
}

// API actions
async function pauseQueue() {
    try {
        const response = await fetch(`${API_BASE}/queue/pause`, { method: 'POST' });
        if (response.ok) {
            fetchMonitorStatus();
        } else {
            alert('Failed to pause queue');
        }
    } catch (err) {
        console.error('Error pausing queue:', err);
    }
}

async function resumeQueue() {
    try {
        const response = await fetch(`${API_BASE}/queue/resume`, { method: 'POST' });
        if (response.ok) {
            fetchMonitorStatus();
        } else {
            alert('Failed to resume queue');
        }
    } catch (err) {
        console.error('Error resuming queue:', err);
    }
}

async function clearQueue() {
    if (!confirm('Are you sure you want to clear all pending jobs?')) return;
    try {
        const response = await fetch(`${API_BASE}/queue/clear`, { method: 'POST' });
        if (response.ok) {
            fetchQueue();
        } else {
            alert('Failed to clear queue');
        }
    } catch (err) {
        console.error('Error clearing queue:', err);
    }
}

// Job actions (exposed globally for button onclick)
window.cancelJob = async function(jobId) {
    try {
        const response = await fetch(`${API_BASE}/jobs/${jobId}/cancel`, { method: 'POST' });
        if (response.ok) {
            fetchQueue();
        } else {
            alert('Failed to cancel job');
        }
    } catch (err) {
        console.error('Error cancelling job:', err);
    }
};

window.retryJob = async function(jobId) {
    try {
        const response = await fetch(`${API_BASE}/jobs/${jobId}/retry`, { method: 'POST' });
        if (response.ok) {
            fetchQueue();
        } else {
            alert('Failed to retry job');
        }
    } catch (err) {
        console.error('Error retrying job:', err);
    }
};

function reconnectWebSocket() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
    }
    connectWebSocket();
}

// Poll for updates every 30 seconds as a fallback
setInterval(fetchQueue, 30000);