// Connection Wizard JavaScript

let currentStep = 1;
let selectedConnectionType = null;
let connectionConfig = {};

// Select connection type
function selectConnectionType(type) {
    selectedConnectionType = type;
    
    // Remove selected class from all cards
    document.querySelectorAll('.connection-type-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Add selected class to clicked card
    event.target.closest('.connection-type-card').classList.add('selected');
}

// Next step
function nextStep() {
    if (currentStep === 1) {
        if (!selectedConnectionType) {
            alert('Please select a connection type');
            return;
        }
        
        // Show appropriate config form
        showConfigForm(selectedConnectionType);
    } else if (currentStep === 2) {
        // Validate and collect configuration
        if (!validateConfiguration()) {
            return;
        }
        
        collectConfiguration();
        displaySummary();
    }
    
    // Move to next step
    currentStep++;
    updateStepDisplay();
}

// Previous step
function previousStep() {
    currentStep--;
    updateStepDisplay();
}

// Update step display
function updateStepDisplay() {
    // Update step indicators
    document.querySelectorAll('.wizard-step').forEach((step, index) => {
        const stepNum = index + 1;
        step.classList.remove('active', 'completed');
        
        if (stepNum < currentStep) {
            step.classList.add('completed');
        } else if (stepNum === currentStep) {
            step.classList.add('active');
        }
    });
    
    // Update step content
    document.querySelectorAll('.step-content').forEach((content, index) => {
        const stepNum = index + 1;
        content.classList.remove('active');
        
        if (stepNum === currentStep) {
            content.classList.add('active');
        }
    });
    
    // Update buttons
    const btnPrevious = document.getElementById('btn-previous');
    const btnNext = document.getElementById('btn-next');
    const btnSave = document.getElementById('btn-save');
    
    btnPrevious.style.display = currentStep > 1 ? 'block' : 'none';
    btnNext.style.display = currentStep < 3 ? 'block' : 'none';
    btnSave.style.display = currentStep === 3 ? 'block' : 'none';
}

// Show config form based on type
function showConfigForm(type) {
    // Hide all config forms
    document.querySelectorAll('.config-form').forEach(form => {
        form.style.display = 'none';
    });
    
    // Show selected config form
    const formId = `config-${type.toLowerCase()}`;
    const form = document.getElementById(formId);
    if (form) {
        form.style.display = 'block';
    }
}

// Validate configuration
function validateConfiguration() {
    const type = selectedConnectionType.toLowerCase();
    
    if (type === 'database') {
        const name = document.getElementById('db-name').value;
        const host = document.getElementById('db-host').value;
        const port = document.getElementById('db-port').value;
        const database = document.getElementById('db-database').value;
        const username = document.getElementById('db-username').value;
        const password = document.getElementById('db-password').value;
        
        if (!name || !host || !port || !database || !username || !password) {
            alert('Please fill in all required fields');
            return false;
        }
    } else if (type === 'api') {
        const name = document.getElementById('api-name').value;
        const url = document.getElementById('api-url').value;
        const apiKey = document.getElementById('api-key').value;
        
        if (!name || !url || !apiKey) {
            alert('Please fill in all required fields');
            return false;
        }
    } else if (type === 'file') {
        const name = document.getElementById('file-name').value;
        const filepath = document.getElementById('file-path').value;
        
        if (!name || !filepath) {
            alert('Please fill in all required fields');
            return false;
        }
    } else if (type === 'stream') {
        const name = document.getElementById('stream-name').value;
        const url = document.getElementById('stream-url').value;
        
        if (!name || !url) {
            alert('Please fill in all required fields');
            return false;
        }
    }
    
    return true;
}

// Collect configuration
function collectConfiguration() {
    const type = selectedConnectionType.toLowerCase();
    
    connectionConfig = {
        type: selectedConnectionType
    };
    
    if (type === 'database') {
        connectionConfig.name = document.getElementById('db-name').value;
        connectionConfig.host = document.getElementById('db-host').value;
        connectionConfig.port = document.getElementById('db-port').value;
        connectionConfig.database = document.getElementById('db-database').value;
        connectionConfig.protocol = document.getElementById('db-protocol').value;
        connectionConfig.username = document.getElementById('db-username').value;
        connectionConfig.password = document.getElementById('db-password').value;
    } else if (type === 'api') {
        connectionConfig.name = document.getElementById('api-name').value;
        connectionConfig.url = document.getElementById('api-url').value;
        connectionConfig.api_key = document.getElementById('api-key').value;
        connectionConfig.method = document.getElementById('api-method').value;
    } else if (type === 'file') {
        connectionConfig.name = document.getElementById('file-name').value;
        connectionConfig.filepath = document.getElementById('file-path').value;
    } else if (type === 'stream') {
        connectionConfig.name = document.getElementById('stream-name').value;
        connectionConfig.url = document.getElementById('stream-url').value;
        connectionConfig.protocol = document.getElementById('stream-protocol').value;
    }
}

// Display summary
function displaySummary() {
    const summaryContent = document.getElementById('summary-content');
    const type = selectedConnectionType.toLowerCase();

    let html = `<p><strong>Type:</strong> ${selectedConnectionType}</p>`;
    html += `<p><strong>Name:</strong> ${connectionConfig.name}</p>`;

    if (type === 'database') {
        html += `<p><strong>Host:</strong> ${connectionConfig.host}:${connectionConfig.port}</p>`;
        html += `<p><strong>Database:</strong> ${connectionConfig.database}</p>`;
        html += `<p><strong>Protocol:</strong> ${connectionConfig.protocol}</p>`;
        html += `<p><strong>Username:</strong> ${connectionConfig.username}</p>`;
        html += `<p><strong>Password:</strong> ********** (encrypted)</p>`;
    } else if (type === 'api') {
        html += `<p><strong>URL:</strong> ${connectionConfig.url}</p>`;
        html += `<p><strong>Method:</strong> ${connectionConfig.method}</p>`;
        html += `<p><strong>API Key:</strong> ********** (encrypted)</p>`;
    } else if (type === 'file') {
        html += `<p><strong>File Path:</strong> ${connectionConfig.filepath}</p>`;
    } else if (type === 'stream') {
        html += `<p><strong>URL:</strong> ${connectionConfig.url}</p>`;
        html += `<p><strong>Protocol:</strong> ${connectionConfig.protocol}</p>`;
    }

    summaryContent.innerHTML = html;
}

// Test connection
async function testConnection() {
    const testResult = document.getElementById('test-result');
    testResult.className = 'test-result';
    testResult.innerHTML = '🔄 Testing connection...';
    testResult.style.display = 'block';

    try {
        const response = await fetch('/api/test-new-connection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: selectedConnectionType,
                config: connectionConfig
            })
        });

        const data = await response.json();

        if (data.success) {
            testResult.className = 'test-result success';
            testResult.innerHTML = `✅ <strong>Connection Successful!</strong><br>${data.message || 'Connection test passed'}`;
        } else {
            testResult.className = 'test-result error';
            testResult.innerHTML = `❌ <strong>Connection Failed!</strong><br>${data.error || 'Unknown error'}`;
        }
    } catch (error) {
        testResult.className = 'test-result error';
        testResult.innerHTML = `❌ <strong>Error:</strong> ${error.message}`;
    }
}

// Save connection
async function saveConnection() {
    if (!confirm(`Save connection '${connectionConfig.name}'?`)) {
        return;
    }

    try {
        const response = await fetch('/api/create-connection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: selectedConnectionType,
                config: connectionConfig
            })
        });

        const data = await response.json();

        if (data.success) {
            alert(`✅ Connection '${connectionConfig.name}' created successfully!`);
            window.location.href = '/connections';
        } else {
            alert(`❌ Error: ${data.error}`);
        }
    } catch (error) {
        alert(`❌ Error: ${error.message}`);
    }
}

// Cancel wizard
function cancelWizard() {
    if (confirm('Cancel connection wizard? All entered data will be lost.')) {
        window.location.href = '/connections';
    }
}

