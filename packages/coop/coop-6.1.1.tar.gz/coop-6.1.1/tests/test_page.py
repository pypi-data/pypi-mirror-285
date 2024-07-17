"""
Tests for the Jinja2 tags included in Coop
"""
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils.form_data import rich_text

from tests.app.models import TestPage


class TestPageModel(WagtailPageTestCase):
    def setUp(self):
        super().setUp()
        self.root_page = Page.objects.get(pk=1)

        self.page = self.root_page.add_child(
            instance=TestPage(title="Test page", body="<p>Hello, world!</p>")
        )
        self.login()

    def test_get_template(self):
        """
        Check that the custom ``get_template`` method returns sensible things
        """
        self.assertEqual(self.page.get_template(None), "layouts/app/test_page.html")

    def test_create_without_show_in_menus(self):
        """
        Check that a page can still be created without sending anything for
        ``show_in_menus``, which has been removed from coop sites in favour of
        a menu builder.
        """
        self.assertCanCreate(
            self.root_page,
            TestPage,
            {
                "title": "Creation test",
                "body": rich_text("<p>Hello, world!</p>"),
                "slug": "creation-test",
            },
        )
