import os
import tempfile

from django.core.management.base import BaseCommand

from ...models import Submission
from ...classify import add_manual_labels, learn


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Problem is that each call to learn() overwrites the existing database,
        # so need to write out all the samples to disk.
        with tempfile.TemporaryDirectory() as spam_dir:
            for i, sample in enumerate(Submission.objects.filter(spam=True)):
                with open(os.path.join(spam_dir, str(i)), 'wb') as f:
                    labelled_content = add_manual_labels(sample.content)
                    f.write(labelled_content.encode('utf-8'))
            learn(spam_dir, spam=True)
        with tempfile.TemporaryDirectory() as ham_dir:
            for i, sample in enumerate(Submission.objects.filter(spam=False)):
                with open(os.path.join(ham_dir, str(i)), 'wb') as f:
                    labelled_content = add_manual_labels(sample.content)
                    f.write(labelled_content.encode('utf-8'))
            learn(ham_dir, spam=False)
