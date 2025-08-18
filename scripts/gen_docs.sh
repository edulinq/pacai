#!/bin/bash

# Create HTML documentation for the current code.

readonly THIS_DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd | xargs realpath)"
readonly ROOT_DIR="${THIS_DIR}/.."
readonly FAVICON_PATH="${ROOT_DIR}/.ci/html/images/favicon.ico"

function main() {
    if [[ $# -gt 1 ]]; then
        echo "USAGE: $0 [out dir]"
        exit 1
    fi

    set -e
    trap exit SIGINT

    local output_dir="${ROOT_DIR}/html"
    if [[ $# -gt 0 ]]; then
        output_dir=$1
    fi

    cd "${ROOT_DIR}"

    mkdir -p "${output_dir}"

    pdoc --output-directory "${output_dir}" --favicon "$(basename "${FAVICON_PATH}")" ./pacai edq !.*_test
    cp "${FAVICON_PATH}" "${output_dir}"

    return $?
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && main "$@"
