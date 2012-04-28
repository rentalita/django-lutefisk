#!/bin/sh

LUTEFISK_HOME="$(dirname $0)"/..
export LUTEFISK_HOME

. "${LUTEFISK_HOME}"/etc/common

TARGET="$@"
TARGET="${TARGET:-help}"

"${LUTEFISK_BIN}"/python.sh "${LUTEFISK_BIN}"/django-manage.py ${TARGET} --settings="${DJANGO_SETTINGS_MODULE}" -v 0

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
