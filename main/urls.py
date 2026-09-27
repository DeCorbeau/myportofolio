from django.urls import path

from main.views import show_main, show_experience, show_skill, create_skill, get_skill_json, delete_skill, update_skill, get_experience_json, register, login_user, logout_user, toggle_endorse, toggle_like, create_experience, delete_experience, update_experience

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("api/experience/", get_experience_json, name="get_experience_json"),
    path("skill/", show_skill, name="show_skill"),
    path("skill/add/", create_skill, name="create_skill"),
    path("skill/<uuid:skill_id>/edit/", update_skill, name="update_skill"),
    path("api/skill/", get_skill_json, name="get_skill_json"),
    path("skill/<uuid:skill_id>/delete/", delete_skill, name="delete_skill"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("skill/<uuid:skill_id>/endorse/", toggle_endorse, name="toggle_endorse"),
    path("experience/<uuid:experience_id>/like/", toggle_like, name="toggle_like"),
    path("experience/add/", create_experience, name="create_experience"),
    path("experience/<uuid:experience_id>/edit/", update_experience, name="update_experience"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),    
]