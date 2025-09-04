from django.db import models

class EventoZK(models.Model):
    event_id = models.BigIntegerField(unique=True)
    terminal_sn = models.CharField(max_length=64, db_index=True)
    codigo = models.CharField(max_length=32, db_index=True)
    event_time = models.DateTimeField(db_index=True)
    area_alias = models.CharField(max_length=128, blank=True)
    upload_time = models.DateTimeField(null=True, blank=True)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_id} | {self.codigo} @ {self.event_time} ({self.terminal_sn})"

