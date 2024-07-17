from django.http import Http404
from django.test import RequestFactory, TestCase

from classifier import views


class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_details(self):
        request = self.factory.get('/')
        with self.assertRaises(Http404):
            views.classify(request, 999, 'spam')
