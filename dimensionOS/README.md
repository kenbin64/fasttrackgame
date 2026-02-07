# DimensionOS

**The First Dimensional Operating System**

DimensionOS is a revolutionary web application built on the ButterflyFx dimensional computation framework. It turns anything you give it into a complete dimensional object and returns deterministic truth whenever you ask about it.

## Features

- **Universal Ingestion**: Ingest any object - images, videos, datasets, concepts, workflows, APIs
- **Natural Language Queries**: Ask questions in plain language, get deterministic answers
- **Dimensional Truth**: No hallucinations, no probability - pure mathematical certainty
- **Dimensional Promotion**: All change is movement through dimensions, not mutation
- **Universal Connector**: Connect to Google Drive, Dropbox, databases, APIs, social media
- **Dimensional Analysis**: Predict behavior, simulate physics, compare designs

## Architecture

DimensionOS is built on top of:
- **Kernel Layer**: Pure mathematical substrate operations (immutable)
- **Core Layer**: ButterflyFx API, SRL connections, dimensional programming
- **DimensionOS Layer**: Web interface, authentication, query processing

## Installation

### Prerequisites

- Python 3.10+
- ButterflyFx core_v2 and kernel (included in parent directory)

### Setup

1. **Clone the repository** (if not already done)

2. **Install dependencies**:
   ```bash
   cd dimensionOS
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your OAuth credentials and secret key
   ```

4. **Set up OAuth Applications**:

   **Google OAuth**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google+ API
   - Create OAuth 2.0 credentials
   - Add authorized redirect URI: `https://dimensionos.net/authorize/google`
   - Copy Client ID and Client Secret to `.env`

   **GitHub OAuth**:
   - Go to [GitHub Developer Settings](https://github.com/settings/developers)
   - Create new OAuth App
   - Set Authorization callback URL: `https://dimensionos.net/authorize/github`
   - Copy Client ID and Client Secret to `.env`

## Running Locally

### Development Mode

```bash
python app.py
```

The app will run on `https://localhost:5000` with a self-signed SSL certificate.

### Production Mode

Use gunicorn with nginx:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

Then configure nginx as a reverse proxy with SSL.

## SSL Configuration

### For Development

The app uses Flask's `ssl_context='adhoc'` for development, which generates a self-signed certificate.

### For Production (dimensionos.net)

1. **Get SSL Certificate**:
   - Use Let's Encrypt (recommended):
     ```bash
     sudo certbot certonly --standalone -d dimensionos.net
     ```
   - Or use a commercial SSL provider

2. **Configure nginx**:
   ```nginx
   server {
       listen 443 ssl;
       server_name dimensionos.net;
       
       ssl_certificate /etc/letsencrypt/live/dimensionos.net/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/dimensionos.net/privkey.pem;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   
   server {
       listen 80;
       server_name dimensionos.net;
       return 301 https://$server_name$request_uri;
   }
   ```

3. **Start services**:
   ```bash
   sudo systemctl start nginx
   gunicorn -w 4 -b 127.0.0.1:8000 app:app
   ```

## Usage

### Landing Page

Visit `https://dimensionos.net` to see:
- Information about DimensionOS
- Features and capabilities
- Login with Google or GitHub

### Dashboard

After logging in, you'll see:
- **Query Box**: Natural language interface
- **Dimensional Tree**: Hierarchical view of objects
- **Center Panel**: Icon, Table, and Dimensional views
- **Attribute Drawer**: Object metadata and properties
- **Connectors**: Integration with external data sources

### Example Queries

```
Load bitcoin
What is the price?
Load 2026 Toyota Corolla
What's the gas mileage?
Show bitcoin
```

## API Endpoints

- `POST /api/ingest` - Ingest an object
- `POST /api/query` - Natural language query
- `GET /api/objects` - Get all user objects

## Philosophy

1. **Existence implies completeness**: Every object is a dimensional substrate with inherent structure
2. **Truth over probability**: No guessing or hallucinations - deterministic truth only
3. **Dimensional promotion, not mutation**: Change is movement through dimensions
4. **Natural language interface**: Users interact through plain language

## Built With

- **Backend**: Flask, Authlib (OAuth), ButterflyFx core_v2
- **Frontend**: Vanilla JavaScript, Glass-morphic CSS
- **Authentication**: Google OAuth, GitHub OAuth
- **Computation**: ButterflyFx dimensional computation framework

## License

Proprietary - ButterflyFx Dimensional Computation Model

## Author

Kenneth Bingham

