#!/bin/sh

LUTEFISK_TESTS=1
export LUTEFISK_TESTS

LUTEFISK_HOME="$(dirname $0)"
. "${LUTEFISK_HOME}"/etc/common

cd "${LUTEFISK_HOME}"

"${LUTEFISK_BIN}"/django-migrate.sh

"${LUTEFISK_BIN}"/nosetests.sh "$@"
[ $? != 0 ] && echo "ERROR!!!" && exit 1

exit 0

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
