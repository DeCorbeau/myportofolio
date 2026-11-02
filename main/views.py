import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render

from main.forms import ExperienceForm, SkillForm
from main.models import Skill


def show_main(request):
    last_login = request.COOKIES.get(
        "last_login", "No login session yet / cookie not found"
    )
    context = {
        "name": "Faiz Yusuf Elriki",
        "short_name": "Faiz",
        "npm": "2506607921",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "I'm a passionate learner with a strong interest in technology, "
            "programming, and business. I enjoy exploring new ideas, sharpening "
            "my skills, and finding ways to apply them in real-world situations. "
            "I believe growth comes from learning with and from others. Whether "
            "it's through collaboration, mentorship, or simply sharing "
            "perspectives, I'm always eager to absorb knowledge and exchange "
            "experiences. With a growth-driven mindset, I aim to contribute "
            "positively wherever I go while continuously improving myself "
            "along the way."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)


# Experience and Skill pages are skeletons: the data is loaded by JS from /api/v1/.

def show_experience(request):
    query = request.GET.get("q", "").strip()
    context = {
        "short_name": "Faiz",
        "query": query,
        "form": ExperienceForm(),
        # auto_id berbeda supaya id input form edit tidak bentrok dengan form tambah
        "edit_form": ExperienceForm(auto_id="edit_experience_%s"),
    }
    return render(request, "experience.html", context)


def show_skill(request):
    query = request.GET.get("q", "").strip()
    context = {
        "short_name": "Faiz",
        "query": query,
        "form": SkillForm(),
        "edit_form": SkillForm(auto_id="edit_skill_%s"),
        "categories": [
            {"code": code, "label": label} for code, label in Skill.SKILL_CATEGORIES
        ],
    }
    return render(request, "skill.html", context)


def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account successfully created. Please log in.")
        return redirect("main:login")
    context = {"form": form, "short_name": "Faiz"}
    return render(request, "register.html", context)


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        response = redirect("main:show_main")
        response.set_cookie("last_login", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return response
    context = {"form": form, "short_name": "Faiz"}
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response