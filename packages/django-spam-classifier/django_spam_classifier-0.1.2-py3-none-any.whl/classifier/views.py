from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from classifier.models import Submission


def classify(request, submission_id, spam_status):
    submission = get_object_or_404(Submission, id=submission_id)
    submission.spam = spam_status == 'spam'
    submission.save()
    return HttpResponse('Thanks!')
