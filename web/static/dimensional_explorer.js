/**
 * Dimensional Explorer - Main JavaScript
 * Windows Explorer-like interface for dimensional substrates
 */

// Quick Connect Configurations - Popular Services
const QUICK_CONNECT_SERVICES = [
    // Social Media
    { id: 'twitter', name: 'Twitter', icon: '🐦', category: 'social', needsAuth: true },
    { id: 'facebook', name: 'Facebook', icon: '📘', category: 'social', needsAuth: true },
    { id: 'instagram', name: 'Instagram', icon: '📷', category: 'social', needsAuth: true },
    { id: 'linkedin', name: 'LinkedIn', icon: '💼', category: 'social', needsAuth: true },
    { id: 'reddit', name: 'Reddit', icon: '🤖', category: 'social', needsAuth: false },
    { id: 'youtube', name: 'YouTube', icon: '📺', category: 'social', needsAuth: true },
    
    // Shopping
    { id: 'amazon', name: 'Amazon', icon: '📦', category: 'shopping', needsAuth: true },
    { id: 'ebay', name: 'eBay', icon: '🛒', category: 'shopping', needsAuth: true },
    { id: 'shopify', name: 'Shopify', icon: '🏪', category: 'shopping', needsAuth: true },
    
    // Knowledge
    { id: 'wikipedia', name: 'Wikipedia', icon: '📚', category: 'knowledge', needsAuth: false },
    { id: 'google', name: 'Google', icon: '🔍', category: 'knowledge', needsAuth: true },
    { id: 'dictionary', name: 'Dictionary', icon: '📖', category: 'knowledge', needsAuth: false },
    
    // Music & Audio
    { id: 'spotify', name: 'Spotify', icon: '🎵', category: 'music', needsAuth: true },
    { id: 'soundcloud', name: 'SoundCloud', icon: '🎧', category: 'music', needsAuth: true },
    { id: 'pandora', name: 'Pandora', icon: '🎶', category: 'music', needsAuth: true },
    { id: 'apple_music', name: 'Apple Music', icon: '🍎', category: 'music', needsAuth: true },
    
    // Cloud Storage
    { id: 'dropbox', name: 'Dropbox', icon: '📦', category: 'storage', needsAuth: true },
    { id: 'google_drive', name: 'Google Drive', icon: '💾', category: 'storage', needsAuth: true },
    { id: 'onedrive', name: 'OneDrive', icon: '☁️', category: 'storage', needsAuth: true },
    { id: 'box', name: 'Box', icon: '📁', category: 'storage', needsAuth: true },
    
    // AI Services
    { id: 'openai', name: 'OpenAI', icon: '🤖', category: 'ai', needsAuth: true },
    { id: 'anthropic', name: 'Anthropic', icon: '🧠', category: 'ai', needsAuth: true },
    { id: 'huggingface', name: 'HuggingFace', icon: '🤗', category: 'ai', needsAuth: true },
    
    // Developer
    { id: 'github', name: 'GitHub', icon: '🐙', category: 'developer', needsAuth: true },
    { id: 'gitlab', name: 'GitLab', icon: '🦊', category: 'developer', needsAuth: true },
    { id: 'bitbucket', name: 'Bitbucket', icon: '🪣', category: 'developer', needsAuth: true },
    
    // Cloud Platforms
    { id: 'aws', name: 'AWS', icon: '☁️', category: 'cloud', needsAuth: true },
    { id: 'azure', name: 'Azure', icon: '🔷', category: 'cloud', needsAuth: true },
    { id: 'gcp', name: 'Google Cloud', icon: '☁️', category: 'cloud', needsAuth: true },
    
    // Databases
    { id: 'mysql', name: 'MySQL', icon: '🐬', category: 'database', needsAuth: true },
    { id: 'postgresql', name: 'PostgreSQL', icon: '🐘', category: 'database', needsAuth: true },
    { id: 'mongodb', name: 'MongoDB', icon: '🍃', category: 'database', needsAuth: true },
    { id: 'redis', name: 'Redis', icon: '🔴', category: 'database', needsAuth: true },
    { id: 'sqlite', name: 'SQLite', icon: '💾', category: 'database', needsAuth: false },
    
    // Weather
    { id: 'weatherapi', name: 'Weather', icon: '🌤️', category: 'data', needsAuth: true },
    { id: 'openmeteo', name: 'Open-Meteo', icon: '🌦️', category: 'data', needsAuth: false },
    
    // Crypto
    { id: 'coingecko', name: 'CoinGecko', icon: '💰', category: 'crypto', needsAuth: false },
    { id: 'binance', name: 'Binance', icon: '🪙', category: 'crypto', needsAuth: true },
    
    // Space
    { id: 'spacex', name: 'SpaceX', icon: '🚀', category: 'space', needsAuth: false },
    { id: 'nasa', name: 'NASA', icon: '🛸', category: 'space', needsAuth: false },
    
    // General/Custom
    { id: 'custom', name: 'Custom API', icon: '⚙️', category: 'general', needsAuth: true },
];

