# DimensionOS Quick Start Guide

Get DimensionOS running locally in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

## Quick Setup

### 1. Install Dependencies

```bash
cd dimensionOS
pip install -r requirements.txt
```

### 2. Create Environment File

```bash
# Copy the example
cp .env.example .env

# Generate a secret key
python -c "import os; print('SECRET_KEY=' + os.urandom(24).hex())" >> .env
```

### 3. Setup OAuth (Optional for Local Testing)

For local testing, you can skip OAuth setup. The app will still run, but login won't work.

To enable login:

**Google OAuth:**
1. Go to https://console.cloud.google.com/
2. Create a project
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add redirect URI: `https://localhost:5000/authorize/google`
6. Add credentials to `.env`:
   ```
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

**GitHub OAuth:**
1. Go to https://github.com/settings/developers
2. Create new OAuth App
3. Set callback URL: `https://localhost:5000/authorize/github`
4. Add credentials to `.env`:
   ```
   GITHUB_CLIENT_ID=your-client-id
   GITHUB_CLIENT_SECRET=your-client-secret
   ```

### 4. Run the Application

```bash
python run.py
```

Or directly:

```bash
python app.py
```

### 5. Access the Application

Open your browser and go to:
```
https://localhost:5000
```

**Note:** You'll see a security warning because we're using a self-signed SSL certificate for development. This is normal. Click "Advanced" and "Proceed to localhost" (or similar, depending on your browser).

## What You'll See

### Landing Page (/)
- Information about DimensionOS
- Features and capabilities
- Login buttons (if OAuth is configured)

### Dashboard (/dashboard)
After logging in, you'll see:
- **Query Box**: Type natural language queries
- **Dimensional Tree**: View ingested objects
- **Center Panel**: Three view modes (Icon, Table, Dimensional)
- **Attribute Drawer**: Object details
- **Connectors**: External data source integrations

## Try These Queries

Once logged in, try these in the query box:

```
Load bitcoin
Load 2026 Toyota Corolla
Show bitcoin
What is the price?
```

## Project Structure

```
dimensionOS/
├── app.py                    # Main Flask application
├── dimension_os_core.py      # Core logic (uses core_v2)
├── templates/                # HTML templates
│   ├── base.html
│   ├── index.html           # Landing page
│   └── dashboard.html       # Main interface
├── static/                   # Static assets
│   ├── css/
│   │   └── style.css        # Glass-morphic styling
│   └── js/
│       ├── main.js          # Utilities
│       └── dashboard.js     # Dashboard logic
├── requirements.txt          # Python dependencies
├── .env                      # Environment config (create this)
└── README.md                # Full documentation
```

## Development Tips

### Hot Reload

The development server automatically reloads when you change Python files.

### Debugging

Set `FLASK_DEBUG=True` in `.env` for detailed error messages.

### Logs

Check the terminal where you ran `python run.py` for logs.

### Browser Console

Open browser DevTools (F12) to see JavaScript logs and network requests.

## Common Issues

### "Address already in use"

Port 5000 is already taken. Either:
- Stop the other process using port 5000
- Change the port in `run.py`: `app.run(port=5001, ...)`

### SSL Certificate Warning

This is normal for development. The app uses a self-signed certificate. In production, you'll use a real SSL certificate from Let's Encrypt.

### OAuth Login Not Working

Make sure:
- You've set up OAuth apps in Google/GitHub
- Redirect URIs match exactly (including https://)
- Client ID and Secret are correct in `.env`

### Import Errors

Make sure you're in the right directory and have installed dependencies:
```bash
cd dimensionOS
pip install -r requirements.txt
```

## Next Steps

- Read [README.md](README.md) for full documentation
- Read [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Explore the code in `dimension_os_core.py` to see how it uses ButterflyFx
- Customize the UI in `templates/` and `static/`

## Architecture

DimensionOS is built on:
- **ButterflyFx Core (core_v2)**: Dimensional computation engine
- **Kernel**: Pure mathematical substrate operations
- **Flask**: Web framework
- **OAuth**: Social authentication
- **Vanilla JS**: Frontend (no frameworks, pure performance)

All object ingestion and queries go through `dimension_os_core.py`, which uses the ButterflyFx API to create substrates and perform dimensional operations.

## Support

For issues or questions:
1. Check the logs
2. Review the code comments
3. Read the ButterflyFx documentation in `core_v2/API_DOCUMENTATION.py`

Happy dimensional computing! 🦋

