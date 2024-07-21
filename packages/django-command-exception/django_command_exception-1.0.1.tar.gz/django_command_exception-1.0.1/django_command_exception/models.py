__all__ = [
    "CommandException",
]

import sys
import time
from django.db import models

class CommandException(models.Model):
    id = models.AutoField(primary_key=True)
    command = models.CharField(max_length=255)
    exc_class = models.CharField(max_length=255, verbose_name="Class")
    exc_message = models.TextField(verbose_name="Message")
    exc_traceback = models.TextField(verbose_name="Traceback")
    created_at = models.IntegerField()

    class Meta:
        db_table = "django_command_exception"
        ordering = ("-created_at",'id')
        verbose_name = "Exception"
        verbose_name_plural = "Exceptions"

    def save(self, *args, **kwargs):
        exc_class, exc_message, exc_traceback = sys.exc_info()
        self.exc_class = self.exc_class or exc_class
        self.exc_message = self.exc_message or exc_message
        self.exc_traceback = self.exc_traceback or exc_traceback
        if not self.created_at:
            self.created_at = int(time.time())
        super().save(*args, **kwargs)
