"""
DimensionOS Web Application
Main Flask application with SSL support and social authentication
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv

# Import DimensionOS core
from dimension_os_core import DimensionOSCore

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))

# CORS configuration
CORS(app)

# OAuth configuration for social login
oauth = OAuth(app)

# Google OAuth
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# GitHub OAuth
github = oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'}
)

# Initialize DimensionOS Core
dimension_os = DimensionOSCore()


# ═══════════════════════════════════════════════════════════════════
# ROUTES - Landing Page & Authentication
# ═══════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Landing page with information and login"""
    user = session.get('user')
    return render_template('index.html', user=user)


@app.route('/login/<provider>')
def login(provider):
    """Initiate OAuth login"""
    if provider == 'google':
        redirect_uri = url_for('authorize_google', _external=True, _scheme='https')
        return google.authorize_redirect(redirect_uri)
    elif provider == 'github':
        redirect_uri = url_for('authorize_github', _external=True, _scheme='https')
        return github.authorize_redirect(redirect_uri)
    return jsonify({'error': 'Unknown provider'}), 400


@app.route('/authorize/google')
def authorize_google():
    """Google OAuth callback"""
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    session['user'] = {
        'provider': 'google',
        'email': user_info['email'],
        'name': user_info['name'],
        'picture': user_info.get('picture')
    }
    return redirect('/dashboard')


@app.route('/authorize/github')
def authorize_github():
    """GitHub OAuth callback"""
    token = github.authorize_access_token()
    resp = github.get('user')
    user_info = resp.json()
    session['user'] = {
        'provider': 'github',
        'email': user_info.get('email'),
        'name': user_info.get('name') or user_info.get('login'),
        'picture': user_info.get('avatar_url')
    }
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('user', None)
    return redirect('/')


@app.route('/dashboard')
def dashboard():
    """Main DimensionOS interface"""
    if 'user' not in session:
        return redirect('/')
    return render_template('dashboard.html', user=session['user'])


# ═══════════════════════════════════════════════════════════════════
# API ROUTES - DimensionOS Operations
# ═══════════════════════════════════════════════════════════════════

@app.route('/api/ingest', methods=['POST'])
def api_ingest():
    """Ingest any object into DimensionOS"""
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    result = dimension_os.ingest(data, user_id=session['user']['email'])
    return jsonify(result)


@app.route('/api/query', methods=['POST'])
def api_query():
    """Natural language query"""
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    query_text = request.json.get('query')
    result = dimension_os.query(query_text, user_id=session['user']['email'])
    return jsonify(result)


@app.route('/api/objects', methods=['GET'])
def api_objects():
    """Get all objects for current user"""
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    objects = dimension_os.get_user_objects(session['user']['email'])
    return jsonify(objects)


if __name__ == '__main__':
    # Development server (use gunicorn + nginx for production)
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')

