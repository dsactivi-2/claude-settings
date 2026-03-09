#!/bin/bash
# Skills Database Filter - Bash Wrapper
# Provides convenient CLI interface to Python filter module

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/skills_filter.py"
PYTHON_INTERPRETER="$HOME/.local/pipx/venvs/open-interpreter/bin/python"

# Check if Python script exists
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "Error: skills_filter.py not found at $PYTHON_SCRIPT" >&2
    exit 1
fi

# Check if Python interpreter exists, fallback to system python3
if [[ ! -f "$PYTHON_INTERPRETER" ]]; then
    echo "Warning: pipx python not found at $PYTHON_INTERPRETER, using system python3" >&2
    if ! command -v python3 &> /dev/null; then
        echo "Error: python3 not found" >&2
        exit 1
    fi
    PYTHON_INTERPRETER="python3"
fi

# Pass all arguments to Python script
"$PYTHON_INTERPRETER" "$PYTHON_SCRIPT" "$@"
