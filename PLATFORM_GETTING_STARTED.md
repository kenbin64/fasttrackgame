# 🚀 DimensionOS Platform - Getting Started

**Privacy-first cloud platform with dimensional computing**

---

## ✅ What's Been Built

### **Core Components (COMPLETE)**

1. **Privacy-First User Model** ✅
   - Anonymous user IDs (SHA256 hashes)
   - NO PII stored on server
   - Bcrypt password hashing
   - Service status management
   - Resource allocation per tier

2. **Authentication System** ✅
   - User registration
   - User login
   - JWT tokens (access + refresh)
   - Password strength validation
   - Service status checking

3. **REST API Endpoints** ✅
   - `/api/auth/register` - Register new user
   - `/api/auth/login` - Login user
   - `/api/auth/refresh` - Refresh access token
   - `/api/auth/logout` - Logout user
   - `/api/user/me` - Get user info
   - `/api/user/status` - Get service status
   - `/api/user/tier` - Update user tier
   - `/api/payment/status` - Update/get payment status
   - `/api/resources/metrics` - Get resource metrics
   - `/api/resources/usage` - Get resource usage

4. **Resource Monitoring** ✅
   - CPU, RAM, storage, network tracking
   - Metrics only (NO content inspection)
   - NO file names, NO queries, NO data

5. **TOS Enforcement** ✅
   - Pattern-based detection
   - Spam, malware, DDoS detection
   - NO content inspection

---

## 🏗️ Quick Start

### **1. Install Dependencies**

```bash
cd server
pip install -r requirements.txt
```

### **2. Set Up Database**

Create PostgreSQL database:

```bash
# Create database
createdb dimensionos

# Or with custom user
createdb -U dimensionos dimensionos
```

Set environment variable (optional):

```bash
export DATABASE_URL="postgresql://dimensionos:dimensionos@localhost:5432/dimensionos"
```

### **3. Initialize Database**

```bash
python server/init_platform_db.py
```

This will:
- Create all tables
- Seed resource allocations for all tiers

### **4. Start Server**

```bash
python server/main_platform.py
```

Server will start on: `http://localhost:8000`

### **5. Test API**

Visit API documentation: `http://localhost:8000/docs`

---

## 📋 API Usage Examples

### **Register User**

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "tier": "free"
  }'
```

Response:
```json
{
  "user_id": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "tier": "free",
  "service_status": "active",
  "trial_ends_at": "2026-03-11T12:00:00"
}
```

### **Login User**

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### **Get User Info**

```bash
curl -X GET http://localhost:8000/api/user/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### **Get Resource Metrics**

```bash
curl -X GET http://localhost:8000/api/resources/metrics \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### **Update Payment Status**

```bash
curl -X POST http://localhost:8000/api/payment/status \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_status": "paid",
    "amount": 10.0,
    "period": "2026-02"
  }'
```

---

## 🔐 Privacy Architecture

### **What Server NEVER Stores:**

❌ Real names  
❌ Email addresses  
❌ Phone numbers  
❌ Billing addresses  
❌ Credit card numbers  
❌ Payment details  
❌ User content  
❌ File names  
❌ Database queries  

### **What Server ONLY Stores:**

✅ Anonymous user ID (SHA256 hash)  
✅ Password hash (bcrypt)  
✅ Service status (active/suspended/cancelled)  
✅ Payment status (paid/unpaid)  
✅ Resource usage metrics (numbers only)  
✅ TOS violation flags (no content)  

---

## 📊 User Tiers

| Tier | CPU | RAM | Storage | Bandwidth | Database | Price |
|------|-----|-----|---------|-----------|----------|-------|
| **FREE** | 1 core | 4GB | 10GB | 1Gbps | SQLite | $0/month (30-day trial) |
| **STARTER** | 8 cores | 64GB | 1TB | 10Gbps | PostgreSQL | $10/month |
| **PRO** | 16 cores | 128GB | 5TB | 100Gbps | PostgreSQL Cluster | $50/month |
| **ENTERPRISE** | 64 cores | 512GB | 50TB | 1Tbps | PostgreSQL + Redis | $500/month |

---

## 🔄 Service Lifecycle

```
Day 0: Payment due
Day 1-3: Grace period → Send reminder
Day 4-7: Soft suspension → Read-only access
Day 8+: Hard suspension → No access

Payment received → Instant reinstatement
```

---

## 🎯 Next Steps

1. **Test the API** - Use the examples above
2. **Build client application** - Electron/Tauri app for credentials and payments
3. **Create landing page** - Next.js marketing site
4. **Implement user provisioning** - Auto-create substrates on signup
5. **Add background jobs** - Payment monitoring, service suspension

---

**Ready to build the future of cloud computing!** 🌌✨


