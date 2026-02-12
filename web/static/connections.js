// Substrate Database Admin - Connections Management

let currentSRL = null;

// Test connection
async function testConnection(srlName) {
    try {
        const response = await fetch(`/api/test-connection/${srlName}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`✅ Connection test successful!\nStatus: ${data.status}`);
            refreshConnections();
        } else {
            alert(`❌ Connection test failed!\nError: ${data.error}`);
        }
    } catch (error) {
        alert(`❌ Error: ${error.message}`);
    }
}

// Toggle enable/disable
async function toggleEnable(srlName) {
    try {
        const response = await fetch(`/api/toggle-enable/${srlName}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            refreshConnections();
        } else {
            alert(`❌ Error: ${data.error}`);
        }
    } catch (error) {
        alert(`❌ Error: ${error.message}`);
    }
}

// Delete connection
async function deleteConnection(srlName) {
    if (!confirm(`Are you sure you want to delete connection '${srlName}'?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/delete-connection/${srlName}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`✅ Connection '${srlName}' deleted`);
            refreshConnections();
        } else {
            alert(`❌ Error: ${data.error}`);
        }
    } catch (error) {
        alert(`❌ Error: ${error.message}`);
    }
}

// Edit connection
function editConnection(srlName) {
    alert(`Edit functionality for '${srlName}' would be implemented here.\n\nThis would allow editing non-encrypted fields like:\n- Name\n- Endpoint\n- Protocol\n- Lazy load settings`);
}

// Show password dialog
function showPasswordDialog(srlName) {
    currentSRL = srlName;
    document.getElementById('passwordDialogSRL').textContent = srlName;
    document.getElementById('newPassword').value = '';
    document.getElementById('passwordDialog').classList.add('show');
}

// Close password dialog
function closePasswordDialog() {
    document.getElementById('passwordDialog').classList.remove('show');
    currentSRL = null;
}

// Change password
async function changePassword() {
    const newPassword = document.getElementById('newPassword').value;
    
    if (!newPassword) {
        alert('Please enter a new password');
        return;
    }
    
    try {
        const response = await fetch(`/api/change-password/${currentSRL}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                new_password: newPassword
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`✅ Password updated for '${currentSRL}'`);
            closePasswordDialog();
        } else {
            alert(`❌ Error: ${data.error}`);
        }
    } catch (error) {
        alert(`❌ Error: ${error.message}`);
    }
}

// Show add connection dialog
function showAddConnectionDialog() {
    alert(`Add Connection functionality would be implemented here.\n\nThis would allow adding new SRLs:\n- Database connections\n- API endpoints\n- File sources\n- Stream sources\n\nWith encrypted credentials and bitcount verification.`);
}

// Refresh connections
function refreshConnections() {
    location.reload();
}

// Close modal on outside click
window.onclick = function(event) {
    const modal = document.getElementById('passwordDialog');
    if (event.target === modal) {
        closePasswordDialog();
    }
}

// Close modal on Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closePasswordDialog();
    }
});

