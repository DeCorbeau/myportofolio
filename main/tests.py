import uuid

from django.contrib.auth.models import Group, Permission, User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Skill

PASSWORD = "pass12345"


class BaseTestCase(TestCase):
    """Shared fixtures: one experience, one skill, and four kinds of visitors.

    guest   -> not logged in (self.client without login)
    regular -> logged in, no extra permission
    editor  -> may change experience/skill, but not create or delete
    owner   -> superuser, may do everything
    """

    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.\nMembuat soal kuis.",
            category="part-time",
            started_at="2007-09-01",
        )
        self.experience.refresh_from_db()
        self.skill = Skill.objects.create(
            name="People Management",
            category="leadership",
            proficiency=4,
            impact="gugugaga",
            context="babycorp",
        )

        self.regular = User.objects.create_user("regular", password=PASSWORD)
        self.editor = User.objects.create_user("editor", password=PASSWORD)
        self.owner = User.objects.create_superuser("owner", password=PASSWORD)

        editor_group = Group.objects.create(name="Editor")
        editor_group.permissions.add(
            Permission.objects.get(codename="change_skill"),
            Permission.objects.get(codename="change_experience"),
        )
        self.editor.groups.add(editor_group)

    def login_as(self, username):
        self.assertTrue(self.client.login(username=username, password=PASSWORD))

    # Valid form data, reused by the create/update tests
    def experience_payload(self, **overrides):
        data = {
            "title": "Committee Member",
            "organization": "Open House",
            "description": "Led the ambassador division.\nTrained 8 members.",
            "category": "committee",
            "thumbnail": "",
            "started_at": "2025-01-01",
            "ended_at": "",
        }
        data.update(overrides)
        return data

    def skill_payload(self, **overrides):
        data = {
            "name": "Public Speaking",
            "category": "communication",
            "proficiency": "3",
            "impact": "Spoke at 5 events",
            "context": "Open House 2026",
        }
        data.update(overrides)
        return data


# ---------------------------------------------------------------------------
# Models and plain pages
# ---------------------------------------------------------------------------
class ModelTest(BaseTestCase):
    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)
        self.assertEqual(
            self.experience.description_points,
            ["Membantu mahasiswa memahami pengembangan web.", "Membuat soal kuis."],
        )

    def test_skill_model(self):
        self.assertEqual(str(self.skill), "People Management")
        self.assertEqual(self.skill.category, "leadership")
        self.assertEqual(self.skill.proficiency, 4)


