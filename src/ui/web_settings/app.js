/**
 * Whisper Cheap Settings - JavaScript Application
 *
 * Handles UI interactions and communicates with Python backend via pywebview.api
 */

// =============================================================================
// STATE
// =============================================================================

let config = {};
let defaultModels = [];
let userModels = [];
let currentModel = '';
let currentSection = 'general';
let modelsPricing = {}; // {model_id: {input: float, output: float}}

// Hotkey capture state
let capturingHotkey = false;
let capturedKeys = new Set();
let originalHotkey = '';

// Auto-save debounce
let saveTimer = null;
let pricingFetchInProgress = false;

// =============================================================================
// INITIALIZATION
// =============================================================================

window.addEventListener('pywebviewready', async () => {
    console.log('[Settings] pywebview ready');
    await loadConfig();
    await loadModels();
    await loadDevices();
    await loadHistory();
    populateUI();
    showSection('general');

    // Auto-fetch pricing in background if cache is empty
    if (Object.keys(modelsPricing).length === 0) {
        console.log('[Settings] Pricing cache empty, fetching from OpenRouter...');
        await fetchOpenrouterPricing();
    }
});

async function loadConfig() {
    try {
        config = await pywebview.api.get_config();
        console.log('[Settings] Config loaded');
    } catch (e) {
        console.error('[Settings] Failed to load config:', e);
        config = {};
    }
}

async function loadModels() {
    try {
        defaultModels = await pywebview.api.get_default_models();
        userModels = config.post_processing?.custom_models || [];
        currentModel = config.post_processing?.model || defaultModels[0] || '';

        console.log('[Settings] Default models:', defaultModels);
        console.log('[Settings] User models:', userModels);
        console.log('[Settings] Current model:', currentModel);

        // Load cached pricing
        modelsPricing = await pywebview.api.get_all_models_pricing();
        console.log('[Settings] Pricing cache:', Object.keys(modelsPricing).length, 'models');

        renderModelList();
    } catch (e) {
        console.error('[Settings] Failed to load models:', e);
    }
}

async function loadDevices() {
    try {
        const devices = await pywebview.api.get_audio_devices();
        const select = document.getElementById('audio-device');
        select.innerHTML = '<option value="">System Default</option>';

        devices.forEach(d => {
            const option = document.createElement('option');
            option.value = d.id;
            option.textContent = `${d.id}: ${d.name}`;
            select.appendChild(option);
        });

        // Set current value
        const deviceId = config.audio?.device_id;
        if (deviceId !== null && deviceId !== undefined) {
            select.value = deviceId;
        }
    } catch (e) {
        console.error('[Settings] Failed to load devices:', e);
    }
}

async function refreshDevices() {
    await loadDevices();
}

// =============================================================================
// UI POPULATION
// =============================================================================

function populateUI() {
    // General
    document.getElementById('hotkey-input').value = config.hotkey || 'ctrl+shift+space';

    const mode = config.mode?.activation_mode || 'ptt';
    document.querySelectorAll('input[name="mode"]').forEach(r => {
        r.checked = r.value === mode;
    });

    document.getElementById('start-on-boot').checked = config.general?.start_on_boot || false;
    document.getElementById('clipboard-policy').value = config.clipboard?.policy || 'dont_modify';

    // Overlay
    document.getElementById('overlay-enabled').checked = config.overlay?.enabled !== false;
    document.getElementById('overlay-position').value = config.overlay?.position || 'bottom';

    const opacity = Math.round((config.overlay?.opacity || 0.85) * 100);
    document.getElementById('overlay-opacity').value = opacity;
    updateOpacityLabel();

    // AI
    document.getElementById('ai-enabled').checked = config.post_processing?.enabled || false;
    document.getElementById('api-key').value = config.post_processing?.openrouter_api_key || '';
}

function updateOpacityLabel() {
    const val = document.getElementById('overlay-opacity').value;
    document.getElementById('opacity-label').textContent = val + '%';
}

// =============================================================================
// NAVIGATION
// =============================================================================

function showSection(name) {
    currentSection = name;

    // Hide all sections
    document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));

    // Show selected section
    const section = document.getElementById('section-' + name);
    if (section) section.classList.remove('hidden');

    // Update nav buttons - clean active state
    document.querySelectorAll('.nav-btn').forEach(btn => {
        const isActive = btn.dataset.nav === name;
        btn.classList.toggle('active', isActive);
        btn.classList.toggle('text-text-secondary', !isActive);
    });

    // Refresh history when switching to that tab
    if (name === 'history') {
        loadHistory();
    }
}

// =============================================================================
// CONFIG SAVING
// =============================================================================

