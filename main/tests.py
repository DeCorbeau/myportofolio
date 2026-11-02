from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse

from main.models import Experience, Skill

PASSWORD = "pass12345"


class BaseTestCase(TestCase):
    """guest: tanpa login | regular: login biasa | editor: boleh ubah | owner: superuser."""

    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.\nMembuat soal kuis.",
            category="part-time",
            started_at="2007-09-01",
        )
        self.experience.refresh_from_db()
        self.skill = Skill.objects.create(
            name="People Management", category="leadership", proficiency=4,
            impact="gugugaga", context="babycorp",
        )
        self.regular = User.objects.create_user("regular", password=PASSWORD)
        self.editor = User.objects.create_user("editor", password=PASSWORD)
        self.owner = User.objects.create_superuser("owner", password=PASSWORD)

        group = Group.objects.create(name="Editor")
        group.permissions.add(
            Permission.objects.get(codename="change_skill"),
            Permission.objects.get(codename="change_experience"),
        )
        self.editor.groups.add(group)

    def login_as(self, username):
        self.assertTrue(self.client.login(username=username, password=PASSWORD))


class ModelTest(BaseTestCase):
    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertTrue(self.experience.is_ongoing)
        self.assertEqual(
            self.experience.description_points,
            ["Membantu mahasiswa memahami pengembangan web.", "Membuat soal kuis."],
        )
        self.assertTrue(self.experience.date_range_display.endswith("Present"))

    def test_skill_model(self):
        self.assertEqual(str(self.skill), "People Management")
        self.assertEqual(self.skill.proficiency, 4)


class PageTest(BaseTestCase):
    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        self.assertEqual(self.client.get("/halaman-yang-tidak-ada/").status_code, 404)

    def test_experience_page_is_only_a_skeleton(self):
        # Data dimuat JS dari API, jadi HTML tidak boleh memuat datanya
        response = self.client.get(reverse("main:show_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertNotContains(response, self.experience.title)
        for element_id in ("loading", "error", "empty", "experience-list"):
            self.assertContains(response, f'id="{element_id}"')
        self.assertContains(response, reverse("api:experience-list"))

    def test_experience_search_box_is_prefilled_from_query(self):
        response = self.client.get(reverse("main:show_experience"), {"q": "intern"})
        self.assertContains(response, 'value="intern"')

    def test_skill_page_still_renders_with_htmx(self):
        response = self.client.get(reverse("main:show_skill"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.skill.name)

    def test_experience_modals_depend_on_role(self):
        # (add, edit, delete) yang harus muncul untuk tiap peran
        expected = {
            None: (False, False, False),
            "regular": (False, False, False),
            "editor": (False, False, False),            
            "owner": (True, True, True),
        }
        for username, (add, edit, delete) in expected.items():
            self.client.logout()
            if username:
                self.login_as(username)
            response = self.client.get(reverse("main:show_experience"))
            for modal_id, shown in (
                ("add-experience-modal", add),
                ("edit-experience-modal", edit),
                ("delete-experience-modal", delete),
            ):
                if shown:
                    self.assertContains(response, f'id="{modal_id}"', msg_prefix=str(username))
                else:
                    self.assertNotContains(response, f'id="{modal_id}"', msg_prefix=str(username))


class AuthTest(BaseTestCase):
    def test_register_creates_account_and_redirects_to_login(self):
        response = self.client.post(reverse("main:register"), {
            "username": "newuser",
            "password1": "S3cure-pass-987",
            "password2": "S3cure-pass-987",
        })
        self.assertRedirects(response, reverse("main:login"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_sets_last_login_cookie(self):
        response = self.client.post(reverse("main:login"), {
            "username": "regular", "password": PASSWORD,
        })
        self.assertRedirects(response, reverse("main:show_main"))
        self.assertIn("last_login", response.cookies)

    def test_login_wrong_password_shows_error(self):
        response = self.client.post(reverse("main:login"), {
            "username": "regular", "password": "salah",
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_deletes_last_login_cookie(self):
        self.login_as("regular")
        response = self.client.get(reverse("main:logout"))
        self.assertRedirects(response, reverse("main:show_main"))
        self.assertEqual(response.cookies["last_login"].value, "")
        self.assertNotIn("_auth_user_id", self.client.session)