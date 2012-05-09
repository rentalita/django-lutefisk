#!/bin/sh

LUTEFISK_HOME="$(dirname $0)"/..
export LUTEFISK_HOME

. "${LUTEFISK_HOME}"/etc/common

"${LUTEFISK_BIN}"/django-manage.sh syncdb --noinput
"${LUTEFISK_BIN}"/django-manage.sh migrate

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
