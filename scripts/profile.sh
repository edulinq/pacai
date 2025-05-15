#!/bin/bash

# Profile a pacai module or script.
# Any arguments passed to this script will be forwarded to the profiling target.

readonly THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
readonly ROOT_DIR="${THIS_DIR}/.."

readonly TEMP_STATS_PATH="/tmp/pacai_profile_stats.cprofile"

readonly ROW_COUNT=50

function main() {
    if [[ $# -eq 0 ]]; then
        echo "USAGE: $0 <target> [args ...]"
        exit 1
    fi

    set -e
    trap exit SIGINT

    local target="$1"
    shift

    if [[ $target != *.py ]] ; then
        target="-m ${target}"
    fi

    cd "${ROOT_DIR}"

    echo "Profiling ..."
    python -m cProfile -o "${TEMP_STATS_PATH}" ${target} "$@"
    echo "Profiling Complete"
    echo ""

    echo "--- BEGIN: All Functions, Sorted by Cumulative Time, Top ${ROW_COUNT} ---"
    python -c "import pstats ; stats = pstats.Stats('${TEMP_STATS_PATH}') ; stats.sort_stats('cumtime').print_stats(${ROW_COUNT})"
    echo "--- END: All Functions, Sorted by Cumulative Time, Top ${ROW_COUNT} ---"

    echo "--- BEGIN: All Functions, Sorted by Total Time, Top ${ROW_COUNT} ---"
    python -c "import pstats ; stats = pstats.Stats('${TEMP_STATS_PATH}') ; stats.sort_stats('tottime').print_stats(${ROW_COUNT})"
    echo "--- END: All Functions, Sorted by Total Time, Top ${ROW_COUNT} ---"

    echo "--- BEGIN: Pacai Functions, Sorted by Cumulative Time, Top ${ROW_COUNT} ---"
    python -c "import pstats ; stats = pstats.Stats('${TEMP_STATS_PATH}') ; stats.sort_stats('cumtime').print_stats('pacai', ${ROW_COUNT})"
    echo "--- END: Pacai Functions, Sorted by Cumulative Time, Top ${ROW_COUNT} ---"

    echo "--- BEGIN: Pacai Functions, Sorted by Total Time, Top ${ROW_COUNT} ---"
    python -c "import pstats ; stats = pstats.Stats('${TEMP_STATS_PATH}') ; stats.sort_stats('tottime').print_stats('pacai', ${ROW_COUNT})"
    echo "--- END: Pacai Functions, Sorted by Total Time, Top ${ROW_COUNT} ---"
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && main "$@"
