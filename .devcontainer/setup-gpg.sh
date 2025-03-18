#!/bin/bash
set -e

# Fix permissions
sudo chown -R vscode:vscode ~/.gnupg
chmod 700 ~/.gnupg
chmod 600 ~/.gnupg/* 2>/dev/null || true

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

echo "GPG configuration completed successfully"
gpg --list-secret-keys
git config --global --list
