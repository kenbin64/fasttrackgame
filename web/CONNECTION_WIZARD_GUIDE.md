# Connection Wizard Guide

## 🧙‍♂️ Creating a Weather API Connection

### Step 1: Get a Weather API Key

1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Navigate to "API keys" section
4. Copy your API key

### Step 2: Access the Connection Wizard

1. Start the admin interface:
   ```bash
   cd web
   python admin_interface.py
   ```

2. Login at `http://localhost:5000`
   - Username: `admin`
   - Password: `admin123`

3. Click "🧙‍♂️ Add Connection" button

### Step 3: Select Connection Type

Choose **REST API** from the connection type cards.

### Step 4: Configure the API Connection

Fill in the following details:

- **Connection Name**: `weather_api` (or any name you prefer)
- **API URL**: `https://api.openweathermap.org/data/2.5`
- **API Key**: Your OpenWeatherMap API key
- **HTTP Method**: `GET` (default)

### Step 5: Test the Connection

Click the "🔍 Test Connection" button. The wizard will:

1. Make a test request to the Weather API
2. Verify the API key is valid
3. Display the test result

**Expected Result:**
```
✅ Connection Successful!
API connection successful (HTTP 200)
```

**If the test fails:**
- ❌ Invalid API key → Check your API key
- ❌ Connection failed → Check your internet connection
- ❌ HTTP Error → Check the API URL

### Step 6: Save the Connection

Click "💾 Save Connection". The wizard will:

1. Encrypt your API key with the master key
2. Calculate bitcount for anti-tampering verification
3. Create an SRL (Substrate Resource Locator)
4. Register the connection in the database
5. Redirect you to the connections table

### Step 7: Use the Connection

Once saved, you can:

1. **Test Connection**: Click 🔍 to test the API
2. **Enable/Disable**: Click ⏸️/▶️ to toggle availability
3. **Query Data**: Use the database query interface
4. **Change API Key**: Click 🔑 to update credentials
5. **Delete**: Click 🗑️ to remove the connection

## 🌐 Example Weather API Queries

Once the connection is created, you can query weather data:

### Query Current Weather
```python
# Query weather for London
result = db.query('weather_api', '/weather?q=London&appid=YOUR_API_KEY')
```

### Query 5-Day Forecast
```python
# Query 5-day forecast for New York
result = db.query('weather_api', '/forecast?q=New York&appid=YOUR_API_KEY')
```

### Query by Coordinates
```python
# Query weather by latitude/longitude
result = db.query('weather_api', '/weather?lat=51.5074&lon=-0.1278&appid=YOUR_API_KEY')
```

## 🔒 Security Features

### Encrypted Credentials
- API key is encrypted with master key
- Stored with SHA256 bitcount verification
- Never shown in HTML interface
- Decrypted in RAM only during queries

### Lazy Loading
- Connection NOT created when registered
- Connection created on first query
- Connection closed after query completes
- Fresh data always from source

### Status Tracking
- 🟢 Connected - Last query successful
- 🔴 Disconnected - Not yet queried or last query failed
- 🟠 Connecting - Query in progress
- ⚫ Blacklisted - Connection blocked

## 📊 Connection Table Display

After saving, the connection appears in the table:

| ID | Name | Type | Status | Connection | Endpoint | Protocol | Actions |
|----|------|------|--------|------------|----------|----------|---------|
| a1b2c3d4 | weather_api | API | ✅ | 🔴 | https://api.openweathermap.org/data/2.5 | HTTPS | 🔍 ⏸️ ✏️ 🔑 🗑️ |

**Columns:**
- **ID**: First 8 characters of substrate ID
- **Name**: Connection name
- **Type**: API (with blue badge)
- **Status**: ✅ Enabled / ❌ Disabled
- **Connection**: 🟢🔴🟠⚫ connection status
- **Endpoint**: API URL (NO API key shown!)
- **Protocol**: HTTPS
- **Actions**: Test, Enable/Disable, Edit, Change Key, Delete

## 🦋 Kenneth's Vision Realized

✅ **Connection Wizard**: Multi-step wizard for creating connections
✅ **Weather API**: Example API connection with OpenWeatherMap
✅ **Encrypted Credentials**: API key encrypted and hidden
✅ **Test Before Save**: Verify connection works before saving
✅ **Lazy Loading**: Connection created on query, not on registration
✅ **Status Tracking**: Real-time connection status indicators
✅ **Security**: Bitcount verification, encrypted storage
✅ **User-Friendly**: Beautiful UI with step-by-step guidance

## 🚀 Next Steps

1. **Try Other Connection Types**:
   - Database (PostgreSQL, MySQL)
   - File System (local files)
   - Stream (WebSocket, MQTT)

2. **Query Weather Data**:
   - Use the database query interface
   - Convert weather data to substrates
   - Store weather patterns

3. **Build Weather Dashboard**:
   - Create visualizations
   - Track weather patterns over time
   - Predict weather using substrate patterns

**The Connection Wizard makes it easy to connect to any external data source!** 🦋✨

