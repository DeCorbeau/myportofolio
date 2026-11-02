from django.urls import path

from main import views

app_name = "main"

urlpatterns = [
    path("", views.show_main, name="show_main"),
    path("register/", views.register, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),

    # Experience
    path("experience/", views.show_experience, name="show_experience"),

    # Skill: the page, plus HTMX fragments
    path("skill/", views.show_skill, name="show_skill"),
]
