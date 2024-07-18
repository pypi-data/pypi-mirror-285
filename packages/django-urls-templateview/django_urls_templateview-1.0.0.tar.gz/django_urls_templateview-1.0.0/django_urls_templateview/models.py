__all__ = [
    "Map",
]

from django.db import models


class UrlsTemplateView(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=255)
    template_name = models.CharField(max_length=255)

    class Meta:
        db_table = "django_urls_templateview"
        ordering = ("url",)
        unique_together = [
            (
                "url",
                "template_name",
            )
        ]
        verbose_name = "Map"
        verbose_name_plural = "Map"
