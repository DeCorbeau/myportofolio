from django.urls import path

from main import views

app_name = "main"

urlpatterns = [
    path("", views.show_main, name="show_main"),
    path("register/", views.register, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),

    # Experience (still the old JavaScript version)
    path("experience/", views.show_experience, name="show_experience"),
    path("api/experience/", views.get_experience_json, name="get_experience_json"),
    path("experience/add/", views.create_experience, name="create_experience"),
    path("experience/add-ajax/", views.create_experience_ajax, name="create_experience_ajax"),
    path("experience/<uuid:experience_id>/edit/", views.update_experience, name="update_experience"),
    path("experience/<uuid:experience_id>/delete-ajax/", views.delete_experience_ajax, name="delete_experience_ajax"),
    path("experience/<uuid:experience_id>/like-ajax/", views.toggle_like_ajax, name="toggle_like_ajax"),

    # Skill: the page, plus HTMX fragments
    path("skill/", views.show_skill, name="show_skill"),
    path("skill/search/", views.search_skill, name="search_skill"),
    path("skill/add/", views.create_skill, name="create_skill"),
    path("skill/<uuid:skill_id>/card/", views.skill_card, name="skill_card"),
    path("skill/<uuid:skill_id>/edit/", views.edit_skill, name="edit_skill"),
    path("skill/<uuid:skill_id>/update/", views.update_skill, name="update_skill"),
    path("skill/<uuid:skill_id>/delete/", views.delete_skill, name="delete_skill"),
    path("skill/<uuid:skill_id>/endorse/", views.toggle_endorse, name="toggle_endorse"),
]
