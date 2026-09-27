from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from main.forms import SkillForm
from main.models import Experience, Skill
from django.core import serializers
from django.http import HttpResponse

def show_main(request):
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
    }
    return render(request, "index.html", context)

def show_experience(request):
    context = {
        "short_name": "Faiz",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def get_experience_json(request):
    experiences = Experience.objects.all()
    experiences_json = serializers.serialize("json", experiences)
    return HttpResponse(experiences_json, content_type="application/json")

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

def create_skill(request):
    form = SkillForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skill baru berhasil ditambahkan!")
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

    skills_json = serializers.serialize("json", skills)
    return HttpResponse(skills_json, content_type="application/json")

def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    if request.method == "POST":
        skill.delete()
        messages.success(request, "Skill berhasil dihapus!")
        return redirect("main:show_skill")
    return redirect("main:show_skill")

def update_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    form = SkillForm(request.POST or None, instance=skill)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skill berhasil diperbarui!")
        return redirect("main:show_skill")
    context = {
        "name": "Faiz",
        "short_name": "Faiz",
        "form": form,
        "skill": skill,
    }
    return render(request, "skill_form.html", context)

def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")
    context = {"form": form,
               "short_name": "Faiz"}
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        response = redirect("main:show_main")
        return response
    context = {"form": form,
               "short_name": "Faiz"}
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response =  redirect("main:show_main")
    return response