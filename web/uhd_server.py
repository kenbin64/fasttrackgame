"""
Simple Flask server for Universal HD development/preview.
"""
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def universal_hard_drive():
    """Universal Hard Drive - Connect to anything interface."""
    return render_template('universal_hard_drive.html')

if __name__ == '__main__':
    print("=" * 60)
    print("ButterflyFX Universal HD Server")
    print("=" * 60)
    print("Open http://127.0.0.1:5000 in your browser")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=5000)
