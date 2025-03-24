# Script to migrate existing monitors to an owner
# Copy this script to a management command or run it as a one-off script

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from monitors.models import Monitor


class Command(BaseCommand):
    help = "Assign owners to existing monitors without owners"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help="Username of the user to assign as owner for existing monitors",
            default="admin",
        )

    def handle(self, *args, **options):
        username = options["username"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"User '{username}' does not exist. Please provide a valid username."
                )
            )
            return

        # Get monitors without owners
        # Note: This is for use after the migration has been applied but before
        # the NOT NULL constraint is enforced
        monitors_without_owner = Monitor.objects.filter(owner__isnull=True)
        count = monitors_without_owner.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS("No monitors found without owners."))
            return

        # Assign the specified user as owner
        monitors_without_owner.update(owner=user)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully assigned {count} monitors to user '{username}'."
            )
        )
