#!/bin/bash
# Frontend environment switcher script

echo "Frontend Environment Switcher"
echo "============================"
echo "Current directory: $(pwd)"

# Check current environment
if [ -f ".frontend-env" ]; then
    current_env=$(grep "CURRENT_ENV=" .frontend-env | cut -d'=' -f2)
    echo "Current environment: $current_env"
else
    echo "No environment file found. Creating one..."
    current_env="unknown"
fi

# Ask user which environment to switch to
echo ""
echo "Which environment do you want to use?"
echo "1) WSL2 (Linux)"
echo "2) Windows"
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        new_env="wsl2"
        echo "Switching to WSL2 environment..."
        ;;
    2)
        new_env="windows"
        echo "Switching to Windows environment..."
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Update environment file
cat > .frontend-env << EOF
# Frontend Development Environment Indicator
# This file indicates which environment is currently set up for frontend development
# DO NOT COMMIT THIS FILE

# Current Environment: $new_env
CURRENT_ENV=$new_env

# Instructions:
# - When developing in WSL2, set CURRENT_ENV=wsl2
# - When developing in Windows, set CURRENT_ENV=windows
# - This helps track which node_modules is currently installed
EOF

echo "Environment switched to: $new_env"
echo ""
echo "Next steps:"
if [ "$new_env" = "windows" ]; then
    echo "1. Open Windows Terminal/PowerShell/CMD"
    echo "2. Navigate to: E:\\PycharmProjects\\stock_analysis_system\\frontend"
    echo "3. Run: npm install"
    echo "4. Run: npm run dev"
else
    echo "1. Stay in WSL2 terminal"
    echo "2. Run: npm install"
    echo "3. Run: npm run dev"
fi