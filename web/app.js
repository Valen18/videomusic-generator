// VideoMusic Generator - Frontend JavaScript

// Global state
let ws = null;
let clientId = generateUUID();
let currentSessions = [];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎵 VideoMusic Generator initialized');
    checkStatus();
    initWebSocket();
    refreshHistory();
});

// Generate UUID for client identification
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// WebSocket connection
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/${clientId}`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('✅ WebSocket connected');
        // Keep-alive ping every 30 seconds
        setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ command: 'ping' }));
            }
        }, 30000);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };

    ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        showToast('Error de conexión con el servidor', 'error');
    };

    ws.onclose = () => {
        console.log('❌ WebSocket disconnected. Reconnecting...');
        setTimeout(initWebSocket, 3000);
    };
}

// Handle WebSocket messages
function handleWebSocketMessage(data) {
    console.log('📨 WebSocket message:', data);

    switch (data.type) {
        case 'progress':
            updateProgress(data.message);
            break;
        case 'complete':
            handleGenerationComplete(data.data);
            break;
        case 'error':
            handleGenerationError(data.error);
            break;
        case 'pong':
            // Keep-alive response
            break;
    }
}

// Check application status
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();

        updateStatusIndicator(status);
        updateUIBasedOnStatus(status);
    } catch (error) {
        console.error('Error checking status:', error);
        showToast('Error al verificar el estado', 'error');
    }
}

// Update status indicator
function updateStatusIndicator(status) {
    const indicator = document.getElementById('statusIndicator');
    const statusText = indicator.querySelector('.status-text');

    if (status.ready) {
        indicator.classList.add('ready');
        indicator.classList.remove('error');
        statusText.textContent = 'Listo';
    } else {
        indicator.classList.remove('ready');
        indicator.classList.add('error');
        statusText.textContent = 'Configuración requerida';
    }
}

// Update UI based on configuration status
function updateUIBasedOnStatus(status) {
    // Update OpenAI status
    const openaiStatus = document.getElementById('openaiStatus');
    const generateLyricsBtn = document.getElementById('generateLyricsBtn');

    if (status.openai_configured) {
        openaiStatus.textContent = '✓ OpenAI disponible';
        openaiStatus.style.color = 'var(--success-color)';
        generateLyricsBtn.disabled = false;
    } else {
        openaiStatus.textContent = 'OpenAI no configurado (opcional)';
        openaiStatus.style.color = 'var(--text-muted)';
        generateLyricsBtn.disabled = true;
    }

    // Update Replicate status
    const replicateStatus = document.getElementById('replicateStatus');
    const generateImageInput = document.getElementById('generateImageInput');

    if (status.replicate_configured) {
        replicateStatus.textContent = '✓ Replicate disponible';
        replicateStatus.style.color = 'var(--success-color)';
        generateImageInput.disabled = false;
    } else {
        replicateStatus.textContent = 'Replicate no configurado (opcional)';
        replicateStatus.style.color = 'var(--text-muted)';
        generateImageInput.disabled = true;
        generateImageInput.checked = false;
    }

    // Update generate button
    const generateSongBtn = document.getElementById('generateSongBtn');
    if (!status.suno_configured) {
        generateSongBtn.disabled = true;
        showToast('⚠️ Configura tu Suno API Key para generar música', 'warning');
    } else {
        generateSongBtn.disabled = false;
    }
}

// Tab switching
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}Tab`).classList.add('active');

    // Refresh history if switching to history tab
    if (tabName === 'history') {
        refreshHistory();
    }
}