function updateConfig() {
    // Debounce save
    clearTimeout(saveTimer);
    saveTimer = setTimeout(saveConfig, 500);
}

async function saveConfig() {
    // Build config from UI
    config.hotkey = document.getElementById('hotkey-input').value;

    config.mode = config.mode || {};
    const modeRadio = document.querySelector('input[name="mode"]:checked');
    config.mode.activation_mode = modeRadio ? modeRadio.value : 'ptt';

    config.general = config.general || {};
    config.general.start_on_boot = document.getElementById('start-on-boot').checked;

    config.clipboard = config.clipboard || {};
    config.clipboard.policy = document.getElementById('clipboard-policy').value;

    // Audio
    config.audio = config.audio || {};
    const deviceVal = document.getElementById('audio-device').value;
    config.audio.device_id = deviceVal === '' ? null : parseInt(deviceVal);

    // Overlay
    config.overlay = config.overlay || {};
    config.overlay.enabled = document.getElementById('overlay-enabled').checked;
    config.overlay.position = document.getElementById('overlay-position').value;
    config.overlay.opacity = parseInt(document.getElementById('overlay-opacity').value) / 100;

    // AI
    config.post_processing = config.post_processing || {};
    config.post_processing.enabled = document.getElementById('ai-enabled').checked;
    config.post_processing.openrouter_api_key = document.getElementById('api-key').value;
    config.post_processing.model = currentModel;
    config.post_processing.custom_models = userModels;

    // Save
    try {
        await pywebview.api.save_config(config);
        console.log('[Settings] Config saved');
    } catch (e) {
        console.error('[Settings] Failed to save config:', e);
    }
}

// =============================================================================
// HOTKEY CAPTURE
// =============================================================================

function startHotkeyCapture() {
    if (capturingHotkey) return;

    capturingHotkey = true;
    capturedKeys.clear();
    originalHotkey = document.getElementById('hotkey-input').value;

    const input = document.getElementById('hotkey-input');
    const btn = document.getElementById('hotkey-btn');

    input.value = 'Press keys...';
    input.classList.add('border-accent');
    btn.textContent = 'CANCEL';
    btn.classList.remove('bg-accent', 'hover:bg-accent-hover');
    btn.classList.add('bg-red-500', 'hover:bg-red-600');
    btn.onclick = cancelHotkeyCapture;

    document.addEventListener('keydown', captureKeyDown);
    document.addEventListener('keyup', captureKeyUp);
}

function captureKeyDown(e) {
    if (!capturingHotkey) return;
    e.preventDefault();
    e.stopPropagation();

    // Map key
    let key = mapKey(e);
    if (key) {
        capturedKeys.add(key);
        updateHotkeyDisplay();
    }

    // Enter to confirm
    if (e.key === 'Enter' && capturedKeys.size > 0) {
        confirmHotkey();
    }

    // Escape to cancel
    if (e.key === 'Escape') {
        cancelHotkeyCapture();
    }
}

function captureKeyUp(e) {
    if (!capturingHotkey) return;

    // When a non-modifier key is released, confirm if we have keys
    const key = mapKey(e);
    if (key && !['ctrl', 'shift', 'alt', 'win'].includes(key) && capturedKeys.size > 0) {
        confirmHotkey();
    }
}

function mapKey(e) {
    // Modifiers
    if (e.key === 'Control') return 'ctrl';
    if (e.key === 'Shift') return 'shift';
    if (e.key === 'Alt') return 'alt';
    if (e.key === 'Meta') return 'win';

    // Special keys
    if (e.key === 'Enter') return null; // Used for confirm
    if (e.key === 'Escape') return null; // Used for cancel

    // Space
    if (e.key === ' ' || e.code === 'Space') return 'space';

    // Arrow keys
    if (e.key.startsWith('Arrow')) return e.key.toLowerCase().replace('arrow', '');

    // Function keys
    if (e.key.startsWith('F') && e.key.length <= 3) return e.key.toLowerCase();

    // Regular keys
    if (e.key.length === 1) return e.key.toLowerCase();

    // Fallback to code
    return e.code.toLowerCase().replace('key', '').replace('digit', '');
}

function updateHotkeyDisplay() {
    const input = document.getElementById('hotkey-input');
    const keys = Array.from(capturedKeys);

    // Sort: modifiers first
    const order = ['ctrl', 'shift', 'alt', 'win'];
    keys.sort((a, b) => {
        const ai = order.indexOf(a);
        const bi = order.indexOf(b);
        if (ai !== -1 && bi !== -1) return ai - bi;
        if (ai !== -1) return -1;
        if (bi !== -1) return 1;
        return 0;
    });

    input.value = keys.join('+') || 'Press keys...';
}

