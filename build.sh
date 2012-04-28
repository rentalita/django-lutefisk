#!/bin/sh

LUTEFISK_TESTS=
export LUTEFISK_TESTS

LUTEFISK_HOME="$(dirname $0)"
. "${LUTEFISK_HOME}"/etc/common

cd "${LUTEFISK_HOME}"

TARGET="$@"
TARGET="${TARGET:-develop}"

"${LUTEFISK_BIN}"/python.sh setup.py -q ${TARGET}
[ $? != 0 ] && echo "ERROR!!!" && exit 1

"${LUTEFISK_BIN}"/django-migrate.sh

exit 0

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
