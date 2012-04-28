#!/bin/sh

LUTEFISK_HOME="$(dirname $0)"/..
export LUTEFISK_HOME

. "${LUTEFISK_HOME}"/etc/common

LOCALES="es"

for locale in ${LOCALES}; do
    (
        cd "${LUTEFISK_SRC}"/python/lutefisk
        "${LUTEFISK_BIN}"/django-manage.sh makemessages -l "${locale}" -e .html -e .txt -e .js
        "${LUTEFISK_BIN}"/django-manage.sh compilemessages -l "${locale}"
    )
done

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
