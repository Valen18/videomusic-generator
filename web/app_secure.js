// VideoMusic Generator - Frontend JavaScript (Secure Version with Auth)

// Global state
let ws = null;
let clientId = generateUUID();
let currentSessions = [];
let currentUser = null;
let currentGeneratingSessionId = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎵 VideoMusic Generator initialized (Secure)');

    // Only initialize if we have the main app elements (not on login page)
    if (document.getElementById('statusIndicator')) {
        loadCurrentUser();
        checkStatus();
        initWebSocket();
        refreshHistory();
    }
});

// Get authentication token from cookie
function getAuthToken() {
    const name = "auth_token=";
    const decodedCookie = decodeURIComponent(document.cookie);
    console.log('🍪 Cookies disponibles:', document.cookie);
    console.log('🍪 Cookies decodificadas:', decodedCookie);
    const ca = decodedCookie.split(';');
    for(let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            const token = c.substring(name.length, c.length);
            console.log('✅ Token encontrado:', token.substring(0, 20) + '...');
            return token;
        }
    }
    console.log('❌ Token NO encontrado');
    return null;
}

// Load current user
async function loadCurrentUser() {
    try {
        const response = await fetch('/api/auth/me');
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            updateUserDisplay();
        } else {
            // Not authenticated, redirect to login (only once)
            if (!window.location.pathname.includes('login')) {
                window.location.href = '/';
            }
        }
    } catch (error) {
        console.error('Error loading user:', error);
        // Don't redirect if already on login page
        if (!window.location.pathname.includes('login')) {
            window.location.href = '/';
        }
    }
}

// Update user display
function updateUserDisplay() {
    const userDisplay = document.getElementById('userDisplay');
    if (userDisplay && currentUser) {
        userDisplay.innerHTML = `
            <span class="user-info">👤 ${currentUser.username}</span>
            <button class="btn btn-secondary" onclick="logout()">Cerrar Sesión</button>
        `;
    }
}

// Logout
async function logout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        window.location.href = '/';
    } catch (error) {
        console.error('Error logging out:', error);
        showToast('Error al cerrar sesión', 'error');
    }
}

