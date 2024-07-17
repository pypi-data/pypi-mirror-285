from django.test import TestCase
from wagtail.models import Page, Site

from coop.test import TestThingsWithContentMixin, TestThingsWithoutContentMixin
from tests.app.models import TestPage


class TestContentThings(TestThingsWithContentMixin, TestCase):
    def setUp(self):
        super().setUp()
        root_page = Page.objects.get(pk=1)
        self.home = root_page.add_child(instance=TestPage(
            title='Home',
            body='<p>Home</p>',
        ))
        self.site = Site.objects.create(
            root_page=self.home,
            hostname='localhost',
            is_default_site=True,
        )


class TestOtherThings(TestThingsWithoutContentMixin, TestCase):
    pass
