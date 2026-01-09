#!/bin/bash
# Setup script for DVC Google Cloud Storage authentication
# Usage: source setup_dvc_env.sh

export GOOGLE_APPLICATION_CREDENTIALS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/grand-principle-480715-v1-bbe44ac95b61.json"
echo "✓ GOOGLE_APPLICATION_CREDENTIALS set to: $GOOGLE_APPLICATION_CREDENTIALS"
echo "✓ You can now run: dvc push"

