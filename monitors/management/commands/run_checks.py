from django.core.management.base import BaseCommand
from monitors.models import Monitor, Check
from monitors.services.checks import check_monitor
import time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run all monitor checks"

    def add_arguments(self, parser):
        parser.add_argument(
            "--once",
            action="store_true",
            help="Run checks only once instead of continuously",
        )
        parser.add_argument(
            "--monitor-id",
            type=str,
            help="Run check for a specific monitor by ID",
        )

    def handle(self, *args, **options):
        run_once = options["once"]
        specific_monitor_id = options["monitor_id"]

        self.stdout.write(self.style.SUCCESS("Starting monitor checks"))

        if specific_monitor_id:
            try:
                monitors = [Monitor.objects.get(id=specific_monitor_id)]
                self.stdout.write(f"Running check for monitor: {monitors[0].name}")
            except Monitor.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Monitor with ID {specific_monitor_id} not found")
                )
                return
        else:
            monitors = Monitor.objects.all()
            self.stdout.write(f"Found {len(monitors)} monitors to check")

        # Run checks once or continuously
        if run_once:
            self._run_checks(monitors)
        else:
            try:
                while True:
                    start_time = time.time()
                    self._run_checks(monitors)

                    # Calculate sleep time (minimum 5 seconds between checks)
                    elapsed = time.time() - start_time
                    sleep_time = max(
                        5, 60 - elapsed
                    )  # At least sleep 5 seconds, at most 60

                    self.stdout.write(f"Sleeping for {sleep_time:.1f} seconds")
                    time.sleep(sleep_time)
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS("\nStopping monitor checks"))

    def _run_checks(self, monitors):
        """Run checks for all provided monitors"""
        for monitor in monitors:
            self.stdout.write(f"Checking {monitor.name} ({monitor.monitor_type})...")

            try:
                # Run the check
                result = check_monitor(monitor)

                # Create check record in database
                Check.objects.create(
                    monitor=monitor,
                    is_up=result["is_up"],
                    response_time=result["response_time"],
                    status_code=result["status_code"],
                    error_message=result["error_message"],
                )

                # Log the result
                status = "UP" if result["is_up"] else "DOWN"
                response_time = (
                    f"{result['response_time']:.1f}ms"
                    if result["response_time"]
                    else "N/A"
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{monitor.name}: {status} - Response time: {response_time}"
                    )
                    if result["is_up"]
                    else self.style.ERROR(
                        f"{monitor.name}: {status} - Error: {result['error_message']}"
                    )
                )
            except Exception as e:
                logger.exception(f"Error checking monitor {monitor.name}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f"Error checking {monitor.name}: {str(e)}")
                )
