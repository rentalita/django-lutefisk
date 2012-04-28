#!/bin/sh

LUTEFISK_HOME="$(dirname $0)"/..
export LUTEFISK_HOME

. "${LUTEFISK_HOME}"/etc/common

"${SQLITE3}" ${SQLITE3FLAGS} ${LUTEFISK_SQLITE3FLAGS} "$@"

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