class PageTest(BaseTestCase):
    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")
        self.assertEqual(response.status_code, 404)

    def test_experience_page_is_only_a_skeleton(self):
        # Data is loaded by JavaScript, so the HTML must not contain it
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, 'id="loading"')
        self.assertContains(response, 'id="error"')
        self.assertContains(response, 'id="empty"')
        self.assertContains(response, 'id="experience-list"')
        self.assertContains(response, reverse("main:get_experience_json"))
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_skill_page_is_only_a_skeleton(self):
        response = self.client.get(reverse("main:show_skill"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "skill.html")
        self.assertNotContains(response, self.skill.name)
        self.assertContains(response, 'id="loading"')
        self.assertContains(response, 'id="error"')
        self.assertContains(response, 'id="empty"')
        self.assertContains(response, 'id="skill-list"')
        self.assertContains(response, reverse("main:get_skill_json"))
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_search_boxes_are_prefilled_from_query(self):
        skill_page = self.client.get(reverse("main:show_skill"), {"name": "python"})
        experience_page = self.client.get(reverse("main:show_experience"), {"q": "intern"})

        self.assertContains(skill_page, 'value="python"')
        self.assertContains(experience_page, 'value="intern"')

    def test_add_modals_are_only_rendered_for_superuser(self):
        guest_exp = self.client.get(reverse("main:show_experience"))
        guest_skill = self.client.get(reverse("main:show_skill"))
        self.assertNotContains(guest_exp, 'id="add-experience-modal"')
        self.assertNotContains(guest_skill, 'id="add-skill-modal"')

        self.login_as("regular")
        regular_exp = self.client.get(reverse("main:show_experience"))
        self.assertNotContains(regular_exp, 'id="add-experience-modal"')

        self.login_as("owner")
        owner_exp = self.client.get(reverse("main:show_experience"))
        owner_skill = self.client.get(reverse("main:show_skill"))
        self.assertContains(owner_exp, 'id="add-experience-modal"')
        self.assertContains(owner_exp, 'id="delete-experience-modal"')
        self.assertContains(owner_skill, 'id="add-skill-modal"')
        self.assertContains(owner_skill, 'id="delete-skill-modal"')


# ---------------------------------------------------------------------------
# JSON endpoints (the data the pages load with fetch())
# ---------------------------------------------------------------------------
class ExperienceJsonTest(BaseTestCase):
    def get_json(self, **params):
        response = self.client.get(reverse("main:get_experience_json"), params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        return response.json()

    def test_experience_json_shape(self):
        data = self.get_json()

        self.assertEqual(len(data), 1)
        item = data[0]
        self.assertEqual(item["pk"], str(self.experience.id))
        fields = item["fields"]
        self.assertEqual(fields["title"], "Asisten Dosen PBP")
        self.assertEqual(fields["category_display"], "Part-Time")
        self.assertEqual(fields["date_range"], self.experience.date_range_display)
        self.assertTrue(fields["date_range"].endswith("Present"))
        self.assertEqual(fields["description_points"], self.experience.description_points)
        self.assertEqual(fields["like_count"], 0)
        self.assertFalse(fields["is_liked"])

    def test_completed_experience_has_no_present(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        self.experience.refresh_from_db()

        fields = self.get_json()[0]["fields"]
        self.assertFalse(self.experience.is_ongoing)
        self.assertEqual(fields["date_range"], self.experience.date_range_display)
        self.assertNotIn("Present", fields["date_range"])

    def test_empty_experience_json(self):
        Experience.objects.all().delete()
        self.assertEqual(self.get_json(), [])

    def test_experience_json_search_by_title_and_organization(self):
        Experience.objects.create(
            title="Backend Intern", organization="Acme Corp",
            description="x", started_at="2025-01-01",
        )
        by_title = self.get_json(q="asisten")
        by_org = self.get_json(q="acme")
        no_match = self.get_json(q="zzz")

        self.assertEqual([i["fields"]["title"] for i in by_title], ["Asisten Dosen PBP"])
        self.assertEqual([i["fields"]["title"] for i in by_org], ["Backend Intern"])
        self.assertEqual(no_match, [])

    def test_experience_json_like_state_is_per_user(self):
        self.experience.liked_by.add(self.regular)

        guest = self.get_json()[0]["fields"]
        self.assertEqual(guest["like_count"], 1)
        self.assertFalse(guest["is_liked"])
        self.assertEqual(guest["liked_by_names"], "regular")

        self.login_as("regular")
        mine = self.get_json()[0]["fields"]
        self.assertTrue(mine["is_liked"])

        self.login_as("owner")
        other = self.get_json()[0]["fields"]
        self.assertFalse(other["is_liked"])


class SkillJsonTest(BaseTestCase):
    def get_json(self, **params):
        response = self.client.get(reverse("main:get_skill_json"), params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        return response.json()

    def test_skill_json_shape(self):
        data = self.get_json()

        self.assertEqual(len(data), 1)
        item = data[0]
        self.assertEqual(item["pk"], str(self.skill.id))
        fields = item["fields"]
        self.assertEqual(fields["name"], "People Management")
        self.assertEqual(fields["category"], "leadership")
        self.assertEqual(fields["category_display"], "Leadership & Management")
        self.assertEqual(fields["proficiency"], 4)
        self.assertEqual(fields["proficiency_display"], "Expert")
        self.assertEqual(fields["impact"], "gugugaga")
        self.assertEqual(fields["context"], "babycorp")
        self.assertEqual(fields["endorse_count"], 0)
        self.assertFalse(fields["is_endorsed"])

    def test_empty_skill_json(self):
        Skill.objects.all().delete()
        self.assertEqual(self.get_json(), [])

    def test_skill_json_filter_by_name(self):
        Skill.objects.create(name="Python", category="technical", proficiency=2)
        Skill.objects.create(name="Public Speaking", category="communication", proficiency=3)

        names = [i["fields"]["name"] for i in self.get_json(name="python")]
        self.assertEqual(names, ["Python"])
        self.assertEqual(self.get_json(name="zzz"), [])

    def test_skills_are_sorted_by_category_order(self):
        # Created in a "wrong" order on purpose; the API must group them
        Skill.objects.create(name="Python", category="technical", proficiency=2)
        Skill.objects.create(name="Event Planning", category="event", proficiency=3)

        names = [i["fields"]["name"] for i in self.get_json()]
        self.assertEqual(names, ["People Management", "Event Planning", "Python"])

    def test_skill_json_uses_usernames_not_ids(self):
        self.skill.endorsed_by.add(self.regular)

        fields = self.get_json()[0]["fields"]
        self.assertEqual(fields["endorse_count"], 1)
        self.assertEqual(fields["endorsed_by_names"], "regular")

    def test_skill_json_endorse_state_is_per_user(self):
        self.skill.endorsed_by.add(self.regular)

        self.assertFalse(self.get_json()[0]["fields"]["is_endorsed"])
        self.login_as("regular")
        self.assertTrue(self.get_json()[0]["fields"]["is_endorsed"])
        self.login_as("owner")
        self.assertFalse(self.get_json()[0]["fields"]["is_endorsed"])


# ---------------------------------------------------------------------------
# Add via AJAX (modal): 201 / 400 / 403, CSRF, XSS protection
# ---------------------------------------------------------------------------
class CreateExperienceAjaxTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("main:create_experience_ajax")

    def test_guest_gets_403_json_not_a_redirect(self):
        response = self.client.post(self.url, self.experience_payload())

        self.assertEqual(response.status_code, 403)
        self.assertIn("message", response.json())
        self.assertEqual(Experience.objects.count(), 1)

    def test_regular_user_and_editor_get_403(self):
        for username in ("regular", "editor"):
            self.login_as(username)
            response = self.client.post(self.url, self.experience_payload())
            self.assertEqual(response.status_code, 403, username)
        self.assertEqual(Experience.objects.count(), 1)

    def test_get_is_not_allowed(self):
        self.login_as("owner")
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_superuser_creates_experience_with_201(self):
        self.login_as("owner")
        response = self.client.post(self.url, self.experience_payload())

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertIn("message", body)
        created = Experience.objects.get(pk=body["pk"])
        self.assertEqual(created.title, "Committee Member")
        self.assertEqual(created.category, "committee")

    def test_invalid_data_returns_400_with_field_errors(self):
        self.login_as("owner")
        response = self.client.post(self.url, self.experience_payload(title="", category="nope"))

        self.assertEqual(response.status_code, 400)
        errors = response.json()["errors"]
        self.assertIn("title", errors)
        self.assertIn("category", errors)
        self.assertEqual(Experience.objects.count(), 1)

    def test_end_date_before_start_date_is_rejected(self):
        self.login_as("owner")
        response = self.client.post(
            self.url, self.experience_payload(started_at="2025-01-01", ended_at="2024-01-01")
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("ended_at", response.json()["errors"])

    def test_end_date_after_start_date_is_accepted(self):
        self.login_as("owner")
        response = self.client.post(
            self.url, self.experience_payload(started_at="2025-01-01", ended_at="2025-06-01")
        )
        self.assertEqual(response.status_code, 201)

    def test_html_tags_are_stripped_on_the_server(self):
        self.login_as("owner")
        response = self.client.post(self.url, self.experience_payload(
            title='<img src="x" onerror="alert(1)">Hacker',
            organization="<b>Org</b>",
            description="<script>alert(1)</script>\nSecond line",
        ))

        self.assertEqual(response.status_code, 201)
        created = Experience.objects.get(pk=response.json()["pk"])
        for value in (created.title, created.organization, created.description):
            self.assertNotIn("<", value)
            self.assertNotIn(">", value)
        self.assertNotIn("onerror", created.title)
        self.assertEqual(created.organization, "Org")

    def test_title_made_only_of_tags_is_rejected(self):
        self.login_as("owner")
        response = self.client.post(self.url, self.experience_payload(title="<b></b>"))

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])

    def test_post_without_csrf_token_is_rejected(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.login(username="owner", password=PASSWORD)

        response = csrf_client.post(self.url, self.experience_payload())

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)


class CreateSkillAjaxTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("main:create_skill_ajax")

    def test_guest_gets_403_json_not_a_redirect(self):
        response = self.client.post(self.url, self.skill_payload())

        self.assertEqual(response.status_code, 403)
        self.assertIn("message", response.json())
        self.assertEqual(Skill.objects.count(), 1)

    def test_regular_user_and_editor_get_403(self):
        for username in ("regular", "editor"):
            self.login_as(username)
            response = self.client.post(self.url, self.skill_payload())
            self.assertEqual(response.status_code, 403, username)
        self.assertEqual(Skill.objects.count(), 1)

    def test_get_is_not_allowed(self):
        self.login_as("owner")
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_superuser_creates_skill_with_201(self):
        self.login_as("owner")
        response = self.client.post(self.url, self.skill_payload())

        self.assertEqual(response.status_code, 201)
        created = Skill.objects.get(pk=response.json()["pk"])
        self.assertEqual(created.name, "Public Speaking")
        self.assertEqual(created.proficiency, 3)

    def test_invalid_data_returns_400_with_field_errors(self):
        self.login_as("owner")
        response = self.client.post(self.url, self.skill_payload(name="", category="nope"))

        self.assertEqual(response.status_code, 400)
        errors = response.json()["errors"]
        self.assertIn("name", errors)
        self.assertIn("category", errors)
        self.assertEqual(Skill.objects.count(), 1)

    def test_html_tags_are_stripped_on_the_server(self):
        self.login_as("owner")
        response = self.client.post(self.url, self.skill_payload(
            name="<b>Python</b>",
            impact='<img src="x" onerror="alert(1)">Shipped it',
            context="<i>Class</i> project",
        ))

        self.assertEqual(response.status_code, 201)
        created = Skill.objects.get(pk=response.json()["pk"])
        self.assertEqual(created.name, "Python")
        self.assertEqual(created.context, "Class project")
        self.assertNotIn("<", created.impact)
        self.assertNotIn("onerror", created.impact)

    def test_name_made_only_of_tags_is_rejected(self):
        self.login_as("owner")
        response = self.client.post(self.url, self.skill_payload(name="<b></b>"))

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.json()["errors"])

    def test_post_without_csrf_token_is_rejected(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.login(username="owner", password=PASSWORD)

        response = csrf_client.post(self.url, self.skill_payload())

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Skill.objects.count(), 1)


# ---------------------------------------------------------------------------
# Delete via AJAX
# ---------------------------------------------------------------------------
class DeleteAjaxTest(BaseTestCase):
    def test_experience_delete_requires_superuser(self):
        url = reverse("main:delete_experience_ajax", args=[self.experience.id])

        self.assertEqual(self.client.post(url).status_code, 403)  # guest
        for username in ("regular", "editor"):
            self.login_as(username)
            self.assertEqual(self.client.post(url).status_code, 403, username)
        self.assertTrue(Experience.objects.filter(pk=self.experience.id).exists())

    def test_superuser_can_delete_experience(self):
        self.login_as("owner")
        url = reverse("main:delete_experience_ajax", args=[self.experience.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())

    def test_delete_unknown_experience_returns_404_json(self):
        self.login_as("owner")
        url = reverse("main:delete_experience_ajax", args=[uuid.uuid4()])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.assertIn("message", response.json())

    def test_experience_delete_rejects_get(self):
        self.login_as("owner")
        url = reverse("main:delete_experience_ajax", args=[self.experience.id])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertTrue(Experience.objects.filter(pk=self.experience.id).exists())

    def test_skill_delete_requires_superuser(self):
        url = reverse("main:delete_skill_ajax", args=[self.skill.id])

        self.assertEqual(self.client.post(url).status_code, 403)  # guest
        for username in ("regular", "editor"):
            self.login_as(username)
            self.assertEqual(self.client.post(url).status_code, 403, username)
        self.assertTrue(Skill.objects.filter(pk=self.skill.id).exists())

    def test_superuser_can_delete_skill(self):
        self.login_as("owner")
        url = reverse("main:delete_skill_ajax", args=[self.skill.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Skill.objects.filter(pk=self.skill.id).exists())

    def test_delete_unknown_skill_returns_404_json(self):
        self.login_as("owner")
        url = reverse("main:delete_skill_ajax", args=[uuid.uuid4()])
        self.assertEqual(self.client.post(url).status_code, 404)

    def test_skill_delete_rejects_get(self):
        self.login_as("owner")
        url = reverse("main:delete_skill_ajax", args=[self.skill.id])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertTrue(Skill.objects.filter(pk=self.skill.id).exists())


# ---------------------------------------------------------------------------
# Like / endorse via AJAX
# ---------------------------------------------------------------------------
class LikeAndEndorseAjaxTest(BaseTestCase):
    def test_like_requires_login_and_returns_401_json(self):
        url = reverse("main:toggle_like_ajax", args=[self.experience.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 401)
        self.assertIn("message", response.json())
        self.assertEqual(self.experience.liked_by.count(), 0)

    def test_like_toggles_on_and_off(self):
        self.login_as("regular")
        url = reverse("main:toggle_like_ajax", args=[self.experience.id])

        first = self.client.post(url)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json(), {"is_liked": True, "like_count": 1})
        self.assertEqual(self.experience.liked_by.count(), 1)

        second = self.client.post(url)
        self.assertEqual(second.json(), {"is_liked": False, "like_count": 0})
        self.assertEqual(self.experience.liked_by.count(), 0)

    def test_like_unknown_experience_returns_404(self):
        self.login_as("regular")
        url = reverse("main:toggle_like_ajax", args=[uuid.uuid4()])
        self.assertEqual(self.client.post(url).status_code, 404)

    def test_like_rejects_get(self):
        self.login_as("regular")
        url = reverse("main:toggle_like_ajax", args=[self.experience.id])
        self.assertEqual(self.client.get(url).status_code, 405)

    def test_endorse_requires_login_and_returns_401_json(self):
        url = reverse("main:toggle_endorse_ajax", args=[self.skill.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 401)
        self.assertIn("message", response.json())
        self.assertEqual(self.skill.endorsed_by.count(), 0)

    def test_endorse_toggles_on_and_off(self):
        self.login_as("regular")
        url = reverse("main:toggle_endorse_ajax", args=[self.skill.id])

        first = self.client.post(url)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json(), {"is_endorsed": True, "endorse_count": 1})
        self.assertEqual(self.skill.endorsed_by.count(), 1)

        second = self.client.post(url)
        self.assertEqual(second.json(), {"is_endorsed": False, "endorse_count": 0})
        self.assertEqual(self.skill.endorsed_by.count(), 0)

    def test_endorse_unknown_skill_returns_404(self):
        self.login_as("regular")
        url = reverse("main:toggle_endorse_ajax", args=[uuid.uuid4()])
        self.assertEqual(self.client.post(url).status_code, 404)

    def test_endorse_rejects_get(self):
        self.login_as("regular")
        url = reverse("main:toggle_endorse_ajax", args=[self.skill.id])
        self.assertEqual(self.client.get(url).status_code, 405)


# ---------------------------------------------------------------------------
# Role permissions on the regular (non-AJAX) pages: add / edit
# ---------------------------------------------------------------------------
class RolePermissionTest(BaseTestCase):
    def test_anonymous_is_redirected_to_login(self):
        for name in ("main:create_skill", "main:create_experience"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302, name)
            self.assertIn("/login/", response.url)

    def test_regular_user_gets_403_on_edit(self):
        self.login_as("regular")
        skill = self.client.get(reverse("main:update_skill", args=[self.skill.id]))
        exp = self.client.get(reverse("main:update_experience", args=[self.experience.id]))
        self.assertEqual(skill.status_code, 403)
        self.assertEqual(exp.status_code, 403)

    def test_editor_can_edit_but_not_create(self):
        self.login_as("editor")
        edit_skill = self.client.get(reverse("main:update_skill", args=[self.skill.id]))
        edit_exp = self.client.get(reverse("main:update_experience", args=[self.experience.id]))
        create_skill = self.client.get(reverse("main:create_skill"))
        create_exp = self.client.get(reverse("main:create_experience"))

        self.assertEqual(edit_skill.status_code, 200)
        self.assertEqual(edit_exp.status_code, 200)
        self.assertEqual(create_skill.status_code, 403)
        self.assertEqual(create_exp.status_code, 403)

    def test_superuser_can_open_create_pages(self):
        self.login_as("owner")
        self.assertEqual(self.client.get(reverse("main:create_skill")).status_code, 200)
        self.assertEqual(self.client.get(reverse("main:create_experience")).status_code, 200)


# ---------------------------------------------------------------------------
# Django messages are rendered so the toast can show them
# ---------------------------------------------------------------------------
class MessageToastTest(BaseTestCase):
    def test_skill_update_message_reaches_the_toast(self):
        self.login_as("owner")
        response = self.client.post(
            reverse("main:update_skill", args=[self.skill.id]),
            self.skill_payload(name="Renamed Skill", category="technical"),
            follow=True,
        )

        self.assertRedirects(response, reverse("main:show_skill"))
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "Renamed Skill")
        self.assertContains(response, "Skill updated successfully!")
        self.assertContains(response, 'id="toast-component"')
        self.assertNotContains(response, '<p class="form-help">')

    def test_experience_update_message_reaches_the_toast(self):
        self.login_as("owner")
        response = self.client.post(
            reverse("main:update_experience", args=[self.experience.id]),
            self.experience_payload(title="Updated Title", category="part-time"),
            follow=True,
        )

        self.assertRedirects(response, reverse("main:show_experience"))
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Updated Title")
        self.assertContains(response, "Experience updated successfully!")

    def test_message_is_shown_only_once(self):
        self.login_as("owner")
        self.client.post(
            reverse("main:update_skill", args=[self.skill.id]),
            self.skill_payload(), follow=True,
        )
        second_visit = self.client.get(reverse("main:show_skill"))
        self.assertNotContains(second_visit, "Skill updated successfully!")


# ---------------------------------------------------------------------------
# Auth & cookie
# ---------------------------------------------------------------------------
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