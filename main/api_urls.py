from django.urls import path

from main import api_views

app_name = "api"

urlpatterns = [
    path("experiences/", api_views.experience_list, name="experience-list"),
    path("experiences/<uuid:experience_id>/", api_views.experience_detail, name="experience-detail"),
    path("experiences/<uuid:experience_id>/like/", api_views.experience_like, name="experience-like"),

    path("skills/", api_views.skill_list, name="skill-list"),
    path("skills/<uuid:skill_id>/", api_views.skill_detail, name="skill-detail"),
    path("skills/<uuid:skill_id>/endorse/", api_views.skill_endorse, name="skill-endorse"),
]