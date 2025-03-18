#!/bin/bash
set -e

echo "Starting GPG setup..."

# Get Git config from host system
HOST_GIT_NAME=$(git config --global user.name || echo "")
HOST_GIT_EMAIL=$(git config --global user.email || echo "")

# Configure Git with host values or ask user
if [ -n "$HOST_GIT_NAME" ]; then
    git config --global user.name "$HOST_GIT_NAME"
    echo "✅ Git user.name configured from host: $HOST_GIT_NAME"
else
    echo "⚠️ Git user.name not found. Please run:"
    echo "git config --global user.name 'Your Name'"
fi

if [ -n "$HOST_GIT_EMAIL" ]; then
    git config --global user.email "$HOST_GIT_EMAIL"
    echo "✅ Git user.email configured from host: $HOST_GIT_EMAIL"
else
    echo "⚠️ Git user.email not found. Please run:"
    echo "git config --global user.email 'your.email@example.com'"
fi

# Configure Git defaults
git config --global core.editor "code --wait"
git config --global pull.rebase false
git config --global init.defaultBranch main

# Check if .gnupg is writable
if touch ~/.gnupg/.test 2>/dev/null; then
    rm ~/.gnupg/.test
    echo "Setting up GPG permissions..."
    sudo chown -R vscode:vscode ~/.gnupg
    chmod 700 ~/.gnupg
    chmod 600 ~/.gnupg/* 2>/dev/null || true
else
    echo "Note: .gnupg is mounted read-only, skipping permissions setup"
fi

# Check if GPG key exists
if gpg --list-secret-keys --keyid-format LONG > /dev/null 2>&1; then
    # Get GPG key ID
    KEY_ID=$(gpg --list-secret-keys --keyid-format LONG | grep sec | cut -d'/' -f2 | cut -d' ' -f1)

    if [ -n "$KEY_ID" ]; then
        echo "Configuring Git commit signing..."
        git config --global user.signingkey $KEY_ID
        git config --global commit.gpgsign true
        echo "✅ GPG signing enabled with key: $KEY_ID"
    fi
else
    echo "ℹ️ No GPG keys found. Commit signing will be disabled."
    echo "To enable commit signing:"
    echo "1. Import your GPG key"
    echo "2. Enable signing in VS Code settings"
fi

echo "Current GPG configuration:"
gpg --list-secret-keys || echo "No keys found"
echo "Current Git configuration:"
git config --global --list || echo "No git config found"
