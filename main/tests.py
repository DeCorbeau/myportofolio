from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import Group, Permission, User
from main.models import Experience
from main.models import Skill


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
            started_at="2007-09-01",
        )
        self.experience.refresh_from_db()
        self.skill = Skill.objects.create(
            name="People Management",
            category='leadership',
            proficiency=4,
            impact='gugugaga',
            context='babycorp'
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Present")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, self.experience.date_range_display)
        self.assertNotContains(response, "Present")

    def test_skill_model(self):
        self.assertEqual(str(self.skill), "People Management")
        self.assertEqual(self.skill.category, "leadership")
        self.assertEqual(self.skill.proficiency, 4)

    def test_skill_page(self):
        response = self.client.get(reverse("main:show_skill"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "skill.html")
        self.assertContains(response, self.skill.name)
        self.assertContains(response, "Leadership &amp; Management")
        self.assertContains(response, "Expert")
        self.assertContains(response, "gugugaga")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_skill_page(self):
        Skill.objects.all().delete()
        response = self.client.get(reverse("main:show_skill"))

        self.assertContains(response, "Belum ada skill yang ditambahkan.")

class RolePermissionTest(TestCase):
    def setUp(self):
        self.skill = Skill.objects.create(
            name="Test Skill", category="technical", proficiency=1
        )
        self.regular = User.objects.create_user("regular", password="pass12345")
        self.editor = User.objects.create_user("editor", password="pass12345")
        self.owner = User.objects.create_superuser("owner", password="pass12345")

        editor_group = Group.objects.create(name="Editor")
        editor_group.permissions.add(Permission.objects.get(codename="change_skill"))
        self.editor.groups.add(editor_group)

    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get(reverse("main:create_skill"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_regular_user_gets_403_on_edit(self):
        self.client.login(username="regular", password="pass12345")
        response = self.client.get(reverse("main:update_skill", args=[self.skill.id]))
        self.assertEqual(response.status_code, 403)

    def test_editor_can_edit_but_not_create_or_delete(self):
        self.client.login(username="editor", password="pass12345")
        edit = self.client.get(reverse("main:update_skill", args=[self.skill.id]))
        create = self.client.get(reverse("main:create_skill"))
        delete = self.client.post(reverse("main:delete_skill", args=[self.skill.id]))
        self.assertEqual(edit.status_code, 200)
        self.assertEqual(create.status_code, 403)
        self.assertEqual(delete.status_code, 403)

    def test_superuser_can_create(self):
        self.client.login(username="owner", password="pass12345")
        response = self.client.get(reverse("main:create_skill"))
        self.assertEqual(response.status_code, 200)

    def test_endorse_toggles_on_and_off(self):
        self.client.login(username="regular", password="pass12345")
        url = reverse("main:toggle_endorse", args=[self.skill.id])
        self.client.post(url)
        self.assertEqual(self.skill.endorsed_by.count(), 1)
        self.client.post(url)
        self.assertEqual(self.skill.endorsed_by.count(), 0)

class ExperienceAndAuthTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Test Exp", description="a\nb", started_at="2025-01-01"
        )
        self.skill = Skill.objects.create(
            name="Python", category="technical", proficiency=2
        )
        self.regular = User.objects.create_user("regular", password="pass12345")
        self.exp_editor = User.objects.create_user("expeditor", password="pass12345")
        self.owner = User.objects.create_superuser("owner", password="pass12345")

        group = Group.objects.create(name="ExpEditor")
        group.permissions.add(Permission.objects.get(codename="change_experience"))
        self.exp_editor.groups.add(group)

    # --- Experience permissions ---
    def test_experience_editor_can_edit_but_not_create_or_delete(self):
        self.client.login(username="expeditor", password="pass12345")
        edit = self.client.get(reverse("main:update_experience", args=[self.experience.id]))
        create = self.client.get(reverse("main:create_experience"))
        delete = self.client.post(reverse("main:delete_experience", args=[self.experience.id]))
        self.assertEqual(edit.status_code, 200)
        self.assertEqual(create.status_code, 403)
        self.assertEqual(delete.status_code, 403)

    def test_regular_user_gets_403_on_experience_edit(self):
        self.client.login(username="regular", password="pass12345")
        response = self.client.get(reverse("main:update_experience", args=[self.experience.id]))
        self.assertEqual(response.status_code, 403)

    def test_superuser_can_delete_experience(self):
        self.client.login(username="owner", password="pass12345")
        self.client.post(reverse("main:delete_experience", args=[self.experience.id]))
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())

    # --- Like ---
    def test_like_toggles_and_requires_login(self):
        url = reverse("main:toggle_like", args=[self.experience.id])
        anon = self.client.post(url)
        self.assertEqual(anon.status_code, 302)
        self.assertIn("/login/", anon.url)

        self.client.login(username="regular", password="pass12345")
        self.client.post(url)
        self.assertEqual(self.experience.liked_by.count(), 1)
        self.client.post(url)
        self.assertEqual(self.experience.liked_by.count(), 0)

    # --- JSON API ---
    def test_skill_json_filter_by_name(self):
        Skill.objects.create(name="Public Speaking", category="communication", proficiency=3)
        response = self.client.get(reverse("main:get_skill_json"), {"name": "python"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertContains(response, "Python")
        self.assertNotContains(response, "Public Speaking")

    def test_skill_json_uses_usernames_not_ids(self):
        self.skill.endorsed_by.add(self.regular)
        response = self.client.get(reverse("main:get_skill_json"))
        self.assertContains(response, "regular")

    def test_experience_json(self):
        response = self.client.get(reverse("main:get_experience_json"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Exp")

    # --- Auth & cookie ---
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
            "username": "regular", "password": "pass12345",
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
        self.client.login(username="regular", password="pass12345")
        response = self.client.get(reverse("main:logout"))
        self.assertRedirects(response, reverse("main:show_main"))
        self.assertEqual(response.cookies["last_login"].value, "")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_skill_page_search(self):
        Skill.objects.create(name="Public Speaking", category="communication", proficiency=3)
        response = self.client.get(reverse("main:show_skill"), {"name": "python"})
        self.assertContains(response, "Python")
        self.assertNotContains(response, "Public Speaking")            