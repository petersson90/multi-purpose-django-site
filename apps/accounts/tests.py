from django.db import IntegrityError, transaction
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.views.defaults import server_error

from .models import Profile, User

PASSWORD = 'a-long-unique-pass-9'

# Create your tests here.
class UserModelTests(TestCase):
    def test_create_user_lowercases_email(self):
        user = User.objects.create_user('Anna@Example.COM', PASSWORD)
        self.assertEqual(user.email, 'anna@example.com')

    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user('', PASSWORD)

    def test_create_superuser(self):
        user = User.objects.create_superuser('root@example.com', PASSWORD)
        self.assertTrue(user.is_staff and user.is_superuser)


class EmailUniquenessTests(TestCase):
    """The case-insensitive guarantee must hold in the database, not only in save()."""

    def setUp(self):
        self.anna = User.objects.create_user('anna@example.com', PASSWORD)

    def test_exact_duplicate_rejected(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user('anna@example.com', PASSWORD)

    def test_save_normalises_case_before_checking(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user('ANNA@Example.com', PASSWORD)

    def test_database_rejects_different_case_when_save_is_bypassed(self):
        # bulk_create() skips User.save(), so the lowercasing there does not run.
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.bulk_create([User(email='Anna@Example.com')])

    def test_database_rejects_case_change_via_queryset_update(self):
        other = User.objects.create_user('bo@example.com', PASSWORD)
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.filter(pk=other.pk).update(email='ANNA@example.com')


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('anna@example.com', PASSWORD)

    def test_login_with_email(self):
        response = self.client.post(
            reverse('login'), {'username': 'anna@example.com', 'password': PASSWORD}
        )
        self.assertRedirects(response, reverse('accounts:profile'))

    def test_login_email_is_case_insensitive(self):
        response = self.client.post(
            reverse('login'), {'username': 'ANNA@Example.com', 'password': PASSWORD}
        )
        self.assertRedirects(response, reverse('accounts:profile'))

    def test_wrong_password_rejected(self):
        response = self.client.post(
            reverse('login'), {'username': 'anna@example.com', 'password': 'wrong-password-1'}
        )
        self.assertEqual(response.status_code, 200)


class NoSignupTests(TestCase):
    def test_no_signup_page(self):
        self.assertEqual(self.client.get('/accounts/signup/').status_code, 404)

    def test_pages_do_not_advertise_signup(self):
        for url in (reverse('home'), reverse('login')):
            self.assertNotContains(self.client.get(url), 'signup')


class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('anna@example.com', PASSWORD)

    def test_profile_created_with_user(self):
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
        self.assertEqual(self.user.profile.name, 'anna@example.com')

    def test_display_name_wins(self):
        self.user.profile.display_name = 'Anna A.'
        self.assertEqual(self.user.profile.name, 'Anna A.')

    def test_profile_requires_login(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_profile_pages_render(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('accounts:profile')).status_code, 200)
        self.assertEqual(self.client.get(reverse('accounts:profile_edit')).status_code, 200)

    def test_edit_profile(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('accounts:profile_edit'),
            {'display_name': 'Anna', 'bio': 'Hej', 'phone_number': '070-000 00 00'},
        )
        self.assertRedirects(response, reverse('accounts:profile'))
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.display_name, 'Anna')

    def test_home_renders(self):
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)


class AdminTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser('root@example.com', PASSWORD)
        self.client.force_login(self.admin_user)

    def test_admin_can_add_user_with_profile(self):
        url = reverse('admin:accounts_user_add')
        self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.post(
            url,
            {
                'email': 'New@Example.com',
                'usable_password': 'true',
                'password1': PASSWORD,
                'password2': PASSWORD,
            },
        )
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(email='new@example.com')
        self.assertTrue(Profile.objects.filter(user=new_user).exists())
        change_url = reverse('admin:accounts_user_change', args=[new_user.pk])
        self.assertEqual(self.client.get(change_url).status_code, 200)

    def test_admin_rejects_duplicate_email_in_any_case(self):
        response = self.client.post(
            reverse('admin:accounts_user_add'),
            {
                'email': 'ROOT@example.com',
                'usable_password': 'true',
                'password1': PASSWORD,
                'password2': PASSWORD,
            },
        )
        self.assertEqual(response.status_code, 200)  # form re-rendered with an error
        self.assertEqual(User.objects.count(), 1)


class ErrorPageTests(TestCase):
    @override_settings(DEBUG=False)
    def test_404_uses_site_layout(self):
        response = self.client.get('/no-such-page/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'Page not found', status_code=404)
        self.assertContains(response, 'navbar', status_code=404)

    def test_500_is_standalone(self):
        response = server_error(RequestFactory().get('/'))
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Something went wrong', response.content)
        self.assertNotIn(b'navbar', response.content)
