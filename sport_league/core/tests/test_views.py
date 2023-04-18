# Django Imports
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from django.test import TestCase, Client

# App Imports
from core.forms import CustomUserCreationForm
from core.models import User, Team, Game
from core.views import SigninView


class SignupViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse("core:sign_up")
        self.user_data = {
            "email": "test@gmail.com",
            "password1": "QAZ123zaq321?",
            "password2": "QAZ123zaq321?",
        }
        self.invalid_user_data = {
            "email": "test@gmail.com",
            "password1": "password",
            "password2": "wrong_password",
        }

    def test_signup_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/sign_up.html")
        self.assertIsInstance(response.context["form"], CustomUserCreationForm)

    def test_signup_view_valid_post(self):
        response = self.client.post(self.url, data=self.user_data)
        self.assertRedirects(response, reverse("core:home"))
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().email, self.user_data["email"])

    def test_signup_view_invalid_post(self):
        response = self.client.post(self.url, data=self.invalid_user_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/sign_up.html")
        self.assertIsInstance(response.context["form"], CustomUserCreationForm)


class SigninViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse("core:sign_in")
        self.user_data = {
            "username": "test@gmail.com",
            "password": "QAZ123zaq321?",
        }
        self.invalid_user_data = {
            "username": "test@gmail.com",
            "password": "wrong_password",
        }
        self.user = User.objects.create_user(
            email="test@gmail.com", password="QAZ123zaq321?"
        )

    def test_signin_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/sign_in.html")
        self.assertIsInstance(response.context["form"], AuthenticationForm)

    def test_signin_view_valid_data(self):
        response = self.client.post(self.url, data=self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("core:home"))

    def test_signin_view_invalid_post(self):
        response = self.client.post(self.url, data=self.invalid_user_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/sign_in.html")
        self.assertIsInstance(response.context["form"], AuthenticationForm)


class LogoutViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.logout_url = reverse("core:log_out")
        self.user = User.objects.create_user(
            email="test@gmail.com",
            password="QAZ123zaq321?"
        )

    def test_redirects_to_signup_view(self):
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, reverse("core:sign_up"))

    def test_logs_out_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("core:sign_up"))


class UploadCSVViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("core:upload_csv")
        self.user = User.objects.create_user(email="test@gmail.com", password="QAZ123zaq321?")
        data = b"Team A,2,Team B,1\nTeam C,3,Team D,1\n"
        self.csv_file = SimpleUploadedFile("test.csv", data, content_type="text/csv")

    def tearDown(self):
        self.user.delete()

    def test_upload_csv_view_get(self):
        self.client.login(username="test@gmail.com", password="QAZ123zaq321?")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/upload_csv.html")

    def test_upload_csv_view_valid_file(self):
        self.client.login(username="test@gmail.com", password="QAZ123zaq321?")
        response = self.client.post(self.url, {"csv_file": self.csv_file})
        self.assertEqual(response.status_code, 302)

    def test_upload_csv_view_invalid_file(self):
        self.client.login(username="test@gmail.com", password="QAZ123zaq321?")
        response = self.client.post(self.url, {"csv_file": SimpleUploadedFile("test.txt", b"test data")})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/upload_csv.html")

    def test_upload_csv_view_no_file(self):
        self.client.login(username="test@gmail.com", password="QAZ123zaq321?")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/upload_csv.html")


class HomeViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("core:home")

    def test_home_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/main.html")
