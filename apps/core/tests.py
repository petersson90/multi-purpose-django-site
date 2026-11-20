import logging

from django import forms
from django.contrib import messages
from django.contrib.messages.storage.base import Message
from django.template import Context, Template
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

# Create your tests here.
class LoggingInTestsTests(SimpleTestCase):
    def test_assert_logs_works_under_test_settings(self):
        """Regression: test output is silenced via LOGGING, not logging.disable(), so
        assertLogs keeps working in every app's tests."""
        with self.assertLogs('apps.core', level='WARNING') as captured:
            logging.getLogger('apps.core').warning('something happened')
        self.assertEqual(len(captured.output), 1)
        self.assertIn('something happened', captured.output[0])


class SampleForm(forms.Form):
    name = forms.CharField(max_length=5)
    agree = forms.BooleanField()
    colour = forms.ChoiceField(choices=[('r', 'Red'), ('g', 'Green')])


class BootstrapFieldTests(SimpleTestCase):
    def render(self, form):
        template = Template('{% load bootstrap %}{% for f in form %}{{ f|bootstrap_field }}{% endfor %}')
        return template.render(Context({'form': form}))

    def test_widgets_get_matching_bootstrap_classes(self):
        html = self.render(SampleForm())
        self.assertIn('class="form-control"', html)
        self.assertIn('class="form-check-input"', html)
        self.assertIn('class="form-select"', html)

    def test_invalid_fields_are_marked(self):
        html = self.render(SampleForm({'name': 'far too long', 'colour': 'r'}))
        self.assertIn('form-control is-invalid', html)
        self.assertIn('form-check-input is-invalid', html)
        self.assertNotIn('form-select is-invalid', html)

    def test_existing_widget_classes_are_kept(self):
        class Form(forms.Form):
            name = forms.CharField(widget=forms.TextInput(attrs={'class': 'mine'}))

        self.assertIn('class="mine form-control"', self.render(Form()))


class LayoutTests(TestCase):
    def test_pages_load_bootstrap_from_static_files(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'vendor/bootstrap/css/bootstrap.min.css')
        self.assertContains(response, 'vendor/bootstrap/js/bootstrap.bundle.min.js')

    def test_login_form_is_rendered_with_bootstrap_classes(self):
        response = self.client.get(reverse('login'))
        self.assertContains(response, 'class="form-control"', count=2)  # email, password

    def test_login_error_is_shown_on_the_form(self):
        response = self.client.post(reverse('login'), {'username': 'no@example.com', 'password': 'x'})
        self.assertContains(response, 'alert alert-danger')

    def test_message_tags_map_to_bootstrap_alert_classes(self):
        self.assertEqual(Message(messages.ERROR, 'x').level_tag, 'danger')
        self.assertEqual(Message(messages.SUCCESS, 'x').level_tag, 'success')
