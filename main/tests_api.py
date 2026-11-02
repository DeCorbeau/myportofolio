import datetime
import uuid

from django.contrib.auth.models import Permission, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience, Skill

PASSWORD = "test-password"


class RoleSetupMixin:
    def create_users(self):
        self.owner = User.objects.create_superuser("owner", "owner@example.com", PASSWORD)
        self.visitor = User.objects.create_user("visitor", password=PASSWORD)
        self.editor = User.objects.create_user("editor", password=PASSWORD)
        self.editor.user_permissions.add(
            Permission.objects.get(content_type__app_label="main", codename="change_experience"),
            Permission.objects.get(content_type__app_label="main", codename="change_skill"),
        )


class ExperienceAPITest(RoleSetupMixin, APITestCase):
    def setUp(self):
        self.create_users()
        self.experience = Experience.objects.create(
            title="Committee Head", organization="BEM", description="Led the team",
            category="committee", started_at=datetime.date(2025, 1, 1),
        )
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.experience.id])
        self.like_url = reverse("api:experience-like", args=[self.experience.id])
        self.payload = {
            "title": "New experience", "organization": "Fasilkom",
            "description": "Did useful things", "category": "internship",
            "thumbnail": "https://example.com/a.png", "started_at": "2025-06-01",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.experience.id))
        self.assertFalse(response.data[0]["is_liked"])
        self.assertNotIn("fields", response.data[0])
        self.assertNotIn("email", str(response.data))
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        self.assertEqual(len(self.client.get(self.list_url, {"q": "bem"}).data), 1)
        self.assertEqual(self.client.get(self.list_url, {"q": "nothing"}).data, [])

    def test_missing_experience(self):
        url = reverse("api:experience-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "X"}, format="json").status_code, 403)
            self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Committee Head")

    def test_editor_cannot_manage_experience(self):
        # Experience adalah contoh tutorial: hanya pemilik yang boleh menulis
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(self.client.patch(self.detail_url, {"title": "X"}, format="json").status_code, 403)
        self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Committee Head")
        self.assertEqual(Experience.objects.count(), 1)

    def test_owner_can_create_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Experience.objects.filter(pk=response.data["id"]).exists())

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        cases = [
            ({"title": " "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"thumbnail": "javascript:alert(1)"}, "thumbnail"),
            ({"category": "astronaut"}, "category"),
            ({"started_at": "not-a-date"}, "started_at"),
            ({"ended_at": "2020-01-01T00:00:00Z"}, "ended_at"),
        ]
        for changes, field in cases:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, field)
            self.assertIn(field, response.data)
        self.assertEqual(Experience.objects.count(), 1)

    def test_tags_are_stripped_from_text(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url, {**self.payload, "title": "Hi <b>there</b>"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Hi there")

    def test_like_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.like_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.experience.liked_by.count(), 0)

        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.like_url)
        self.assertTrue(response.data["is_liked"])
        self.assertEqual(response.data["like_count"], 1)
        response = self.client.post(self.like_url)
        self.assertFalse(response.data["is_liked"])
        self.assertEqual(response.data["like_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "like_count": 99, "is_liked": True,
            "liked_by_names": "forged", "liked_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["like_count"], 0)
        self.assertFalse(response.data["is_liked"])

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password=PASSWORD))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password=PASSWORD)
        # base.html merender {{ csrf_token }}, jadi halaman ini menyetel cookie csrftoken
        page = client.get(reverse("main:show_experience"))
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_date_only_end_date_is_accepted(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {**self.payload, "started_at": "2025-01-01", "ended_at": "2025-06-01"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_owner_patch_and_put(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Changed")
        self.assertEqual(self.experience.description, "Led the team")  # PATCH parsial: field lain tetap

        response = self.client.put(self.detail_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "New experience")

class SkillAPITest(RoleSetupMixin, APITestCase):
    def setUp(self):
        self.create_users()
        self.skill = Skill.objects.create(name="Python", category="technical", proficiency=3)
        self.list_url = reverse("api:skill-list")
        self.detail_url = reverse("api:skill-detail", args=[self.skill.id])
        self.endorse_url = reverse("api:skill-endorse", args=[self.skill.id])
        self.payload = {
            "name": "Public Speaking", "category": "communication",
            "proficiency": 2, "impact": "Presented to 100 people", "context": "Seminar",
        }

    def test_public_read_and_search(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["proficiency_display"], "Advanced")
        self.assertEqual(len(self.client.get(self.list_url, {"q": "pyth"}).data), 1)
        self.assertEqual(self.client.get(self.list_url, {"q": "zzz"}).data, [])

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"name": "X"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Skill.objects.count(), 1)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "Python")

    def test_editor_can_patch_but_not_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {"proficiency": 4}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.proficiency, 4)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Skill.objects.count(), 1)

    def test_owner_can_create_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.client.delete(self.detail_url).status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Skill.objects.filter(pk=self.skill.id).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        cases = [
            ({"name": " "}, "name"),
            ({"name": "<b></b>"}, "name"),
            ({"proficiency": 9}, "proficiency"),
            ({"category": "wizardry"}, "category"),
        ]
        for changes, field in cases:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, field)
            self.assertIn(field, response.data)
        self.assertEqual(Skill.objects.count(), 1)

    def test_endorse_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.endorse_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.skill.endorsed_by.count(), 0)

        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.endorse_url)
        self.assertTrue(response.data["is_endorsed"])
        self.assertEqual(response.data["endorse_count"], 1)
        response = self.client.post(self.endorse_url)
        self.assertFalse(response.data["is_endorsed"])

    def test_script_tags_are_stripped_from_name(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {**self.payload, "name": "<script>alert(1)</script>Python 2"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("<", response.data["name"])

    def test_owner_can_patch_and_editor_can_put(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"impact": "Shipped it"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.impact, "Shipped it")
        self.assertEqual(self.skill.name, "Python")

        self.client.force_authenticate(user=self.editor)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "Public Speaking")

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="editor", password=PASSWORD))
        response = client.patch(self.detail_url, {"name": "X"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "Python")

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="editor", password=PASSWORD)
        # halaman Skill harus menyetel cookie csrftoken (lewat {{ csrf_token }} di base.html)
        self.assertEqual(client.get(reverse("main:show_skill")).status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.patch(
            self.detail_url, {"proficiency": 4}, format="json", HTTP_X_CSRFTOKEN=token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)