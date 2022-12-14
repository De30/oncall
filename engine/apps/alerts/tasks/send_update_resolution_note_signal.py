from django.apps import apps
from django.conf import settings

from apps.alerts.signals import alert_group_update_resolution_note_signal
from common.custom_celery_tasks import shared_dedicated_queue_retry_task


@shared_dedicated_queue_retry_task(
    autoretry_for=(Exception,), retry_backoff=True, max_retries=1 if settings.DEBUG else None
)
def send_update_resolution_note_signal(alert_group_pk, resolution_note_pk):
    """Sends a signal to update messages associated with resolution note"""
    AlertGroup = apps.get_model("alerts", "AlertGroup")
    ResolutionNote = apps.get_model("alerts", "ResolutionNote")

    alert_group = AlertGroup.unarchived_objects.filter(pk=alert_group_pk).first()
    if alert_group is None:
        print("Sent signal to update resolution note, but alert group is archived or does not exist")
        return

    resolution_note = ResolutionNote.objects_with_deleted.get(pk=resolution_note_pk)

    alert_group_update_resolution_note_signal.send(
        sender=send_update_resolution_note_signal,
        alert_group=alert_group,
        resolution_note=resolution_note,
    )
