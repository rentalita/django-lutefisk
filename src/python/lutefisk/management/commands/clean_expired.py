from django.core.management.base import NoArgsCommand

from lutefisk.models import LutefiskSignup

class Command(NoArgsCommand):
    """
    Search for users that still haven't verified their email after
    ``LUTEFISK_ACTIVATION_DAYS`` and delete them.

    """
    help = 'Deletes expired users.'
    def handle_noargs(self, **options):
        users = LutefiskSignup.objects.delete_expired_users()
