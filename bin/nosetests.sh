#!/bin/sh

LUTEFISK_HOME="$(dirname $0)"/..
export LUTEFISK_HOME

. "${LUTEFISK_HOME}"/etc/common

"${NOSETESTS}" ${NOSETESTSFLAGS} ${LUTEFISK_NOSETESTSFLAGS} "$@"

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