// Generate UUID for client identification
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// WebSocket connection with authentication
function initWebSocket() {
    const token = getAuthToken();
    if (!token) {
        console.error('No auth token found');
        return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/${clientId}?token=${token}`;

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
            // Check for image completion
            if (data.message.includes('¡Imagen generada!') || data.message.includes('Imagen guardada:')) {
                loadCurrentSessionPreview();
            }
            // Check for loop completion
            if (data.message.includes('Loop creado exitosamente') || data.message.includes('actualizado exitosamente')) {
                setTimeout(() => {
                    hideProgress();
                    showToast('✅ Loop actualizado con subtítulos personalizados', 'success');
                    refreshHistory();
                }, 1000);
            }
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

// Validate APIs
async function validateAPIs() {
    const btn = event.target;
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Validando...';

    try {
        const response = await fetch('/api/validate-apis', { method: 'POST' });
        const data = await response.json();

        const results = data.results;
        let message = 'Resultados de validación:\n\n';

        for (const [api, [isValid, msg]] of Object.entries(results)) {
            message += `${msg}\n`;
        }

        alert(message);

    } catch (error) {
        showToast(`Error al validar APIs: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🔍 Validar Conectividad';
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

    // Reset progress bar to 0%
    progressFill.style.width = '0%';
    progressFill.style.background = 'linear-gradient(90deg, #667eea, #764ba2)';
    progressFill.style.transition = 'width 0.5s ease';

    // Animate to 5% to show it started
    setTimeout(() => {
        progressFill.style.width = '5%';
    }, 100);
}

function updateProgress(message) {
    const progressText = document.getElementById('progressText');
    const progressFill = document.getElementById('progressFill');
    const progressSection = document.getElementById('progressSection');

    progressText.textContent = message;
    console.log('📊 Progreso:', message);

    // Show progress section
    progressSection.style.display = 'block';

    // Calculate progress percentage based on message keywords
    let progress = 0;
    const msg = message.toLowerCase();

    // Determine progress based on keywords
    if (msg.includes('iniciando') || msg.includes('creando sesión')) {
        progress = 5;
    } else if (msg.includes('enviando') || msg.includes('petición')) {
        progress = 15;
    } else if (msg.includes('esperando') && msg.includes('música')) {
        progress = 25;
    } else if (msg.includes('estado música')) {
        progress = 35;
    } else if (msg.includes('descargando') && msg.includes('audio')) {
        progress = 50;
    } else if (msg.includes('generando imagen') || msg.includes('enviando imagen')) {
        progress = 60;
    } else if (msg.includes('esperando') && msg.includes('imagen')) {
        progress = 70;
    } else if (msg.includes('descargando imagen')) {
        progress = 75;
    } else if (msg.includes('creando video') || msg.includes('enviando') && msg.includes('video')) {
        progress = 80;
    } else if (msg.includes('esperando') && msg.includes('video')) {
        progress = 85;
    } else if (msg.includes('descargando video')) {
        progress = 90;
    } else if (msg.includes('bucle') || msg.includes('loop') || msg.includes('subtítulos') || msg.includes('karaoke')) {
        progress = 95;
    } else if (msg.includes('completada') || msg.includes('exitosamente') || msg.includes('creado') || msg.includes('actualizado')) {
        progress = 100;
    } else if (msg.includes('error')) {
        progress = 0;
    } else {
        // Gradual progress for unknown steps
        const currentProgress = parseInt(progressFill.style.width) || 0;
        progress = Math.min(currentProgress + 5, 98);
    }

    // Animate progress bar
    progressFill.style.width = progress + '%';
    progressFill.style.transition = 'width 0.5s ease';

    // Change color based on state
    if (msg.includes('error')) {
        progressFill.style.background = 'linear-gradient(90deg, #ef4444, #dc2626)';
    } else if (progress === 100) {
        progressFill.style.background = 'linear-gradient(90deg, #10b981, #059669)';
    } else {
        progressFill.style.background = 'linear-gradient(90deg, #667eea, #764ba2)';
    }

    // Also show a toast for important updates
    if (message.includes('completada') || message.includes('Error') || message.includes('Descargando')) {
        showToast(message, message.includes('Error') ? 'error' : 'success');
    }
}

function hideProgress() {
    const progressSection = document.getElementById('progressSection');
    progressSection.style.display = 'none';
}

// Generation complete handler
function handleGenerationComplete(data) {
    hideProgress();
    document.getElementById('generateSongBtn').disabled = false;
    currentGeneratingSessionId = data.session_id;

    showToast(`✅ ¡Canción "${data.title}" generada con éxito!`, 'success');

    // Load and show the generated content immediately
    loadCurrentSessionPreview();

    // Switch to history tab and refresh
    setTimeout(() => {
        switchTab('history');
        refreshHistory();
    }, 1500);
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
async function renderSessions(sessions) {
    const sessionsList = document.getElementById('sessionsList');

    if (sessions.length === 0) {
        sessionsList.innerHTML = '<p class="empty-state">No hay sesiones generadas aún</p>';
        return;
    }

    // Render cards with clean Spotify-like design
    sessionsList.innerHTML = sessions.map(session => `
        <div class="session-card-wrapper" id="session-${session.session_id}">
            <!-- Cover Image with fixed 16:9 aspect ratio -->
            <div class="cover-container" id="cover-${session.session_id}">
                <div class="absolute inset-0 flex items-center justify-center text-white text-5xl opacity-30">
                    🎵
                </div>
            </div>

            <!-- Content section -->
            <div class="session-content">
                <!-- Title and info -->
                <div>
                    <h3 class="text-lg font-bold text-white truncate">${session.title}</h3>
                    <p class="text-sm text-gray-400 truncate">${session.style}</p>
                    <p class="text-xs text-gray-500">${formatDate(session.timestamp)}</p>
                </div>

                <!-- Audio players -->
                <div id="audio-${session.session_id}" class="space-y-2">
                    <!-- Audio loaded dynamically -->
                </div>

                <!-- Video player (if exists) -->
                <div id="video-${session.session_id}">
                    <!-- Video loaded dynamically -->
                </div>

                <!-- Action buttons -->
                <div class="flex gap-2 flex-wrap">
                    ${!session.has_image ? `<button class="px-3 py-1.5 text-xs bg-slate-700 hover:bg-slate-600 text-white rounded-md transition" onclick="generateImageForSession('${session.session_id}')">📸 Imagen</button>` : ''}
                    ${session.has_image && !session.has_video ? `<button class="px-3 py-1.5 text-xs bg-slate-700 hover:bg-slate-600 text-white rounded-md transition" onclick="generateVideoForSession('${session.session_id}')">🎬 Video</button>` : ''}
                    ${session.has_video ? `<button class="px-3 py-1.5 text-xs bg-slate-700 hover:bg-slate-600 text-white rounded-md transition" onclick="loopVideoForSession('${session.session_id}')">🔄 Loop</button>` : ''}
                </div>
            </div>
        </div>
    `).join('');

    // Load content for each session
    for (const session of sessions) {
        loadSessionContent(session.session_id);
    }
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

        showProgress('🎬 Iniciando generación de video animado...');
        showToast('🎬 Generando video...', 'success');
    } else {
        showToast('Error: No hay conexión con el servidor', 'error');
    }
}

// Loop video for session - Open configuration modal first
let currentLoopSessionId = null;

function loopVideoForSession(sessionId) {
    currentLoopSessionId = sessionId;
    openSubtitleConfig();
}

function openSubtitleConfig() {
    const modal = document.getElementById('subtitleConfigModal');
    modal.classList.add('active');

    // Update value displays when sliders change
    document.getElementById('subtitleFontSize').oninput = function() {
        document.getElementById('fontSizeValue').textContent = this.value + 'px';
    };

    document.getElementById('subtitleOutlineWidth').oninput = function() {
        document.getElementById('outlineWidthValue').textContent = this.value + 'px';
    };

    document.getElementById('subtitleFontColor').oninput = function() {
        document.getElementById('fontColorValue').textContent = this.value;
    };

    document.getElementById('subtitleOutlineColor').oninput = function() {
        document.getElementById('outlineColorValue').textContent = this.value;
    };
}

function closeSubtitleConfig() {
    const modal = document.getElementById('subtitleConfigModal');
    modal.classList.remove('active');
    currentLoopSessionId = null;
}

function applySubtitleConfigAndGenerate() {
    if (!currentLoopSessionId) {
        showToast('Error: No se ha seleccionado una sesión', 'error');
        return;
    }

    // Get configuration values
    const config = {
        fontSize: parseInt(document.getElementById('subtitleFontSize').value),
        fontColor: document.getElementById('subtitleFontColor').value,
        outlineColor: document.getElementById('subtitleOutlineColor').value,
        outlineWidth: parseInt(document.getElementById('subtitleOutlineWidth').value),
        animation: document.getElementById('subtitleAnimation').value,
        position: document.getElementById('subtitlePosition').value,
        enableSyncAdjustment: document.getElementById('enableSyncAdjustment').checked
    };

    // Send command with configuration
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            command: 'loop_video',
            session_id: currentLoopSessionId,
            subtitle_config: config
        }));

        showProgress('🔄 Iniciando creación de loop con subtítulos personalizados...');
        showToast('🔄 Recreando bucle de video con tu configuración...', 'success');
        closeSubtitleConfig();
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

