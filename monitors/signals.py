from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import django_rq

from monitors.models import Monitor
from monitors.tasks import perform_check


@receiver(post_save, sender=Monitor)
def schedule_monitor_on_save(sender, instance, created, **kwargs):
    scheduler = django_rq.get_scheduler()

    for job in scheduler.get_jobs():
        if hasattr(job, "meta") and job.meta.get("monitor_id") == str(instance.id):
            job.delete()
            break

    job = scheduler.schedule(
        scheduled_time=timezone.now(),
        func=perform_check,
        args=[str(instance.id)],
        interval=instance.interval_seconds,
        repeat=None,
    )

    job.meta = {
        "monitor_id": str(instance.id),
        "monitor_name": instance.name,
        "interval": instance.interval_seconds,
        "scheduled_at": timezone.now().isoformat(),
    }
    job.save_meta()


@receiver(post_delete, sender=Monitor)
def remove_monitor_schedule(sender, instance, **kwargs):
    scheduler = django_rq.get_scheduler()

    for job in scheduler.get_jobs():
        if hasattr(job, "meta") and job.meta.get("monitor_id") == str(instance.id):
            job.delete()
            break
