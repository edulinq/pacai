#!/bin/bash

# Generate any data used for testing.
# This should only be necessary to run when output formats change.

readonly THIS_DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd | xargs realpath)"
readonly ROOT_DIR="${THIS_DIR}/.."

function main() {
    if [[ $# -ne 0 ]]; then
        echo "USAGE: $0"
        exit 1
    fi

    set -e
    trap exit SIGINT

    cd "${ROOT_DIR}"

    local error_count=0

    python3 -m pacai.pacman.bin --seed 4 --ui pacai.ui.null.NullUI --pacman pacai.agents.random.RandomAgent --board maze-test.board --save-path pacai/test/data/maze-test-random-replay.json
    ((error_count += $?))

    if [[ ${error_count} -gt 0 ]] ; then
        echo "Found ${error_count} issues."
    else
        echo "No issues found."
    fi

    return ${error_count}
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && main "$@"
