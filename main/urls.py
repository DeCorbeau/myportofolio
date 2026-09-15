from django.urls import path

from main.views import show_main, show_experience, show_skill, create_skill, get_skill_json

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("skill/", show_skill, name="show_skill"),
    path("skill/add/", create_skill, name="create_skill"),
    path("api/skill/", get_skill_json, name="get_skill_json"),
]