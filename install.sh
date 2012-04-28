#!/bin/sh

LUTEFISK_TESTS=
export LUTEFISK_TESTS

LUTEFISK_HOME="$(dirname $0)"
. "${LUTEFISK_HOME}"/etc/common

cd "${LUTEFISK_HOME}"

"${LUTEFISK_BIN}"/python.sh setup.py -q install "$@"
[ $? != 0 ] && echo "ERROR!!!" && exit 1

exit 0

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
