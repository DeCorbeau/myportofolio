import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from main.forms import ExperienceForm, SkillForm
from main.htmx_utils import form_errors_text, plain_error, with_toast
from main.models import Experience, Skill


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
                "category": experience.category,
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

@require_POST
def delete_experience_ajax(request, experience_id):
    if not request.user.is_superuser:
        return JsonResponse({"message": "Only the portfolio owner can delete experience."}, status=403)
    experience = Experience.objects.filter(pk=experience_id).first()
    if experience is None:
        return JsonResponse({"message": "Experience not found."}, status=404)
    experience.delete()
    return JsonResponse({"message": "Experience deleted successfully!"})

@require_POST
def toggle_like_ajax(request, experience_id):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "Please log in to like an experience."}, status=401)
    experience = Experience.objects.filter(pk=experience_id).first()
    if experience is None:
        return JsonResponse({"message": "Experience not found."}, status=404)
    if experience.liked_by.filter(pk=request.user.pk).exists():
        experience.liked_by.remove(request.user)
        is_liked = False
    else:
        experience.liked_by.add(request.user)
        is_liked = True
    return JsonResponse({"is_liked": is_liked, "like_count": experience.liked_by.count()})


# ---------------------------------------------------------------------------
# Skill (HTMX)
# ---------------------------------------------------------------------------

def annotate_skill(skill, user):
    """Attach the per-user endorsement state that the card template needs."""
    endorsers = list(skill.endorsed_by.all())
    skill.endorse_count = len(endorsers)
    skill.is_endorsed = user.is_authenticated and user in endorsers
    skill.endorsed_by_names = ", ".join(u.username for u in endorsers)
    return skill


def fetch_skill(skill_id):
    """Load one skill with its endorsers, or None if it does not exist."""
    return Skill.objects.prefetch_related("endorsed_by").filter(pk=skill_id).first()


def build_skill_groups(query, user, open_codes=()):
    """Group skills by category, in the same order as SKILL_CATEGORIES.

    A group is rendered open while searching, or when its code is in open_codes.
    """
    skills = Skill.objects.prefetch_related("endorsed_by").all()
    if query:
        skills = skills.filter(name__icontains=query)

    by_category = {}
    for skill in skills:
        by_category.setdefault(skill.category, []).append(annotate_skill(skill, user))

    # Known categories first, in SKILL_CATEGORIES order. Any category outside
    # the choices (e.g. from old seed data) goes last instead of being dropped.
    known = [code for code, _ in Skill.SKILL_CATEGORIES]
    extra = [code for code in by_category if code not in known]

    return [
        {
            "code": code,
            # get_category_display() falls back to the raw value for unknown codes
            "label": by_category[code][0].get_category_display(),
            "skills": by_category[code],
            "open": bool(query) or code in open_codes,
        }
        for code in known + extra
        if code in by_category
    ]


def render_skill_groups(request, query, open_codes=()):
    context = {
        "query": query,
        "groups": build_skill_groups(query, request.user, open_codes),
    }
    return render(request, "components/skill_groups.html", context)


def render_skill_card(request, skill):
    context = {"skill": annotate_skill(skill, request.user)}
    return render(request, "components/skill_card.html", context)


def show_skill(request):
    query = request.GET.get("q", "").strip()
    context = {
        "short_name": "Faiz",
        "query": query,
        "form": SkillForm(),
        "groups": build_skill_groups(query, request.user),
    }
    return render(request, "skill.html", context)


@require_GET
def search_skill(request):
    return render_skill_groups(request, request.GET.get("q", "").strip())


@require_POST
def create_skill(request):
    # Same reasoning as create_experience: a plain 403 instead of a redirect.
    if not request.user.is_superuser:
        return plain_error("Only the portfolio owner can add skills.", 403)
    form = SkillForm(request.POST)
    if not form.is_valid():
        return plain_error(form_errors_text(form), 400)
    skill = form.save()
    # Keep the search filter, and open the group that holds the new skill.
    response = render_skill_groups(
        request, request.POST.get("q", "").strip(), open_codes=[skill.category]
    )
    return with_toast(response, "Success", "New skill added successfully!")


@require_GET
def skill_card(request, skill_id):
    skill = fetch_skill(skill_id)
    if skill is None:
        return plain_error("Skill not found.", 404)
    return render_skill_card(request, skill)


@require_GET
def edit_skill(request, skill_id):
    if not request.user.has_perm("main.change_skill"):
        return plain_error("You do not have permission to edit skills.", 403)
    skill = fetch_skill(skill_id)
    if skill is None:
        return plain_error("Skill not found.", 404)
    form = SkillForm(instance=skill, auto_id=f"edit_skill_{skill.id}_%s")
    return render(
        request, "components/skill_edit_card.html", {"skill": skill, "form": form}
    )


@require_http_methods(["PUT"])
def update_skill(request, skill_id):
    if not request.user.has_perm("main.change_skill"):
        return plain_error("You do not have permission to edit skills.", 403)
    skill = fetch_skill(skill_id)
    if skill is None:
        return plain_error("Skill not found.", 404)
    form = SkillForm(QueryDict(request.body), instance=skill)
    if not form.is_valid():
        return plain_error(form_errors_text(form), 400)
    form.save()
    response = render_skill_card(request, fetch_skill(skill_id))
    return with_toast(response, "Success", "Skill updated successfully!")


@require_http_methods(["DELETE"])
def delete_skill(request, skill_id):
    if not request.user.is_superuser:
        return plain_error("Only the portfolio owner can delete skills.", 403)
    skill = Skill.objects.filter(pk=skill_id).first()
    if skill is None:
        return plain_error("Skill not found.", 404)
    skill.delete()
    return with_toast(HttpResponse(""), "Success", "Skill deleted successfully!")


@require_POST
def toggle_endorse(request, skill_id):
    if not request.user.is_authenticated:
        return plain_error("Please log in to endorse a skill.", 401)
    skill = Skill.objects.filter(pk=skill_id).first()
    if skill is None:
        return plain_error("Skill not found.", 404)
    if skill.endorsed_by.filter(pk=request.user.pk).exists():
        skill.endorsed_by.remove(request.user)
    else:
        skill.endorsed_by.add(request.user)
    return render_skill_card(request, fetch_skill(skill_id))


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