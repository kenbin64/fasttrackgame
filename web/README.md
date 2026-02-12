# Substrate Database Admin Interface

## Overview

A phpMyAdmin-style web interface for managing the Substrate-Centric Database with SRLs (Substrate Resource Locators).

## Features

### 🔐 User Management
- **SUPERADMIN**: Database initializer, cannot be deleted (except emergency)
- **ADMIN**: Full access to admin interface, can manage users
- **USER**: Read-only access, NO admin interface access

### 🔗 Connection Management
- View all SRL connections in table format
- Status indicators:
  - ✅ Enabled / ❌ Disabled
  - 🟢 Connected / 🔴 Disconnected / 🟠 Connecting / ⚫ Blacklisted
- Actions per connection:
  - 🔍 Test Connection
  - ⏸️/▶️ Enable/Disable
  - ✏️ Edit (non-encrypted fields only)
  - 🔑 Change Password (for supported sources)
  - 🗑️ Delete

### 🛡️ Security Features
- Encrypted credentials (NOT shown in HTML)
- Bitcount anti-tampering verification
- Blacklist protection for critical OS/system files
- Session-based authentication
- Role-based access control

### 📊 Connection Table Columns
- **ID**: Substrate ID (first 8 characters)
- **Name**: Connection name
- **Type**: DATABASE, API, FILE, STREAM
- **Status**: Enabled/Disabled indicator
- **Connection**: Connection status indicator
- **Endpoint**: Connection endpoint (NO passwords!)
- **Protocol**: Connection protocol
- **Last Test**: Last connection test timestamp
- **Actions**: Action buttons

## Installation

### Prerequisites
```bash
pip install flask
```

### File Structure
```
web/
├── admin_interface.py          # Flask application
├── templates/
│   ├── login.html             # Login page
│   ├── connections.html       # Connection table
│   └── users.html             # User management
├── static/
│   ├── style.css              # Styles
│   ├── connections.js         # Connection management JS
│   └── users.js               # User management JS
└── README.md                  # This file

kernel/
├── substrate_centric_database.py      # Database core
├── substrate_resource_locator.py      # SRL system
├── database_user_management.py        # User management
└── connection_status_manager.py       # Status tracking
```

## Usage

### 1. Start the Server
```bash
cd web
python admin_interface.py
```

### 2. Access the Interface
```
URL: http://localhost:5000
```

### 3. Login
```
Default Superadmin:
  Username: admin
  Password: admin123
```

**⚠️ IMPORTANT: Change the default password in production!**

### 4. Manage Connections
- Navigate to "Connections" page
- View all registered SRLs
- Test connections
- Enable/disable connections
- Change passwords (for supported sources)
- Delete connections

### 5. Manage Users
- Navigate to "Users" page
- Create new users (ADMIN or USER)
- Delete users (except SUPERADMIN)
- Request emergency removal of SUPERADMIN (requires 3+ admins, 2 signatures)

## Security Rules

### User Roles
1. **SUPERADMIN**
   - Created during database initialization
   - Cannot be deleted by admins
   - Can reassign superadmin rights
   - Exception: Emergency removal with 3+ admins and 2 signatures

2. **ADMIN**
   - Full access to admin interface
   - Can create/delete users
   - Can manage connections
   - Cannot delete SUPERADMIN (except emergency)

3. **USER**
   - Read-only access to database
   - NO access to admin interface
   - Cannot manage users or connections

### Emergency Superadmin Removal
Kenneth's Vision:
> "a superadmin can create admins and users but cannot be kicked out by other
> admins unless there are 3 or more admins and then they can if the superuser
> does not consent on an emergency basis and it must be signed off by 2 other
> admins"

**Requirements:**
- Minimum 3 admins (excluding superadmin)
- 2 admin signatures required
- Reason must be provided
- Executed automatically when 2nd signature added

### Encrypted Fields
**NOT shown in HTML:**
- Passwords
- Private keys
- API secrets
- Any encrypted credentials

**Shown in HTML:**
- Public keys
- API keys (not secrets)
- Connection strings (without passwords)
- Endpoints
- IP addresses

### Blacklist Protection
**Automatically blacklisted:**
- Windows: `C:\Windows\System32\*`, `C:\Program Files\*`, etc.
- Linux/Mac: `/etc/*`, `/boot/*`, `/sys/*`, etc.

**Blacklisted connections:**
- Cannot be enabled
- Show ⚫ gray dot indicator
- Cannot be tested or used

## API Endpoints

### Authentication
- `POST /login` - Login
- `GET /logout` - Logout

### Connections
- `GET /connections` - View connection table
- `POST /api/test-connection/<srl_name>` - Test connection
- `POST /api/toggle-enable/<srl_name>` - Enable/disable
- `POST /api/delete-connection/<srl_name>` - Delete
- `POST /api/change-password/<srl_name>` - Change password

### Users
- `GET /users` - View user table
- `POST /api/create-user` - Create user
- `POST /api/delete-user/<username>` - Delete user
- `POST /api/emergency-removal` - Request emergency removal
- `POST /api/sign-emergency-removal` - Sign emergency request

### Database
- `GET /api/database-info` - Get database metrics and integrity

## Kenneth's Vision Realized

✅ **phpMyAdmin-type interface**: Browser-based admin interface
✅ **Connection table**: All SRL connections with status indicators
✅ **Encrypted credentials**: NOT shown in HTML
✅ **Human-readable auditing**: ID, name, created on, created by
✅ **Status indicators**: Green/red/amber/gray dots
✅ **Action buttons**: Test, enable/disable, edit, delete, change password
✅ **Blacklist protection**: Critical OS/system files blocked
✅ **User management**: Superadmin, admin, user roles
✅ **Emergency removal**: 3+ admins, 2 signatures required
✅ **Security**: Encrypted fields, bitcount verification, session auth

## 🦋 The Complete Substrate Database Admin Interface! ✨

