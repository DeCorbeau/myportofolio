from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from main.forms import SkillForm
from main.models import Experience, Skill

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
        "name": "Faiz",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_skill(request):
    skills = Skill.objects.all().order_by('category', '-proficiency')
    grouped = {}
    for code, label in Skill.SKILL_CATEGORIES:
        items = skills.filter(category=code)
        if items.exists():
            grouped[label] = items
    context = {
        "name": "Faiz",
        "skill_groups": grouped,
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
        "form": form,
    }
    return render(request, "skill_form.html", context)