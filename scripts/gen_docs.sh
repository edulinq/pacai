#!/bin/bash

# Create HTML documentation for the current code.

readonly THIS_DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd | xargs realpath)"
readonly ROOT_DIR="${THIS_DIR}/.."

function main() {
    if [[ $# -gt 1 ]]; then
        echo "USAGE: $0 [out dir]"
        exit 1
    fi

    set -e
    trap exit SIGINT

    local outputDir="${ROOT_DIR}/html"
    if [[ $# -gt 0 ]]; then
        outputDir=$1
    fi

    cd "${ROOT_DIR}"

    mkdir -p "${outputDir}"

    pdoc --output-directory "${outputDir}" pacai !.*\.test_.*

    return 0
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && main "$@"
