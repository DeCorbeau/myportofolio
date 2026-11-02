import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db.models import Q
from django.http import HttpResponse, QueryDict
from django.shortcuts import redirect, render
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


# ---------------------------------------------------------------------------
# Experience (HTMX): every view below returns an HTML fragment, not a full page
# ---------------------------------------------------------------------------

def annotate_experience(experience, user):
    """Attach the per-user like state that the card template needs."""
    likers = list(experience.liked_by.all())
    experience.like_count = len(likers)
    experience.is_liked = user.is_authenticated and user in likers
    experience.liked_by_names = ", ".join(u.username for u in likers)
    return experience


def fetch_experience(experience_id):
    """Load one experience with its likers, or None if it does not exist."""
    return (
        Experience.objects.prefetch_related("liked_by")
        .filter(pk=experience_id)
        .first()
    )


def get_experiences(query, user):
    experiences = Experience.objects.prefetch_related("liked_by").all()
    if query:
        experiences = experiences.filter(
            Q(title__icontains=query) | Q(organization__icontains=query)
        )
    return [annotate_experience(experience, user) for experience in experiences]


def render_experience_list(request, query):
    context = {
        "query": query,
        "experiences": get_experiences(query, request.user),
    }
    return render(request, "components/experience_list.html", context)


def render_experience_item(request, experience):
    context = {"experience": annotate_experience(experience, request.user)}
    return render(request, "components/experience_item.html", context)


def show_experience(request):
    query = request.GET.get("q", "").strip()
    context = {
        "short_name": "Faiz",
        "query": query,
        "form": ExperienceForm(),
        "experiences": get_experiences(query, request.user),
    }
    return render(request, "experience.html", context)


@require_GET
def search_experience(request):
    return render_experience_list(request, request.GET.get("q", "").strip())


@require_POST
def create_experience(request):
    # No @login_required: it would redirect to an HTML login page, and HTMX
    # would swap that page into the list. AnonymousUser.is_superuser is False,
    # so this one check rejects guests and normal users with a plain 403.
    if not request.user.is_superuser:
        return plain_error("Only the portfolio owner can add experience.", 403)
    form = ExperienceForm(request.POST)
    if not form.is_valid():
        return plain_error(form_errors_text(form), 400)
    form.save()
    # The add form includes the search box (hx-include), so keep the filter.
    response = render_experience_list(request, request.POST.get("q", "").strip())
    return with_toast(response, "Success", "New experience added successfully!")


@require_GET
def experience_card(request, experience_id):
    experience = fetch_experience(experience_id)
    if experience is None:
        return plain_error("Experience not found.", 404)
    return render_experience_item(request, experience)


@require_GET
def edit_experience(request, experience_id):
    if not request.user.has_perm("main.change_experience"):
        return plain_error("You do not have permission to edit experience.", 403)
    experience = fetch_experience(experience_id)
    if experience is None:
        return plain_error("Experience not found.", 404)
    # auto_id keeps the field ids unique when several forms are on the page
    form = ExperienceForm(
        instance=experience, auto_id=f"edit_experience_{experience.id}_%s"
    )
    context = {"experience": experience, "form": form}
    return render(request, "components/experience_edit_item.html", context)


@require_http_methods(["PUT"])
def update_experience(request, experience_id):
    if not request.user.has_perm("main.change_experience"):
        return plain_error("You do not have permission to edit experience.", 403)
    experience = fetch_experience(experience_id)
    if experience is None:
        return plain_error("Experience not found.", 404)
    # Django only fills request.POST for POST, so parse the PUT body ourselves.
    form = ExperienceForm(QueryDict(request.body), instance=experience)
    if not form.is_valid():
        return plain_error(form_errors_text(form), 400)
    form.save()
    response = render_experience_item(request, fetch_experience(experience_id))
    return with_toast(response, "Success", "Experience updated successfully!")


@require_http_methods(["DELETE"])
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        return plain_error("Only the portfolio owner can delete experience.", 403)
    experience = Experience.objects.filter(pk=experience_id).first()
    if experience is None:
        return plain_error("Experience not found.", 404)
    experience.delete()
    # Status 200 with an empty body: HTMX swaps the card for nothing.
    # A 204 would not be swapped, so the card would stay on the page.
    return with_toast(
        HttpResponse(""), "Success", "Experience deleted successfully!"
    )


@require_POST
def toggle_like(request, experience_id):
    if not request.user.is_authenticated:
        return plain_error("Please log in to like an experience.", 401)
    experience = Experience.objects.filter(pk=experience_id).first()
    if experience is None:
        return plain_error("Experience not found.", 404)
    if experience.liked_by.filter(pk=request.user.pk).exists():
        experience.liked_by.remove(request.user)
    else:
        experience.liked_by.add(request.user)
    return render_experience_item(request, fetch_experience(experience_id))


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

    return [
        {
            "code": code,
            "label": label,
            "skills": by_category[code],
            "open": bool(query) or code in open_codes,
        }
        for code, label in Skill.SKILL_CATEGORIES
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


# ---------------------------------------------------------------------------
# Auth (unchanged)
# ---------------------------------------------------------------------------

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
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response
