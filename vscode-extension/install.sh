#!/bin/bash
# Dimensional VPS Optimizer - Installation Script

set -e

echo "╔════════════════════════════════════════════╗"
echo "║  Dimensional VPS Optimizer - Install       ║"
echo "║  z = x·y | φ = 1.618... | Layers: 1-7      ║"
echo "╚════════════════════════════════════════════╝"

# Navigate to extension directory
cd "$(dirname "$0")"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js first."
    exit 1
fi

echo "✓ Node.js $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm first."
    exit 1
fi

echo "✓ npm $(npm --version)"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
npm install

# Compile TypeScript
echo ""
echo "🔨 Compiling TypeScript..."
npm run compile

# Check if vsce is installed
if ! command -v vsce &> /dev/null; then
    echo ""
    echo "📦 Installing vsce (VS Code Extension CLI)..."
    npm install -g @vscode/vsce
fi

# Package extension
echo ""
echo "📦 Packaging extension..."
vsce package

# Find the generated .vsix file
VSIX_FILE=$(ls -t *.vsix 2>/dev/null | head -1)

if [ -n "$VSIX_FILE" ]; then
    echo ""
    echo "✅ Extension packaged: $VSIX_FILE"
    echo ""
    echo "To install in VS Code:"
    echo "  1. Open VS Code"
    echo "  2. Go to Extensions (Ctrl+Shift+X)"
    echo "  3. Click '...' → 'Install from VSIX...'"
    echo "  4. Select: $(pwd)/$VSIX_FILE"
    echo ""
    echo "Or install via command line:"
    echo "  code --install-extension $VSIX_FILE"
else
    echo ""
    echo "⚠️  No .vsix file found. Check for errors above."
fi

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║  Installation complete!                    ║"
echo "╚════════════════════════════════════════════╝"