// Load and display preview of currently generating session
async function loadCurrentSessionPreview() {
    if (!currentGeneratingSessionId) {
        console.log('No current session to preview');
        return;
    }

    try {
        const response = await fetch(`/api/sessions/${currentGeneratingSessionId}`);
        if (!response.ok) {
            console.error('Failed to load session for preview');
            return;
        }

        const session = await response.json();
        displaySessionPreview(session);
    } catch (error) {
        console.error('Error loading session preview:', error);
    }
}

// Load session content (cover image + audio players + video)
async function loadSessionContent(sessionId) {
    const coverDiv = document.getElementById(`cover-${sessionId}`);
    const audioDiv = document.getElementById(`audio-${sessionId}`);
    const videoDiv = document.getElementById(`video-${sessionId}`);

    try {
        const response = await fetch(`/api/sessions/${sessionId}`);
        if (!response.ok) {
            throw new Error('Failed to load session content');
        }

        const session = await response.json();

        // Load cover image - replaces the placeholder
        if (session.image_file && session.image_file.url) {
            coverDiv.innerHTML = `<img src="${session.image_file.url}" alt="${session.title}">`;
        }

        // Load audio players with compact design
        if (session.audio_files && session.audio_files.length > 0) {
            let audioHTML = '';
            session.audio_files.forEach((audio, index) => {
                audioHTML += `
                    <div>
                        <label class="text-xs text-gray-400 block mb-1">Opción ${index + 1}</label>
                        <audio controls preload="metadata" class="audio-compact">
                            <source src="${audio.url}" type="audio/mpeg">
                        </audio>
                    </div>
                `;
            });
            audioDiv.innerHTML = audioHTML;
        }

        // Load video if available
        if (session.video_file && session.video_file.url) {
            videoDiv.innerHTML = `
                <div>
                    <label class="text-xs text-gray-400 block mb-1">Video Loop</label>
                    <video controls preload="metadata" class="w-full rounded-lg" style="max-height: 300px;">
                        <source src="${session.video_file.url}" type="video/mp4">
                    </video>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading session content:', error);
        coverDiv.innerHTML = '<div class="absolute inset-0 flex items-center justify-center text-red-500 text-3xl">❌</div>';
    }
}

// Display session preview
function displaySessionPreview(session) {
    const previewSection = document.getElementById('previewSection');
    const imagePreview = document.getElementById('imagePreview');
    const audioPreview = document.getElementById('audioPreview');
    const videoPreview = document.getElementById('videoPreview');

    let hasContent = false;

    // Show image if available
    if (session.image_file && session.image_file.url) {
        const img = document.getElementById('previewImage');
        img.src = session.image_file.url;
        imagePreview.style.display = 'block';
        hasContent = true;
        console.log('✅ Showing image preview');
    } else {
        imagePreview.style.display = 'none';
    }

    // Show audio players if available
    if (session.audio_files && session.audio_files.length > 0) {
        const audioPlayers = document.getElementById('audioPlayers');
        audioPlayers.innerHTML = session.audio_files.map((audio, index) => `
            <div class="audio-player-item">
                <p style="margin: 0 0 8px 0; font-weight: 600;">Track ${index + 1}: ${audio.title || 'Sin título'}</p>
                <audio controls preload="auto">
                    <source src="${audio.url}" type="audio/mpeg">
                    Tu navegador no soporta el elemento de audio.
                </audio>
            </div>
        `).join('');
        audioPreview.style.display = 'block';
        hasContent = true;
        console.log('✅ Showing audio preview');
    } else {
        audioPreview.style.display = 'none';
    }

    // Show video if available
    if (session.video_file && session.video_file.url) {
        const video = document.getElementById('previewVideo');
        video.src = session.video_file.url;
        videoPreview.style.display = 'block';
        hasContent = true;
        console.log('✅ Showing video preview');
    } else {
        videoPreview.style.display = 'none';
    }

    // Show/hide the preview section based on content availability
    if (hasContent) {
        previewSection.style.display = 'block';
        console.log('📺 Preview section visible');
    } else {
        previewSection.style.display = 'none';
        console.log('⏳ No preview content available yet');
    }
}
