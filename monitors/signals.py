from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import django_rq

from monitors.models import Monitor
from monitors.tasks import perform_check


@receiver(post_save, sender=Monitor)
def schedule_monitor_on_save(sender, instance, created, **kwargs):
    """When a monitor is saved, update its schedule"""
    scheduler = django_rq.get_scheduler()

    # Find and remove any existing jobs for this monitor
    for job in scheduler.get_jobs():
        if hasattr(job, "meta") and job.meta.get("monitor_id") == str(instance.id):
            job.cancel()
            break

    # Create a new scheduled job
    job = scheduler.schedule(
        scheduled_time=timezone.now(),
        func=perform_check,
        args=[str(instance.id)],
        interval=instance.interval_seconds,
        repeat=None,  # Repeat indefinitely
    )

    # Store metadata about this job
    job.meta = {
        "monitor_id": str(instance.id),
        "monitor_name": instance.name,
        "interval": instance.interval_seconds,
        "scheduled_at": timezone.now().isoformat(),
    }
    job.save_meta()


@receiver(post_delete, sender=Monitor)
def remove_monitor_schedule(sender, instance, **kwargs):
    """When a monitor is deleted, remove its scheduled job"""
    scheduler = django_rq.get_scheduler()

    # Find and remove any existing jobs for this monitor
    for job in scheduler.get_jobs():
        if hasattr(job, "meta") and job.meta.get("monitor_id") == str(instance.id):
            job.cancel()
            break
