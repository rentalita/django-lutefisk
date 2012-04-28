#!/bin/sh

LUTEFISK_TESTS=
export LUTEFISK_TESTS

LUTEFISK_HOME="$(dirname $0)"
. "${LUTEFISK_HOME}"/etc/common

cd "${LUTEFISK_HOME}"

"${LUTEFISK_BIN}"/python.sh setup.py -q clean "$@"
[ $? != 0 ] && echo "ERROR!!!" && exit 1

find . -name "*~" | xargs rm -f
find . -name "*.pyc" | xargs rm -f

exit 0

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
