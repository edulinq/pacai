#!/bin/bash

# Create a full website including all documentation ready to be deployed.
# This script should only be done from a clean repo on the main branch.
# Documentation will be generated from the main branch (latest) as well as each version tag.

readonly THIS_DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd | xargs realpath)"
readonly ROOT_DIR="${THIS_DIR}/.."
readonly TEMPLATE_HTML_DIR="${THIS_DIR}/html"
readonly BUILD_DIR="${ROOT_DIR}/html"
readonly BASE_OUT_DIR="${ROOT_DIR}/._site"
readonly DOCS_DIRNAME='docs'
readonly DOCS_OUT_DIR="${BASE_OUT_DIR}/${DOCS_DIRNAME}"
readonly GEN_DOCS_SCRIPT="${ROOT_DIR}/scripts/gen_docs.sh"

readonly MAIN_BRANCH="main"

readonly INDEX_TITLE_LOCATION='<header class="pdoc">'
readonly MODULE_TITLE_LOCATION='<section class="module-info">'

readonly API_DOC_MARKER='<!-- API-DOC-MARKER -->'

function check_git() {
    if [ ! -z "$(git status --porcelain)" ] ; then
        echo "ERROR: Repository is not clean."
        exit 1
    fi

    if [ $(git branch --show-current) != 'main' ] ; then
        echo "ERROR: Repository is not on the main branch."
        exit 2
    fi

    return 0
}

function gen_docs() {
    local label=$1
    local reference=$2

    echo "Generating docs for '${label}'."

    rm -rf "${BUILD_DIR}"
    ${GEN_DOCS_SCRIPT}

    # Add in the label to the landing pages.
    local git_link="https://github.com/edulinq/pacai/tree/${reference}"

    local index_title="<h1 style='flex-grow: 1'>Pacai API Reference: <a href='${git_link}'>${label}</a></h1>"
    sed -i "s#${INDEX_TITLE_LOCATION}#${INDEX_TITLE_LOCATION}${index_title}#" "${BUILD_DIR}/index.html"

    local module_title="<h1>Pacai API Reference: <a href='${git_link}'>${label}</a></h1>"
    sed -i "s#${MODULE_TITLE_LOCATION}#${MODULE_TITLE_LOCATION}${module_title}#" "${BUILD_DIR}/pacai.html"

    # Moved the compiled documentation to the main site.
    mkdir -p "${DOCS_OUT_DIR}"
    mv "${BUILD_DIR}" "${DOCS_OUT_DIR}/${label}"

    # Add this documentation to the main index page.
    local index_li="<li><a href='${DOCS_DIRNAME}/${label}/index.html'>${label}</a></li>"
    sed -i "s#${API_DOC_MARKER}#${index_li}${API_DOC_MARKER}#" "${BASE_OUT_DIR}/index.html"
}

function main() {
    if [[ $# -ne 0 ]]; then
        echo "USAGE: $0"
        exit 1
    fi

    set -e
    trap exit SIGINT

    cd "${ROOT_DIR}"

    # Remove any existing output.
    rm -rf "${BASE_OUT_DIR}"
    cp -r "${TEMPLATE_HTML_DIR}" "${BASE_OUT_DIR}"

    # Ensure that the repo looks good.
    check_git

    # Generate the latest documentation.
    local git_hash=$(git rev-parse --short HEAD)
    gen_docs "latest (${git_hash})" "${git_hash}"

    # Generate docs for each tagged version.
    for tag in $(git tag -l | grep -P '^v\d+\.\d+\.\d+') ; do
        git checkout --quiet "${tag}"
        gen_docs "${tag}" "${tag}"
    done

    # Move back to main.
    git checkout --quiet main

    return 0
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && main "$@"