// Initialize the explorer
document.addEventListener('DOMContentLoaded', function() {
    initializeQuickConnect();
    initializeViewTabs();
    initializeTreeView();
    initializeSearchBar();
    initializeNavigation();
    loadInitialData();
});

// Initialize Quick Connect Buttons
function initializeQuickConnect() {
    const container = document.getElementById('quick-connect-buttons');
    
    QUICK_CONNECT_SERVICES.forEach(service => {
        const btn = document.createElement('button');
        btn.className = 'quick-connect-btn';
        btn.dataset.serviceId = service.id;
        btn.dataset.needsAuth = service.needsAuth;
        
        btn.innerHTML = `
            <div class="quick-connect-icon">${service.icon}</div>
            <div class="quick-connect-name">${service.name}</div>
        `;
        
        btn.addEventListener('click', () => handleQuickConnect(service));
        container.appendChild(btn);
    });
}

// Handle Quick Connect
function handleQuickConnect(service) {
    console.log('Quick connect:', service.name);
    
    if (service.needsAuth) {
        // Open connection wizard with pre-filled service info
        openConnectionWizard(service);
    } else {
        // Connect immediately (no auth needed)
        connectToService(service);
    }
}

// Open Connection Wizard
function openConnectionWizard(service = null) {
    // Redirect to connection wizard page
    const url = service 
        ? `/connection-wizard?service=${service.id}`
        : '/connection-wizard';
    window.location.href = url;
}

// Connect to Service (no auth)
async function connectToService(service) {
    updateStatus(`Connecting to ${service.name}...`);
    
    try {
        const response = await fetch('/api/quick-connect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ service_id: service.id })
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateStatus(`Connected to ${service.name}`);
            refreshConnectionsTree();
        } else {
            updateStatus(`Failed to connect: ${result.error}`);
        }
    } catch (error) {
        updateStatus(`Error: ${error.message}`);
    }
}

// Initialize View Tabs
function initializeViewTabs() {
    const tabs = document.querySelectorAll('.view-tab');
    const views = document.querySelectorAll('.view-container');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const viewType = tab.dataset.view;
            
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Update active view
            views.forEach(v => v.classList.remove('active'));
            document.getElementById(`${viewType}-view`).classList.add('active');
            
            // Load view-specific data
            loadViewData(viewType);
        });
    });
}

// Initialize Tree View
function initializeTreeView() {
    const treeItems = document.querySelectorAll('.tree-item');

    treeItems.forEach(item => {
        item.addEventListener('click', () => {
            // Update active item
            treeItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            // Load content for selected item
            const subject = item.dataset.subject;
            const path = item.dataset.path;

            if (subject) {
                loadSubjectData(subject);
            } else if (path) {
                loadPathData(path);
            }
        });
    });
}

// Initialize Search Bar
function initializeSearchBar() {
    const searchInput = document.getElementById('search-input');
    const searchMode = document.getElementById('search-mode');
    const executeBtn = document.getElementById('execute-btn');

    executeBtn.addEventListener('click', () => {
        const query = searchInput.value;
        const mode = searchMode.value;

        if (mode === 'search') {
            performSearch(query);
        } else if (mode === 'query') {
            performQuery(query);
        } else if (mode === 'filter') {
            performFilter(query);
        }
    });

    // Enter key support
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            executeBtn.click();
        }
    });
}

// Initialize Navigation
function initializeNavigation() {
    document.getElementById('back-btn').addEventListener('click', () => navigateBack());
    document.getElementById('forward-btn').addEventListener('click', () => navigateForward());
    document.getElementById('up-btn').addEventListener('click', () => navigateUp());
    document.getElementById('refresh-btn').addEventListener('click', () => refreshCurrentView());
    document.getElementById('new-connection-btn').addEventListener('click', () => openConnectionWizard());
    document.getElementById('view-connections-btn').addEventListener('click', () => viewConnectionsTable());
}

// Load Initial Data
async function loadInitialData() {
    updateStatus('Loading substrates...');

    try {
        const response = await fetch('/api/substrates');
        const data = await response.json();

        if (data.success) {
            renderFolderView(data.substrates);
            updateStatus(`Loaded ${data.substrates.length} substrates`);
        }
    } catch (error) {
        updateStatus(`Error loading data: ${error.message}`);
    }
}

