from django.db import models


class Submission(models.Model):
    # Needs UUID
    time = models.DateTimeField(auto_now_add=True, null=True)
    spam_auto = models.BooleanField(
        null=True,
        help_text='Automatic classification as spam/not spam',
    )
    spam = models.BooleanField(
        null=True,
        help_text='Classification as spam/not spam (possibly overridden manually)',
    )
    content = models.TextField()
    confidence = models.SmallIntegerField(
        null=True,
        blank=True,
        help_text='Confidence of automated classification (0-100)',
    )
