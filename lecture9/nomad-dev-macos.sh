#!/usr/bin/env bash
# macOS + Docker Desktop: put Nomad state under $HOME so Docker can bind-mount allocs.
# (Default -dev uses /private/tmp/NomadClient* → often "permission denied" in Docker.)
#
# Usage:
#   chmod +x nomad-dev-macos.sh
#   ./nomad-dev-macos.sh
#
# Optional: NOMAD_MACOS_DATA_DIR=/path ./nomad-dev-macos.sh

set -euo pipefail

DATA_DIR="${NOMAD_MACOS_DATA_DIR:-$HOME/nomad-dev-data}"
mkdir -p "$DATA_DIR"

echo "Nomad -dev data dir: $DATA_DIR"
echo "Starting agent (sudo). Press Ctrl+C to stop."
exec sudo nomad agent -dev \
  -data-dir="$DATA_DIR" \
  -bind 0.0.0.0 \
  -network-interface='{{ GetDefaultInterfaces | attr "name" }}'
