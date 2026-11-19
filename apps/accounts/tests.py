from django.db import IntegrityError, transaction
from django.test import TestCase

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


class ProfileTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('anna@example.com', PASSWORD)


    def test_profile_created_with_user(self):
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
        self.assertEqual(self.user.profile.name, 'anna@example.com')


    def test_display_name_wins(self):
        self.user.profile.display_name = 'Anna A.'
        self.assertEqual(self.user.profile.name, 'Anna A.')
