/**
 * DimensionOS Dashboard JavaScript
 * Handles query processing, object display, and UI interactions
 */

const { apiCall, showNotification } = window.DimensionOS;

// State
let currentObjects = [];
let selectedObject = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    initializeQueryBox();
    initializeViewTabs();
    initializeConnectors();
    loadUserObjects();
});

// Query Box
function initializeQueryBox() {
    const queryInput = document.getElementById('query-input');
    const querySubmit = document.getElementById('query-submit');
    
    querySubmit.addEventListener('click', () => submitQuery());
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            submitQuery();
        }
    });
}

async function submitQuery() {
    const queryInput = document.getElementById('query-input');
    const query = queryInput.value.trim();
    
    if (!query) return;
    
    // Show loading state
    const responseArea = document.getElementById('response-area');
    responseArea.classList.add('active');
    responseArea.innerHTML = '<p>Processing query...</p>';
    
    // Submit query
    const result = await apiCall('/api/query', 'POST', { query });
    
    // Display result
    if (result.success) {
        displayQueryResult(result);
        
        // Reload objects if it was a load command
        if (query.toLowerCase().startsWith('load ')) {
            await loadUserObjects();
        }
    } else {
        responseArea.innerHTML = `<p style="color: #ef4444;">${result.message || 'Query failed'}</p>`;
    }
    
    // Clear input
    queryInput.value = '';
}

function displayQueryResult(result) {
    const responseArea = document.getElementById('response-area');
    
    let html = '<div style="padding: 1rem;">';
    html += `<p><strong>Result:</strong> ${result.message}</p>`;
    
    if (result.truth) {
        html += `<p><strong>Truth:</strong> <code>${result.truth}</code></p>`;
    }
    
    if (result.value) {
        html += `<p><strong>Value:</strong> ${result.value}</p>`;
    }
    
    if (result.object) {
        html += `<p><strong>Object:</strong> ${result.object}</p>`;
    }
    
    html += '</div>';
    responseArea.innerHTML = html;
}

// View Tabs
function initializeViewTabs() {
    const tabs = document.querySelectorAll('.view-tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const viewName = tab.dataset.view;
            switchView(viewName);
        });
    });
}

function switchView(viewName) {
    // Update tabs
    document.querySelectorAll('.view-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.view === viewName);
    });
    
    // Update views
    document.querySelectorAll('.view-content').forEach(view => {
        view.classList.remove('active');
    });
    document.getElementById(`view-${viewName}`).classList.add('active');
}

// Load User Objects
async function loadUserObjects() {
    const result = await apiCall('/api/objects', 'GET');
    
    if (result && Array.isArray(result)) {
        currentObjects = result;
        updateObjectDisplays();
    }
}

function updateObjectDisplays() {
    updateIconView();
    updateTableView();
    updateTreeView();
}

function updateIconView() {
    const iconGrid = document.getElementById('icon-grid');
    
    if (currentObjects.length === 0) {
        iconGrid.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">◈</div>
                <h3>No Objects Loaded</h3>
                <p>Use the query box above to ingest objects</p>
            </div>
        `;
        return;
    }
    
    iconGrid.innerHTML = currentObjects.map(obj => `
        <div class="object-card" data-name="${obj.name}">
            <div class="object-icon">◈</div>
            <div class="object-name">${obj.name}</div>
            <div class="object-type">${obj.type}</div>
        </div>
    `).join('');
    
    // Add click handlers
    document.querySelectorAll('.object-card').forEach(card => {
        card.addEventListener('click', () => {
            const name = card.dataset.name;
            selectObject(name);
        });
    });
}

function updateTableView() {
    const tableBody = document.getElementById('table-body');
    
    if (currentObjects.length === 0) {
        tableBody.innerHTML = '<tr class="empty-row"><td colspan="5">No objects loaded</td></tr>';
        return;
    }
    
    tableBody.innerHTML = currentObjects.map(obj => `
        <tr>
            <td>${obj.name}</td>
            <td>${obj.type}</td>
            <td><code>${obj.truth ? '0x' + obj.truth.toString(16) : 'N/A'}</code></td>
            <td>0D-4D</td>
            <td><button class="btn-small" onclick="selectObject('${obj.name}')">View</button></td>
        </tr>
    `).join('');
}

function updateTreeView() {
    const treeContainer = document.getElementById('tree-container');
    
    if (currentObjects.length === 0) {
        treeContainer.innerHTML = `
            <div class="tree-empty">
                <p>No objects yet</p>
                <p class="hint">Try: "Load bitcoin" or "Load 2026 Toyota Corolla"</p>
            </div>
        `;
        return;
    }
    
    treeContainer.innerHTML = currentObjects.map(obj => `
        <div class="tree-item" data-name="${obj.name}">
            <span class="tree-glyph">◈</span>
            <span class="tree-label">${obj.name}</span>
        </div>
    `).join('');
}

function selectObject(name) {
    selectedObject = currentObjects.find(obj => obj.name === name);
    if (selectedObject) {
        displayObjectAttributes(selectedObject);
        showNotification(`Selected: ${name}`, 'info');
    }
}

function displayObjectAttributes(obj) {
    const container = document.getElementById('attributes-container');
    
    container.innerHTML = `
        <div class="attribute-section">
            <h4>Identity</h4>
            <p><strong>Name:</strong> ${obj.name}</p>
            <p><strong>Type:</strong> ${obj.type}</p>
            <p><strong>Truth:</strong> <code>${obj.truth ? '0x' + obj.truth.toString(16) : 'N/A'}</code></p>
        </div>
    `;
}

// Connectors
function initializeConnectors() {
    const connectorBtns = document.querySelectorAll('.connector-btn');
    
    connectorBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const connector = btn.dataset.connector;
            showNotification(`${connector} connector - Coming soon!`, 'info');
        });
    });
}

