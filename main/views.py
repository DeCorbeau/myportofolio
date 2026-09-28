from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from main.forms import SkillForm, ExperienceForm
from main.models import Experience, Skill
from django.core import serializers
from django.http import HttpResponse
import datetime

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

def show_experience(request):
    context = {
        "short_name": "Faiz",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

@login_required(login_url="/login/")
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    form = ExperienceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience added successfully!")
        return redirect("main:show_experience")
    context = {
        "name": "Faiz Yusuf Elriki",
        "short_name": "Faiz",
        "form": form,
    }
    return render(request, "experience_form.html", context)


@login_required(login_url="/login/")
@permission_required("main.change_skill", raise_exception=True)
def update_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience updated successfully!")
        return redirect("main:show_experience")
    context = {
        "name": "Faiz Yusuf Elriki",
        "short_name": "Faiz",
        "form": form,
        "experience": experience,
    }
    return render(request, "experience_form.html", context)


@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience deleted successfully!")
        return redirect("main:show_experience")
    return redirect("main:show_experience")

def get_experience_json(request):
    experiences = Experience.objects.all()
    experiences_json = serializers.serialize("json", experiences, use_natural_foreign_keys=True)
    return HttpResponse(experiences_json, content_type="application/json")

@login_required(login_url="/login/")
def toggle_like(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == "POST":
        if request.user in experience.liked_by.all():
            experience.liked_by.remove(request.user)
        else:
            experience.liked_by.add(request.user)
    return redirect("main:show_experience")

def show_skill(request):
    json_response = get_skill_json(request)
    skills = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    skills = [skill.object for skill in skills]

    name_query = request.GET.get("name", "").strip()

    grouped = {}
    for code, label in Skill.SKILL_CATEGORIES:
        items = [s for s in skills if s.category == code]
        if items:
            grouped[label] = items

    context = {
        "short_name": "Faiz",
        "skill_groups": grouped,
        "name_query": name_query,
    }
    return render(request, "skill.html", context)

@login_required(login_url="/login/")
def create_skill(request):
    if not request.user.is_superuser:
        raise PermissionDenied    
    form = SkillForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skill added successfully!")
        return redirect("main:show_skill")
    context = {
        "name": "Faiz",
        "short_name": "Faiz",
        "form": form,
    }
    return render(request, "skill_form.html", context)

def get_skill_json(request):
    name_query = request.GET.get("name", "").strip()
    skills = Skill.objects.all()

    if name_query:
        skills = skills.filter(name__icontains=name_query)

    skills_json = serializers.serialize("json", skills, use_natural_foreign_keys=True)
    return HttpResponse(skills_json, content_type="application/json")

@login_required(login_url="/login/")
def delete_skill(request, skill_id):
    if not request.user.is_superuser:
        raise PermissionDenied    
    skill = get_object_or_404(Skill, pk=skill_id)
    if request.method == "POST":
        skill.delete()
        messages.success(request, "Skill deleted successfully!")
        return redirect("main:show_skill")
    return redirect("main:show_skill")

@login_required(login_url="/login/")
@permission_required("main.change_skill", raise_exception=True)
def update_skill(request, skill_id): 
    skill = get_object_or_404(Skill, pk=skill_id)
    form = SkillForm(request.POST or None, instance=skill)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skill updated successfully!")
        return redirect("main:show_skill")
    context = {
        "name": "Faiz",
        "short_name": "Faiz",
        "form": form,
        "skill": skill,
    }
    return render(request, "skill_form.html", context)

@login_required(login_url="/login/")
def toggle_endorse(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    if request.method == "POST":
        if request.user in skill.endorsed_by.all():
            skill.endorsed_by.remove(request.user)
        else:
            skill.endorsed_by.add(request.user)
    return redirect("main:show_skill")

def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account successfully created. Please log in.")
        return redirect("main:login")
    context = {"form": form,
               "short_name": "Faiz"}
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        response = redirect("main:show_main")
        response.set_cookie("last_login", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return response
    context = {"form": form,
               "short_name": "Faiz"}
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response =  redirect("main:show_main")
    response.delete_cookie("last_login")
    return response