// Load View Data
function loadViewData(viewType) {
    if (viewType === 'folder') {
        loadInitialData();
    } else if (viewType === 'table') {
        loadTableView();
    } else if (viewType === 'dimension') {
        loadDimensionView();
    }
}

// Load Subject Data
async function loadSubjectData(subject) {
    updateStatus(`Loading ${subject} substrates...`);

    try {
        const response = await fetch(`/api/substrates/${subject}`);
        const data = await response.json();

        if (data.success) {
            renderFolderView(data.substrates);
            updateStatus(`${data.substrates.length} ${subject} substrates`);
        }
    } catch (error) {
        updateStatus(`Error: ${error.message}`);
    }
}

// Load Path Data
function loadPathData(path) {
    updateStatus(`Loading ${path}...`);
    // Implementation for loading path-specific data
}

// Render Folder View
function renderFolderView(substrates) {
    const grid = document.getElementById('folder-grid');
    grid.innerHTML = '';

    substrates.forEach(substrate => {
        const item = document.createElement('div');
        item.className = 'folder-item';
        item.dataset.identity = substrate.identity;

        const icon = getSubjectIcon(substrate.subject);

        item.innerHTML = `
            <div class="folder-icon">${icon}</div>
            <div class="folder-name">${substrate.name || 'Substrate'}</div>
        `;

        item.addEventListener('click', () => openSubstrate(substrate));
        grid.appendChild(item);
    });

    updateItemCount(substrates.length);
}

// Load Table View
async function loadTableView() {
    updateStatus('Loading table view...');

    try {
        const response = await fetch('/api/substrates');
        const data = await response.json();

        if (data.success) {
            renderTableView(data.substrates);
        }
    } catch (error) {
        updateStatus(`Error: ${error.message}`);
    }
}

// Render Table View
function renderTableView(substrates) {
    const tbody = document.getElementById('table-body');
    tbody.innerHTML = '';

    substrates.forEach(substrate => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>0x${substrate.identity.toString(16).toUpperCase()}</td>
            <td>${substrate.name || 'Unnamed'}</td>
            <td>${substrate.subject}</td>
            <td>${substrate.source || 'Local'}</td>
            <td>${new Date(substrate.created).toLocaleString()}</td>
            <td>${substrate.tags ? substrate.tags.join(', ') : ''}</td>
            <td>
                <button onclick="viewSubstrate('${substrate.identity}')">View</button>
                <button onclick="deleteSubstrate('${substrate.identity}')">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Load Dimension View
function loadDimensionView() {
    updateStatus('Loading dimensional visualization...');
    const canvas = document.getElementById('dimension-canvas');
    const ctx = canvas.getContext('2d');

    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    // Draw placeholder
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#ffffff';
    ctx.font = '20px Segoe UI';
    ctx.textAlign = 'center';
    ctx.fillText('3D Dimensional Visualization', canvas.width / 2, canvas.height / 2);
    ctx.font = '14px Segoe UI';
    ctx.fillStyle = '#888';
    ctx.fillText('(Coming soon - WebGL rendering)', canvas.width / 2, canvas.height / 2 + 30);
}

// Helper Functions
function getSubjectIcon(subject) {
    const icons = {
        'WEATHER': '🌤️',
        'IMAGE': '🖼️',
        'VIDEO': '🎬',
        'AUDIO': '🎵',
        'TEXT': '📄',
        'NUMBER': '🔢',
        'RECORD': '📊',
        'PATTERN': '🔷',
        'CUSTOM': '⚙️'
    };
    return icons[subject] || '📦';
}

function updateStatus(message) {
    document.getElementById('status-text').textContent = message;
}

function updateItemCount(count) {
    document.getElementById('item-count').textContent = `${count} items`;
}

function performSearch(query) {
    updateStatus(`Searching for: ${query}`);
    // Implementation
}

function performQuery(query) {
    updateStatus(`Executing query: ${query}`);
    // Implementation
}

function performFilter(query) {
    updateStatus(`Filtering by: ${query}`);
    // Implementation
}

function navigateBack() {
    updateStatus('Navigate back');
}

function navigateForward() {
    updateStatus('Navigate forward');
}

function navigateUp() {
    updateStatus('Navigate up');
}

function refreshCurrentView() {
    updateStatus('Refreshing...');
    loadInitialData();
}

function viewConnectionsTable() {
    window.location.href = '/connections';
}

function refreshConnectionsTree() {
    // Refresh connections in tree view
    updateStatus('Connections refreshed');
}

function openSubstrate(substrate) {
    console.log('Opening substrate:', substrate);
}

function viewSubstrate(identity) {
    console.log('Viewing substrate:', identity);
}

function deleteSubstrate(identity) {
    if (confirm('Delete this substrate?')) {
        console.log('Deleting substrate:', identity);
    }
}

