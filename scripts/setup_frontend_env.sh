#!/bin/bash
# Frontend Environment Setup Script for Stock Analysis System
# Compatible with both WSL2 and native Linux

echo "=== Stock Analysis System Frontend Environment Setup ==="
echo "This script will set up Node.js environment for React development"
echo ""

# Detect environment
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "Detected WSL2 environment"
    ENV_TYPE="WSL2"
else
    echo "Detected native Linux environment"
    ENV_TYPE="LINUX"
fi

# Function to install nvm
install_nvm() {
    echo "Installing NVM (Node Version Manager)..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
    
    # Source nvm
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
    
    # Add to bashrc
    echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.bashrc
    echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> ~/.bashrc
    echo '[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"' >> ~/.bashrc
}

# Check if nvm is installed
if ! command -v nvm &> /dev/null; then
    install_nvm
else
    echo "NVM already installed"
fi

# Install Node.js 18 LTS
echo "Installing Node.js 18 LTS..."
nvm install 18
nvm use 18
nvm alias default 18

# Verify installation
echo ""
echo "=== Installation Summary ==="
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"

# Set npm registry (for China)
echo "Setting npm registry to taobao mirror..."
npm config set registry https://registry.npmmirror.com/

# Create project directory structure
echo "Creating frontend project structure..."
mkdir -p frontend/{src,public,docs}

# Create package.json template
cat > frontend/package.json.template << 'EOF'
{
  "name": "stock-analysis-frontend",
  "version": "1.0.0",
  "description": "Claude.ai style frontend for Stock Analysis System",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0",
    "rehype-katex": "^7.0.0",
    "remark-math": "^6.0.0",
    "react-syntax-highlighter": "^15.5.0",
    "axios": "^1.6.0",
    "react-router-dom": "^6.20.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@types/react-syntax-highlighter": "^15.5.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "autoprefixer": "^10.4.0",
    "eslint": "^8.0.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.3.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0"
  }
}
EOF

echo ""
echo "=== Setup Complete ==="
echo "Frontend environment has been set up successfully!"
echo ""
echo "Next steps:"
echo "1. For Windows Anaconda setup, run the Windows setup script"
echo "2. Navigate to frontend/ directory to start React development"
echo "3. Use 'npm create vite@latest .' to initialize the React project"
echo ""
echo "Environment info saved to: backups/environment/"