from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from main.forms import SkillForm, ExperienceForm
from main.models import Experience, Skill
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
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
    query = request.GET.get("q", "").strip()
    context = {
        "short_name": "Faiz",
        "query": query,
        "form": ExperienceForm(),
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


@require_POST
def create_experience_ajax(request):
    # No @login_required here: it would redirect to an HTML login page, which
    # fetch() follows and JavaScript cannot recognise as a failure. AnonymousUser
    # has is_superuser == False, so this one check rejects guests and normal users.
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Only the portfolio owner can add experience."},
            status=403,
        )
    form = ExperienceForm(request.POST)
    if form.is_valid():
        experience = form.save()
        return JsonResponse(
            {"message": "Experience added successfully.", "pk": str(experience.id)},
            status=201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@login_required(login_url="/login/")
@permission_required("main.change_experience", raise_exception=True)
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
    query = request.GET.get("q", "").strip()
    experiences = Experience.objects.prefetch_related("liked_by").all()
    if query:
        experiences = experiences.filter(
            Q(title__icontains=query) | Q(organization__icontains=query)
        )

    # Build the JSON manually so we can include per-user like state
    data = []
    for experience in experiences:
        liked_users = list(experience.liked_by.all())
        is_liked = request.user.is_authenticated and request.user in liked_users
        data.append({
            "pk": str(experience.id),
            "fields": {
                "title": experience.title,
                "organization": experience.organization,
                "category_display": experience.get_category_display(),
                "date_range": experience.date_range_display,
                "description_points": experience.description_points,
                "thumbnail": experience.thumbnail,
                "like_count": len(liked_users),
                "is_liked": is_liked,
                "liked_by_names": ", ".join(u.username for u in liked_users),
            },
        })
    return JsonResponse(data, safe=False)

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
    name_query = request.GET.get("name", "").strip()
    context = {
        "short_name": "Faiz",
        "name_query": name_query,
        "form": SkillForm(),
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
    skills = Skill.objects.prefetch_related("endorsed_by").all()
    if name_query:
        skills = skills.filter(name__icontains=name_query)

    # Keep skills ordered by category, in the same order as SKILL_CATEGORIES
    category_order = {code: index for index, (code, _) in enumerate(Skill.SKILL_CATEGORIES)}
    skills = sorted(skills, key=lambda skill: category_order.get(skill.category, len(category_order)))

    # Build the JSON manually so we can include per-user endorsement state
    data = []
    for skill in skills:
        endorsers = list(skill.endorsed_by.all())
        is_endorsed = request.user.is_authenticated and request.user in endorsers
        data.append({
            "pk": str(skill.id),
            "fields": {
                "name": skill.name,
                "category": skill.category,
                "category_display": skill.get_category_display(),
                "proficiency": skill.proficiency,
                "proficiency_display": skill.get_proficiency_display(),
                "impact": skill.impact,
                "context": skill.context,
                "endorse_count": len(endorsers),
                "is_endorsed": is_endorsed,
                "endorsed_by_names": ", ".join(u.username for u in endorsers),
            },
        })
    return JsonResponse(data, safe=False)

@require_POST
def create_skill_ajax(request):
    # No @login_required here: it would redirect to an HTML login page, which
    # fetch() cannot recognise as a failure. AnonymousUser has is_superuser == False,
    # so this single check rejects guests and normal users with a JSON 403.
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Only the portfolio owner can add skills."},
            status=403,
        )
    form = SkillForm(request.POST)
    if form.is_valid():
        skill = form.save()
        return JsonResponse(
            {"message": "Skill added successfully.", "pk": str(skill.id)},
            status=201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

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