function confirmHotkey() {
    if (!capturingHotkey) return;

    const hotkey = Array.from(capturedKeys).join('+');
    if (hotkey) {
        document.getElementById('hotkey-input').value = hotkey;
        updateConfig();
    }

    resetHotkeyCapture();
}

function cancelHotkeyCapture() {
    document.getElementById('hotkey-input').value = originalHotkey;
    resetHotkeyCapture();
}

function resetHotkeyCapture() {
    capturingHotkey = false;
    capturedKeys.clear();

    const input = document.getElementById('hotkey-input');
    const btn = document.getElementById('hotkey-btn');

    input.classList.remove('border-accent');
    btn.textContent = 'RECORD';
    btn.classList.remove('bg-red-500', 'hover:bg-red-600');
    btn.classList.add('bg-accent', 'hover:bg-accent-hover');
    btn.onclick = startHotkeyCapture;

    document.removeEventListener('keydown', captureKeyDown);
    document.removeEventListener('keyup', captureKeyUp);
}

// =============================================================================
// MODELS
// =============================================================================

function renderModelList() {
    const container = document.getElementById('model-list');
    if (!container) {
        console.error('[Settings] model-list container not found!');
        return;
    }

    const searchQuery = document.getElementById('model-search')?.value.toLowerCase() || '';

    // Combine models
    const allModels = [...new Set([...userModels, ...defaultModels])];
    console.log('[Settings] renderModelList - allModels:', allModels);

    // Filter
    const filtered = searchQuery
        ? allModels.filter(m => m.toLowerCase().includes(searchQuery))
        : allModels;

    // Limit display
    const display = filtered.slice(0, 50);
    console.log('[Settings] renderModelList - display:', display);

    container.innerHTML = display.map(model => {
        const isSelected = model === currentModel;
        const isCustom = userModels.includes(model) && !defaultModels.includes(model);
        const pricing = modelsPricing[model];
        const priceStr = pricing
            ? `$${pricing.input} / $${pricing.output}`
            : 'Loading...';

        return `
            <div class="flex items-center justify-between gap-2 p-3 rounded-lg ${isSelected ? 'bg-accent/20 border border-accent/50' : 'bg-bg-input border border-transparent hover:border-border-subtle'}">
                <div class="flex-1 min-w-0">
                    <div class="text-sm ${isSelected ? 'text-white' : 'text-gray-400'} truncate">${model}</div>
                    <div class="text-xs text-text-dim mt-0.5">Input / Output (per 1M tokens): ${priceStr}</div>
                </div>
                <div class="flex items-center gap-2 flex-shrink-0">
                    ${isCustom ? `<button onclick="deleteModel('${model}')" class="text-red-400 hover:text-red-300 text-xs px-2">Delete</button>` : ''}
                    <button onclick="selectModel('${model}')"
                        class="px-3 py-1 text-xs rounded whitespace-nowrap ${isSelected ? 'bg-accent text-black' : 'bg-white/10 text-white hover:bg-white/20'}">
                        ${isSelected ? 'Selected' : 'Select'}
                    </button>
                </div>
            </div>
        `;
    }).join('');

    if (display.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-center py-4">No models found</p>';
    }
}

function filterModels() {
    renderModelList();
}

function selectModel(model) {
    currentModel = model;
    renderModelList();
    updateConfig();
}

async function addModel() {
    const input = document.getElementById('new-model');
    const model = input.value.trim();

    if (!model) return;
    if (userModels.includes(model) || defaultModels.includes(model)) {
        alert('Model already exists');
        return;
    }

    userModels.push(model);
    currentModel = model;
    input.value = '';

    // Try to fetch pricing for the new model if not cached
    if (!modelsPricing[model]) {
        await fetchOpenrouterPricing();
    }

    renderModelList();
    updateConfig();
}

function deleteModel(model) {
    userModels = userModels.filter(m => m !== model);
    if (currentModel === model) {
        currentModel = defaultModels[0] || userModels[0] || '';
    }
    renderModelList();
    updateConfig();
}

function resetModels() {
    userModels = [];
    currentModel = defaultModels[0] || '';
    document.getElementById('model-search').value = '';
    renderModelList();
    updateConfig();
}

