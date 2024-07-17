from django.contrib import admin

from .models import Submission


def content_prefix(obj):
    return obj.content[:150].replace('\n', ' ')


content_prefix.short_description = 'Content'  # type: ignore


def mark_as_spam(modeladmin, request, queryset):
    queryset.update(spam=True)


def mark_as_not_spam(modeladmin, request, queryset):
    queryset.update(spam=False)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'time', 'spam_auto', 'confidence', 'spam', content_prefix]
    actions = [mark_as_spam, mark_as_not_spam]
    list_filter = ['spam_auto', 'spam']
