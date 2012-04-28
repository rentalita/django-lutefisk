# -*- coding: utf-8 -*-

from south.db import db
from south.v2 import SchemaMigration

class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('userena_userenasignup', 'lutefisk_lutefisksignup')

    def backwards(self, orm):
        db.rename_table('lutefisk_lutefisksignup','userena_userenasignup')

# Local Variables:
# indent-tabs-mode: nil
# End:
# vim: ai et sw=4 ts=4
