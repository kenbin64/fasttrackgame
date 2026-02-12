// Substrate Database Admin - User Management

let currentTargetUser = null;

// Show create user dialog
function showCreateUserDialog() {
    document.getElementById('newUsername').value = '';
    document.getElementById('newUserPassword').value = '';
    document.getElementById('newUserRole').value = 'ADMIN';
    document.getElementById('createUserDialog').classList.add('show');
}

// Close create user dialog
function closeCreateUserDialog() {
    document.getElementById('createUserDialog').classList.remove('show');
}

// Create user
async function createUser() {
    const username = document.getElementById('newUsername').value;
    const password = document.getElementById('newUserPassword').value;
    const role = document.getElementById('newUserRole').value;
    
    if (!username || !password) {
        alert('Please enter username and password');
        return;
    }
    
    try {
        const response = await fetch('/api/create-user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password,
                role: role
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`✅ User '${data.username}' created successfully`);
            closeCreateUserDialog();
            refreshUsers();
        } else {
            alert(`❌ Error: ${data.error}`);
        }
    } catch (error) {
        alert(`❌ Error: ${error.message}`);
    }
}

// Delete user
async function deleteUser(username) {
    if (!confirm(`Are you sure you want to delete user '${username}'?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/delete-user/${username}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`✅ User '${username}' deleted`);
            refreshUsers();
        } else {
            alert(`❌ Error: ${data.error}`);
        }
    } catch (error) {
        alert(`❌ Error: ${error.message}`);
    }
}

// Show emergency removal dialog
function showEmergencyRemovalDialog(username) {
    currentTargetUser = username;
    document.getElementById('emergencyTargetUser').textContent = username;
    document.getElementById('emergencyReason').value = '';
    document.getElementById('emergencyRemovalDialog').classList.add('show');
}

// Close emergency removal dialog
function closeEmergencyRemovalDialog() {
    document.getElementById('emergencyRemovalDialog').classList.remove('show');
    currentTargetUser = null;
}

// Request emergency removal
async function requestEmergencyRemoval() {
    const reason = document.getElementById('emergencyReason').value;
    
    if (!reason) {
        alert('Please provide a reason for emergency removal');
        return;
    }
    
    if (!confirm(`⚠️ WARNING: This will request emergency removal of superadmin '${currentTargetUser}'.\n\nThis requires 2 admin signatures to execute.\n\nContinue?`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/emergency-removal', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                target_superadmin: currentTargetUser,
                reason: reason
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (data.approved) {
                alert(`✅ Emergency removal request approved!\nSignatures: ${data.signatures}/2\n\nRequest will be executed when 2nd signature is added.`);
            } else {
                alert(`✅ Emergency removal request created.\nSignatures: ${data.signatures}/2\n\nWaiting for additional admin signatures.`);
            }
            closeEmergencyRemovalDialog();
            refreshUsers();
        } else {
            alert(`❌ Error: ${data.error}`);
        }
    } catch (error) {
        alert(`❌ Error: ${error.message}`);
    }
}

// Refresh users
function refreshUsers() {
    location.reload();
}

// Close modals on outside click
window.onclick = function(event) {
    const createDialog = document.getElementById('createUserDialog');
    const emergencyDialog = document.getElementById('emergencyRemovalDialog');
    
    if (event.target === createDialog) {
        closeCreateUserDialog();
    }
    if (event.target === emergencyDialog) {
        closeEmergencyRemovalDialog();
    }
}

// Close modals on Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeCreateUserDialog();
        closeEmergencyRemovalDialog();
    }
});

