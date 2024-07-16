"""
Tests for the Jinja2 tags included in Coop
"""
from django.http.request import QueryDict
from django.template import engines
from django.test import TestCase

from coop.jinja2tags import core
from tests.app.models import TestPage


class TestJinja2Tags(TestCase):
    engine = engines['jinja2']

    def render(self, string, context):
        return self.engine.from_string(string).render(context)

    def test_model_classname(self):
        self.assertEqual(core.model_classname(TestPage), 'page-app-testpage')
        instance = TestPage(title='My page', body='<p>Hello, world!</p>')
        self.assertEqual(core.model_classname(instance), 'page-app-testpage')

    def test_qs(self):
        class request():
            GET = QueryDict('foo=bar')
        ctx = {'request': request}

        # No extra keys should return it unchanged
        self.assertEqual(core.qs(ctx), 'foo=bar')

        # Updating keys
        self.assertEqual(core.qs(ctx, foo='baz'), 'foo=baz')
        self.assertEqual(core.qs(ctx, foo=1), 'foo=1')
        self.assertEqual(core.qs(ctx, foo=None), '')
        self.assertEqual(core.qs(ctx, foo=None, baz='quux'), 'baz=quux')

        # Adding keys
        # Dict order is undefined, so using assertIn with both possibilities
        self.assertIn(core.qs(ctx, baz='quux'),
                      ['foo=bar&baz=quux', 'baz=quux&foo=bar'])
        self.assertEqual(core.qs(ctx, foo=None, baz='quux'), 'baz=quux')

        # Pass in a custom querydict
        self.assertEqual(core.qs({}, QueryDict('new=dict')), 'new=dict')

    def test_tel_filter(self):
        self.assertEqual(core.tel('0361234567'),
                         'tel:0361234567')
        self.assertEqual(core.tel('(03) 6123 4567'),
                         'tel:03-6123-4567')
        self.assertEqual(core.tel('+61 3 6123 4567'),
                         'tel:+61-3-6123-4567')
        self.assertEqual(core.tel('0407 000 111'),
                         'tel:0407-000-111')

    def test_br_filter(self):
        template = '{{ s|br }}'
        self.assertEqual(self.render(template, {'s': 'hello world'}),
                         'hello world')
        self.assertEqual(self.render(template, {'s': 'hello\nworld'}),
                         'hello<br>world')
        self.assertEqual(self.render(template, {'s': 'hello\n\nworld'}),
                         'hello<br><br>world')

    def test_p_filter(self):
        template = '{{ s|p }}'
        self.assertEqual(self.render(template, {'s': 'hello world'}),
                         '<p>hello world</p>')
        self.assertEqual(self.render(template, {'s': 'hello\nworld'}),
                         '<p>hello<br>world</p>')
        self.assertEqual(self.render(template, {'s': 'hello\n\nworld'}),
                         '<p>hello</p>\n\n<p>world</p>')
