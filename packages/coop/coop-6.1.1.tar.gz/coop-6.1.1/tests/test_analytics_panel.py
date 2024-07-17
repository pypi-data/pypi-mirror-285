from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from wagtail.models import Page, Site

from coop.models import AnalyticsSettings


class TestAnalyticsPanel(TestCase):
    def setUp(self):
        super().setUp()
        self.admin = User.objects.create_superuser(
            'admin', 'admin@example.com', 'p')
        self.client.login(username='admin', password='p')

    def make_link(self, site):
        url = reverse('wagtailsettings:edit', args=[
            'coop', 'analyticssettings', site.pk])
        return '<a href="{}">Add your relevant IDs</a>'.format(url)

    def test_no_site(self):
        """
        This used to throw an error if there was no Site, rendering the admin
        useless
        """
        response = self.client.get(reverse('wagtailadmin_home'))
        self.assertEqual(response.status_code, 200)

    def test_analytics_panel_appears(self):
        site = Site.objects.create(
            hostname='example.com',
            root_page=Page.objects.get(pk=1),
            is_default_site=True)

        response = self.client.get(reverse('wagtailadmin_home'))
        self.assertContains(response, self.make_link(site), html=True)

    def test_no_panel(self):
        site = Site.objects.create(
            hostname='example.com',
            root_page=Page.objects.get(pk=1),
            is_default_site=True)

        AnalyticsSettings.objects.create(
            site=site, google_analytics='UA-XXXX-XXXX')

        response = self.client.get(reverse('wagtailadmin_home'))
        self.assertNotContains(response, self.make_link(site), html=True)