async function testConnection() {
    const btn = document.getElementById('test-btn');
    const result = document.getElementById('test-result');
    const apiKey = document.getElementById('api-key').value;

    if (!apiKey) {
        showTestResult(false, 'API key is required');
        return;
    }
    if (!currentModel) {
        showTestResult(false, 'Select a model first');
        return;
    }

    btn.textContent = 'Testing...';
    btn.disabled = true;

    try {
        const response = await pywebview.api.test_llm_connection(apiKey, currentModel);
        if (response.success) {
            showTestResult(true, `OK (${response.chars} chars): ${response.response}`);
            // Fetch pricing when API key is validated
            await fetchOpenrouterPricing(apiKey);
        } else {
            showTestResult(false, response.error);
        }
    } catch (e) {
        showTestResult(false, e.toString());
    }

    btn.textContent = 'Test';
    btn.disabled = false;
}

async function fetchOpenrouterPricing(apiKey = null) {
    if (pricingFetchInProgress) {
        console.log('[Settings] Pricing fetch already in progress, skipping');
        return;
    }
    pricingFetchInProgress = true;

    try {
        console.log('[Settings] Calling fetch_openrouter_pricing...');
        const response = await pywebview.api.fetch_openrouter_pricing(apiKey);
        console.log('[Settings] Fetch response:', response);

        if (response.success) {
            console.log('[Settings] Fetch successful, reloading pricing cache...');
            // Reload pricing cache
            modelsPricing = await pywebview.api.get_all_models_pricing();
            console.log('[Settings] Loaded pricing for', Object.keys(modelsPricing).length, 'models');
            renderModelList();
            console.log(`[Settings] Pricing updated: ${response.models_count} models`);
        } else {
            console.warn('[Settings] Failed to fetch pricing:', response.error);
        }
    } catch (e) {
        console.error('[Settings] Error fetching pricing:', e);
    } finally {
        pricingFetchInProgress = false;
    }
}

function showTestResult(success, message) {
    const result = document.getElementById('test-result');
    result.classList.remove('hidden');
    result.querySelector('div').className = `p-3 rounded-lg text-sm ${success ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`;
    result.querySelector('div').textContent = message;

    // Auto-hide after 5s
    setTimeout(() => {
        result.classList.add('hidden');
    }, 5000);
}

// =============================================================================
// HISTORY
// =============================================================================

async function loadHistory() {
    const container = document.getElementById('history-list');

    try {
        const history = await pywebview.api.get_history(20);

        if (history.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-8">No transcriptions yet</p>';
            return;
        }

        container.innerHTML = history.map(entry => {
            const date = entry.timestamp ? formatDate(entry.timestamp) : 'Unknown date';
            const duration = entry.duration ? formatDuration(entry.duration) : '';

            return `
                <div class="bg-bg-elevated rounded-xl border border-border-subtle p-4">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-gray-500 text-sm">${date}</span>
                        <div class="flex gap-2">
                            ${entry.audio_path ? `<button onclick="playAudio('${entry.audio_path.replace(/\\/g, '\\\\')}')" class="text-xs px-2 py-1 bg-white/10 rounded hover:bg-white/20">Play ${duration}</button>` : ''}
                            <button onclick="copyText('${escapeJS(entry.text)}')" class="text-xs px-2 py-1 bg-white/10 rounded hover:bg-white/20">Copy</button>
                        </div>
                    </div>
                    <p class="text-gray-300 text-sm">${escapeHTML(entry.text) || '<em class="text-gray-500">Empty transcription</em>'}</p>
                </div>
            `;
        }).join('');
    } catch (e) {
        console.error('[Settings] Failed to load history:', e);
        container.innerHTML = '<p class="text-red-400 text-center py-8">Failed to load history</p>';
    }
}

async function refreshHistory() {
    await loadHistory();
}

function formatDate(timestamp) {
    try {
        const date = new Date(timestamp);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: 'numeric',
            minute: '2-digit'
        });
    } catch {
        return timestamp;
    }
}

function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

async function playAudio(path) {
    try {
        await pywebview.api.play_audio(path);
    } catch (e) {
        console.error('[Settings] Failed to play audio:', e);
    }
}

async function copyText(text) {
    try {
        await pywebview.api.copy_to_clipboard(text);
    } catch (e) {
        // Fallback to browser API
        navigator.clipboard.writeText(text);
    }
}

// =============================================================================
// FOLDERS
// =============================================================================

async function openFolder(type) {
    try {
        await pywebview.api.open_folder(type);
    } catch (e) {
        console.error('[Settings] Failed to open folder:', e);
    }
}

// =============================================================================
// UTILITIES
// =============================================================================

function escapeHTML(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function escapeJS(str) {
    if (!str) return '';
    return str
        .replace(/\\/g, '\\\\')
        .replace(/'/g, "\\'")
        .replace(/"/g, '\\"')
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '\\r');
}
