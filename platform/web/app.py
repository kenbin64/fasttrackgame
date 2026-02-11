"""
ButterflyFx Platform - Main Application

Unified platform for all ButterflyFx products:
- Python API
- Universal Connector
- Universal Hard Drive

Features:
- Unified authentication
- Common navigation
- Product routing
- Subscription management
"""

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import secrets
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.auth.user_manager import PlatformUserManager, UserRole, ProductAccess
from core.auth.decorators import (
    init_auth, 
    require_auth, 
    require_product_access,
    get_current_user
)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Initialize user manager
user_manager = PlatformUserManager()
init_auth(user_manager)

# Create demo users
demo_free = user_manager.register_user(
    username='demo_free',
    email='free@butterflyfx.com',
    password='demo123',
    role=UserRole.FREE
)

demo_basic = user_manager.register_user(
    username='demo_basic',
    email='basic@butterflyfx.com',
    password='demo123',
    role=UserRole.BASIC
)

demo_pro = user_manager.register_user(
    username='demo_pro',
    email='pro@butterflyfx.com',
    password='demo123',
    role=UserRole.PRO
)


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        session_token = user_manager.login(username, password)
        
        if session_token:
            session['session_token'] = session_token
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            user = user_manager.register_user(username, email, password)
            
            # Auto-login after registration
            session_token = user_manager.login(username, password)
            session['session_token'] = session_token
            
            return redirect(url_for('dashboard'))
        
        except ValueError as e:
            return render_template('register.html', error=str(e))
    
    return render_template('register.html')


@app.route('/logout')
def logout():
    """Logout user."""
    session_token = session.get('session_token')
    if session_token:
        user_manager.logout(session_token)
        session.pop('session_token', None)
    
    return redirect(url_for('home'))


# ============================================================================
# PLATFORM ROUTES
# ============================================================================

@app.route('/')
def home():
    """Platform home page - Main landing page."""
    return render_template('landing/butterflyfx.html', current_user=get_current_user())


@app.route('/dashboard')
@require_auth
def dashboard():
    """User dashboard."""
    user = get_current_user()
    accessible_products = user.get_accessible_products()
    
    return render_template(
        'dashboard.html',
        current_user=user,
        accessible_products=accessible_products
    )


@app.route('/products')
def products():
    """All products page."""
    return render_template('products.html', current_user=get_current_user())


@app.route('/pricing')
def pricing():
    """Pricing page."""
    return render_template('pricing.html', current_user=get_current_user())


@app.route('/docs')
def docs():
    """Documentation page."""
    return render_template('docs.html', current_user=get_current_user())


# ============================================================================
# LANDING PAGE ROUTES (Public - No Login Required)
# ============================================================================

@app.route('/harddrive')
def harddrive_landing():
    """Universal Hard Drive landing page."""
    return render_template('landing/harddrive.html', current_user=get_current_user())


@app.route('/connector')
def connector_landing():
    """Universal Connector landing page."""
    return render_template('landing/connector.html', current_user=get_current_user())


@app.route('/pythonapi')
def pythonapi_landing():
    """Python API landing page."""
    return render_template('landing/pythonapi.html', current_user=get_current_user())


@app.route('/database')
def database_landing():
    """Dimensional Database landing page."""
    return render_template('landing/database.html', current_user=get_current_user())


@app.route('/account')
@require_auth
def account():
    """Account settings."""
    return render_template('account.html', current_user=get_current_user())


@app.route('/billing')
@require_auth
def billing():
    """Billing page."""
    return render_template('billing.html', current_user=get_current_user())


@app.route('/api-keys')
@require_auth
def api_keys():
    """API keys management."""
    user = get_current_user()
    return render_template('api_keys.html', current_user=user, api_key=user.api_key)


@app.route('/upgrade')
@require_auth
def upgrade():
    """Upgrade subscription page."""
    product = request.args.get('product')
    return render_template('upgrade.html', current_user=get_current_user(), product=product)


# ============================================================================
# PRODUCT ROUTES
# ============================================================================

@app.route('/products/python-api')
@require_product_access(ProductAccess.PYTHON_API)
def python_api_home():
    """Python API product home."""
    return render_template('products/python_api.html', current_user=get_current_user())


@app.route('/products/universal-connector')
@require_product_access(ProductAccess.UNIVERSAL_CONNECTOR)
def universal_connector_home():
    """Universal Connector product home."""
    return render_template('products/universal_connector.html', current_user=get_current_user())


@app.route('/products/universal-harddrive')
@require_product_access(ProductAccess.UNIVERSAL_HARDDRIVE)
def universal_harddrive_home():
    """Universal Hard Drive product home."""
    return render_template('products/universal_harddrive.html', current_user=get_current_user())


# ============================================================================
# PACKAGE ROUTES
# ============================================================================

@app.route('/packages/python')
def package_python():
    """Python package page."""
    return render_template('packages/python.html', current_user=get_current_user())


@app.route('/packages/nodejs')
def package_nodejs():
    """Node.js package page."""
    return render_template('packages/nodejs.html', current_user=get_current_user())


@app.route('/packages/java')
def package_java():
    """Java package page."""
    return render_template('packages/java.html', current_user=get_current_user())


@app.route('/packages/cpp')
def package_cpp():
    """C++ package page."""
    return render_template('packages/cpp.html', current_user=get_current_user())


@app.route('/packages/go')
def package_go():
    """Go package page."""
    return render_template('packages/go.html', current_user=get_current_user())


# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/user/info')
@require_auth
def api_user_info():
    """Get current user info."""
    user = get_current_user()

    return jsonify({
        'user_id': user.user_id,
        'username': user.username,
        'email': user.email,
        'role': user.role.value,
        'api_key': user.api_key,
        'accessible_products': [p.value for p in user.get_accessible_products()],
        'subscription_expires': user.subscription_expires.isoformat() if user.subscription_expires else None
    })


@app.route('/api/products/access')
@require_auth
def api_products_access():
    """Get user's product access."""
    user = get_current_user()

    products = {}
    for product in ProductAccess:
        products[product.value] = {
            'has_access': user.has_product_access(product),
            'name': product.value.replace('_', ' ').title()
        }

    return jsonify({
        'products': products,
        'role': user.role.value
    })


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print()
    print("=" * 80)
    print("🦋 BUTTERFLYFX PLATFORM")
    print("=" * 80)
    print()
    print("Platform URL: http://localhost:5000")
    print()
    print("Demo Accounts:")
    print("-" * 80)
    print("FREE Tier:")
    print("  Username: demo_free")
    print("  Password: demo123")
    print("  Access: Python API only")
    print()
    print("BASIC Tier:")
    print("  Username: demo_basic")
    print("  Password: demo123")
    print("  Access: Python API + Universal Connector")
    print()
    print("PRO Tier:")
    print("  Username: demo_pro")
    print("  Password: demo123")
    print("  Access: All products")
    print()
    print("=" * 80)
    print()

    app.run(debug=True, host='0.0.0.0', port=5000)

