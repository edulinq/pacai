#!/bin/bash

# Profile a pacai module.
# Any arguments passed to this script will be forwarded to the module.

readonly THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
readonly ROOT_DIR="${THIS_DIR}/.."

readonly TEMP_STATS_PATH="/tmp/pacai_profile_stats.cprofile"

readonly ROW_COUNT=50

function main() {
    if [[ $# -eq 0 ]]; then
        echo "USAGE: $0 <module> [args ...]"
        exit 1
    fi

    set -e
    trap exit SIGINT

    local module="$1"
    shift

    cd "${ROOT_DIR}"

    echo "Profiling ..."
    # TEST
    # python -m cProfile -o "${TEMP_STATS_PATH}" -m "${module}" "$@" > "${TEMP_STATS_PATH}.out" 2> "${TEMP_STATS_PATH}.err"
    python -m cProfile -o "${TEMP_STATS_PATH}" -m "${module}" "$@"
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
