import logging
import django_rq
from django.core.management.base import BaseCommand
from django.utils import timezone

from monitors.models import Monitor
from monitors.tasks import perform_check

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Schedule all monitors with RQ Scheduler"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear all existing scheduled jobs before scheduling",
        )

    def handle(self, *args, **options):
        scheduler = django_rq.get_scheduler()

        # Clear existing jobs if requested
        if options["clear"]:
            self.stdout.write("Clearing existing scheduled jobs...")
            scheduler.clear()

        # Get all active monitors
        monitors = Monitor.objects.all()
        self.stdout.write(f"Found {len(monitors)} monitors to schedule")

        # Schedule each monitor
        for monitor in monitors:
            # Get the interval in seconds
            interval = monitor.interval_seconds

            # Check if this monitor is already scheduled
            scheduled_job = None
            for job in scheduler.get_jobs():
                if hasattr(job, "meta") and job.meta.get("monitor_id") == str(
                    monitor.id
                ):
                    scheduled_job = job
                    break

            # If the job exists and the interval has changed, cancel it
            if scheduled_job and scheduled_job.meta.get("interval") != interval:
                self.stdout.write(f"Removing outdated job for monitor: {monitor.name}")
                scheduled_job.cancel()
                scheduled_job = None

            # Schedule a new job if needed
            if not scheduled_job:
                job = scheduler.schedule(
                    scheduled_time=timezone.now(),
                    func=perform_check,
                    args=[str(monitor.id)],
                    interval=interval,
                    repeat=None,  # Repeat indefinitely
                )

                # Store metadata about this job
                job.meta = {
                    "monitor_id": str(monitor.id),
                    "monitor_name": monitor.name,
                    "interval": interval,
                    "scheduled_at": timezone.now().isoformat(),
                }
                job.save_meta()

                self.stdout.write(
                    f"Scheduled monitor: {monitor.name} - every {interval} seconds"
                )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully scheduled {len(monitors)} monitors")
        )