// Generate lyrics with AI
async function generateLyrics() {
    const description = document.getElementById('descriptionInput').value.trim();

    if (!description) {
        showToast('Por favor, ingresa una descripción', 'error');
        return;
    }

    const btn = document.getElementById('generateLyricsBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Generando...';

    try {
        const response = await fetch('/api/generate-lyrics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ description })
        });

        if (!response.ok) {
            throw new Error(await response.text());
        }

        const data = await response.json();
        document.getElementById('lyricsInput').value = data.lyrics;
        showToast('✨ Letra generada con éxito', 'success');
    } catch (error) {
        console.error('Error generating lyrics:', error);
        showToast(`Error al generar letra: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '✨ Generar Letra con IA';
    }
}

// Generate song
function generateSong() {
    const lyrics = document.getElementById('lyricsInput').value.trim();
    const title = document.getElementById('titleInput').value.trim();
    const style = document.getElementById('styleInput').value.trim();

    // Validation
    if (!lyrics) {
        showToast('Por favor, ingresa la letra de la canción', 'error');
        return;
    }

    if (!title) {
        showToast('Por favor, ingresa un título', 'error');
        return;
    }

    if (!style) {
        showToast('Por favor, selecciona un estilo musical', 'error');
        return;
    }

    // Build request
    const request = {
        lyrics: lyrics,
        title: title,
        style: style,
        model: document.getElementById('modelInput').value,
        custom_mode: document.getElementById('customModeInput').checked,
        instrumental: document.getElementById('instrumentalInput').checked,
        generate_image: document.getElementById('generateImageInput').checked
    };

    // Send via WebSocket
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            command: 'generate_song',
            request: request
        }));

        // Show progress
        showProgress('Iniciando generación de canción...');
        document.getElementById('generateSongBtn').disabled = true;
    } else {
        showToast('Error: No hay conexión con el servidor', 'error');
    }
}

// Clear form
function clearForm() {
    document.getElementById('descriptionInput').value = '';
    document.getElementById('lyricsInput').value = '';
    document.getElementById('titleInput').value = '';
    document.getElementById('styleInput').value = '';
    document.getElementById('modelInput').value = 'V4_5';
    document.getElementById('customModeInput').checked = true;
    document.getElementById('instrumentalInput').checked = false;
    document.getElementById('generateImageInput').checked = true;
}

// Progress management
function showProgress(message) {
    const progressSection = document.getElementById('progressSection');
    const progressText = document.getElementById('progressText');
    const progressFill = document.getElementById('progressFill');

    progressSection.style.display = 'block';
    progressText.textContent = message;
    progressFill.style.width = '100%';
}

function updateProgress(message) {
    const progressText = document.getElementById('progressText');
    progressText.textContent = message;
}

function hideProgress() {
    const progressSection = document.getElementById('progressSection');
    progressSection.style.display = 'none';
}

// Generation complete handler
function handleGenerationComplete(data) {
    hideProgress();
    document.getElementById('generateSongBtn').disabled = false;

    showToast(`✅ ¡Canción "${data.title}" generada con éxito!`, 'success');

    // Switch to history tab and refresh
    setTimeout(() => {
        switchTab('history');
        refreshHistory();
    }, 1000);
}

// Generation error handler
function handleGenerationError(error) {
    hideProgress();
    document.getElementById('generateSongBtn').disabled = false;
    showToast(`❌ Error: ${error}`, 'error');
}

// History management
async function refreshHistory() {
    try {
        const response = await fetch('/api/sessions');
        const data = await response.json();

        currentSessions = data.sessions;
        renderSessions(currentSessions);
    } catch (error) {
        console.error('Error loading sessions:', error);
        showToast('Error al cargar el historial', 'error');
    }
}

// Render sessions
function renderSessions(sessions) {
    const sessionsList = document.getElementById('sessionsList');

    if (sessions.length === 0) {
        sessionsList.innerHTML = '<p class="empty-state">No hay sesiones generadas aún</p>';
        return;
    }

    sessionsList.innerHTML = sessions.map(session => `
        <div class="session-card" onclick="openSessionDetail('${session.session_id}')">
            <div class="session-header">
                <h3 class="session-title">${session.title}</h3>
                <p class="session-date">${formatDate(session.timestamp)}</p>
            </div>
            <p class="session-style">${session.style}</p>
            <div class="session-badges">
                ${session.has_audio ? '<span class="badge badge-success">🎵 Audio</span>' : ''}
                ${session.has_image ? '<span class="badge badge-success">🖼️ Imagen</span>' : ''}
                ${session.has_video ? '<span class="badge badge-success">🎬 Video</span>' : ''}
            </div>
            <div class="session-actions" onclick="event.stopPropagation()">
                ${!session.has_image ? `<button class="btn btn-secondary" onclick="generateImageForSession('${session.session_id}')">📸 Imagen</button>` : ''}
                ${session.has_image && !session.has_video ? `<button class="btn btn-secondary" onclick="generateVideoForSession('${session.session_id}')">🎬 Video</button>` : ''}
                ${session.has_video ? `<button class="btn btn-secondary" onclick="loopVideoForSession('${session.session_id}')">🔄 Recrear bucle</button>` : ''}
            </div>
        </div>
    `).join('');
}

// Filter sessions
function filterSessions() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const filtered = currentSessions.filter(session =>
        session.title.toLowerCase().includes(searchTerm) ||
        session.style.toLowerCase().includes(searchTerm)
    );
    renderSessions(filtered);
}

// Format date
function formatDate(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Hace un momento';
    if (diffMins < 60) return `Hace ${diffMins} minuto${diffMins > 1 ? 's' : ''}`;
    if (diffHours < 24) return `Hace ${diffHours} hora${diffHours > 1 ? 's' : ''}`;
    if (diffDays < 7) return `Hace ${diffDays} día${diffDays > 1 ? 's' : ''}`;

    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Open session detail modal
async function openSessionDetail(sessionId) {
    try {
        const response = await fetch(`/api/sessions/${sessionId}`);
        const session = await response.json();

        const modal = document.getElementById('sessionModal');
        document.getElementById('sessionModalTitle').textContent = session.title;

        const modalBody = document.getElementById('sessionModalBody');
        modalBody.innerHTML = `
            <div class="session-detail">
                <h3>Fecha</h3>
                <p>${formatDate(session.timestamp)}</p>
            </div>

            <div class="session-detail">
                <h3>Estilo</h3>
                <p>${session.style}</p>
            </div>

            <div class="session-detail">
                <h3>Letra</h3>
                <div class="lyrics-display">${session.lyrics}</div>
            </div>

            ${session.audio_files.length > 0 ? `
                <div class="session-detail">
                    <h3>Audio</h3>
                    ${session.audio_files.map(audio => `
                        <div class="media-preview">
                            <p>${audio.title}</p>
                            <audio controls src="${audio.url}"></audio>
                        </div>
                    `).join('')}
                </div>
            ` : ''}

            ${session.image_file ? `
                <div class="session-detail">
                    <h3>Imagen de Portada</h3>
                    <div class="media-preview">
                        <img src="${session.image_file.url}" alt="Portada">
                    </div>
                </div>
            ` : ''}

            ${session.video_file ? `
                <div class="session-detail">
                    <h3>Video Animado</h3>
                    <div class="media-preview">
                        <video controls src="${session.video_file.url}"></video>
                    </div>
                </div>
            ` : ''}
        `;

        modal.classList.add('active');
    } catch (error) {
        console.error('Error loading session detail:', error);
        showToast('Error al cargar los detalles de la sesión', 'error');
    }
}

// Close session detail modal
function closeSessionModal() {
    document.getElementById('sessionModal').classList.remove('active');
}

// Generate image for session
function generateImageForSession(sessionId) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            command: 'generate_image',
            session_id: sessionId
        }));

        showToast('🖼️ Generando imagen...', 'success');
    } else {
        showToast('Error: No hay conexión con el servidor', 'error');
    }
}

// Generate video for session
function generateVideoForSession(sessionId) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            command: 'generate_video',
            session_id: sessionId
        }));

        showToast('🎬 Generando video...', 'success');
    } else {
        showToast('Error: No hay conexión con el servidor', 'error');
    }
}

// Loop video for session
function loopVideoForSession(sessionId) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            command: 'loop_video',
            session_id: sessionId
        }));

        showToast('🔄 Recreando bucle de video...', 'success');
    } else {
        showToast('Error: No hay conexión con el servidor', 'error');
    }
}

// Settings management
function openSettings() {
    loadCurrentSettings();
    document.getElementById('settingsModal').classList.add('active');
}

function closeSettings() {
    document.getElementById('settingsModal').classList.remove('active');
}

async function loadCurrentSettings() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();

        document.getElementById('sunoBaseUrlInput').value = config.suno_base_url;
        document.getElementById('openaiAssistantIdInput').value = config.openai_assistant_id;

        // Don't load masked keys
        document.getElementById('sunoApiKeyInput').placeholder = config.suno_api_key ? '***' : 'sk-...';
        document.getElementById('replicateApiTokenInput').placeholder = config.replicate_api_token ? '***' : 'r8_...';
        document.getElementById('openaiApiKeyInput').placeholder = config.openai_api_key ? '***' : 'sk-...';
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

async function saveSettings() {
    const config = {
        suno_api_key: document.getElementById('sunoApiKeyInput').value,
        suno_base_url: document.getElementById('sunoBaseUrlInput').value,
        replicate_api_token: document.getElementById('replicateApiTokenInput').value,
        openai_api_key: document.getElementById('openaiApiKeyInput').value,
        openai_assistant_id: document.getElementById('openaiAssistantIdInput').value
    };

    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        if (!response.ok) {
            throw new Error(await response.text());
        }

        showToast('✅ Configuración guardada', 'success');
        closeSettings();

        // Refresh status
        setTimeout(() => checkStatus(), 1000);
    } catch (error) {
        console.error('Error saving settings:', error);
        showToast(`Error al guardar configuración: ${error.message}`, 'error');
    }
}

// Toast notifications
function showToast(message, type = 'success') {
    // Remove existing toasts
    document.querySelectorAll('.toast').forEach(toast => toast.remove());

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}
