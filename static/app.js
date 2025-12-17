/**
 * Data Analytics Assistant - Frontend Application
 */

// DOM Elements
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const uploadSection = document.getElementById('upload-section');
const datasetSection = document.getElementById('dataset-section');
const chatMessages = document.getElementById('chat-messages');
const chatPlaceholder = document.getElementById('chat-placeholder');
const chatInput = document.getElementById('chat-input');
const btnSend = document.getElementById('btn-send');
const btnClear = document.getElementById('btn-clear');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.getElementById('loading-text');
const apiStatus = document.getElementById('api-status');
const chartsGrid = document.getElementById('charts-grid');

// State
let isDatasetLoaded = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkStatus();
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    // File upload via click
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // Chat
    btnSend.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Clear
    btnClear.addEventListener('click', clearDataset);
}

// Check API Status
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        if (data.api_configured) {
            apiStatus.textContent = 'API Connected';
            apiStatus.className = 'status connected';
        } else {
            apiStatus.textContent = 'API Not Configured';
            apiStatus.className = 'status disconnected';
        }

        // If dataset already loaded (e.g., page refresh with session)
        if (data.dataset_loaded) {
            // Could reload the dataset state here if using server sessions
        }
    } catch (error) {
        apiStatus.textContent = 'Connection Error';
        apiStatus.className = 'status disconnected';
    }
}

// Drag and Drop Handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

// File Selection Handler
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

// Upload File to Server
async function uploadFile(file) {
    // Validate file type
    const validExtensions = ['.csv', '.xlsx', '.xls', '.json'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();

    if (!validExtensions.includes(ext)) {
        showError('Unsupported file type. Please upload CSV, Excel, or JSON files.');
        return;
    }

    showLoading('Analyzing dataset and generating insights...');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            displayDataset(data);
            enableChat();
        } else {
            showError(data.error || 'Failed to upload file');
        }
    } catch (error) {
        showError('Network error. Please try again.');
    } finally {
        hideLoading();
    }
}

// Display Dataset Information
function displayDataset(data) {
    // Hide upload, show dataset section
    uploadSection.classList.add('hidden');
    datasetSection.classList.remove('hidden');

    // Update filename
    document.getElementById('file-name').textContent = data.filename;

    // Update metrics
    document.getElementById('metric-rows').textContent = formatNumber(data.summary.rows);
    document.getElementById('metric-cols').textContent = data.summary.columns;
    document.getElementById('metric-empty').textContent = formatNumber(data.summary.empty_values);

    // Display AI-generated charts
    if (data.charts && data.charts.length > 0) {
        displayCharts(data.charts);
    } else {
        chartsGrid.innerHTML = '<p class="charts-loading">No charts generated</p>';
    }

    // Build preview table
    buildPreviewTable(data.preview);

    isDatasetLoaded = true;
}

// Build Preview Table
function buildPreviewTable(preview) {
    const thead = document.getElementById('table-head');
    const tbody = document.getElementById('table-body');

    // Clear existing
    thead.innerHTML = '';
    tbody.innerHTML = '';

    // Build header
    const headerRow = document.createElement('tr');
    preview.columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);

    // Build body
    preview.data.forEach(row => {
        const tr = document.createElement('tr');
        preview.columns.forEach(col => {
            const td = document.createElement('td');
            const value = row[col];
            td.textContent = value !== null && value !== undefined ? value : '—';
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

// Display AI-Generated Charts
function displayCharts(charts) {
    chartsGrid.innerHTML = '';

    charts.forEach(chart => {
        const card = document.createElement('div');
        card.className = 'chart-card';

        const img = document.createElement('img');
        img.className = 'chart-image';
        img.src = chart.image;
        img.alt = chart.title;

        const info = document.createElement('div');
        info.className = 'chart-info';

        const title = document.createElement('div');
        title.className = 'chart-title';
        title.textContent = chart.title;

        const description = document.createElement('div');
        description.className = 'chart-description';
        description.textContent = chart.description || '';

        info.appendChild(title);
        info.appendChild(description);
        card.appendChild(img);
        card.appendChild(info);
        chartsGrid.appendChild(card);
    });
}

// Enable Chat
function enableChat() {
    chatInput.disabled = false;
    btnSend.disabled = false;
    chatInput.placeholder = 'Ask a question about your data...';
    chatPlaceholder.innerHTML = `
        <span class="placeholder-icon">✨</span>
        <p>Ready! Ask me anything about your dataset.</p>
    `;
}

// Disable Chat
function disableChat() {
    chatInput.disabled = true;
    btnSend.disabled = true;
    chatInput.placeholder = 'Upload a dataset first...';
    chatPlaceholder.innerHTML = `
        <span class="placeholder-icon">💬</span>
        <p>Upload a dataset to start asking questions</p>
    `;
}

// Send Chat Message
async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message || !isDatasetLoaded) return;

    // Clear input
    chatInput.value = '';

    // Hide placeholder if visible
    chatPlaceholder.classList.add('hidden');

    // Add user message
    addMessage(message, 'user');

    // Show typing indicator
    const typingId = showTyping();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        // Remove typing indicator
        removeTyping(typingId);

        if (response.ok && data.success) {
            addMessage(data.response, 'assistant');
        } else {
            addMessage('Sorry, I encountered an error: ' + (data.error || 'Unknown error'), 'assistant');
        }
    } catch (error) {
        removeTyping(typingId);
        addMessage('Sorry, there was a network error. Please try again.', 'assistant');
    }
}

// Add Message to Chat
function addMessage(content, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${role}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;

    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show Typing Indicator
function showTyping() {
    const id = 'typing-' + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.id = id;
    typingDiv.className = 'message message-assistant';
    typingDiv.innerHTML = `
        <div class="message-content" style="padding: 0.5rem 1rem;">
            <span style="animation: pulse 1s infinite;">Thinking...</span>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
}

// Remove Typing Indicator
function removeTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// Clear Dataset
async function clearDataset() {
    try {
        await fetch('/api/clear', { method: 'POST' });
    } catch (error) {
        // Ignore errors
    }

    // Reset UI
    datasetSection.classList.add('hidden');
    uploadSection.classList.remove('hidden');

    // Clear chat
    chatMessages.innerHTML = '';
    chatMessages.appendChild(chatPlaceholder);
    chatPlaceholder.classList.remove('hidden');

    // Disable chat
    disableChat();

    isDatasetLoaded = false;

    // Reset file input
    fileInput.value = '';

    // Clear charts
    chartsGrid.innerHTML = '';
}

// Utility Functions
function formatNumber(num) {
    return num.toLocaleString();
}

function showLoading(text) {
    loadingText.textContent = text || 'Loading...';
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

function showError(message) {
    // Simple alert for now - could be replaced with a toast notification
    alert(message);
}
