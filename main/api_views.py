from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Experience, Skill
from main.permissions import CanManageExperience, CanManageSkill
from main.serializers import ExperienceSerializer, SkillSerializer


# --- helper bersama (logikanya sama untuk Experience dan Skill) -------------

def _list_or_create(request, queryset, serializer_class):
    context = {"request": request}
    if request.method in ("GET", "HEAD"):
        return Response(serializer_class(queryset, many=True, context=context).data)
    serializer = serializer_class(data=request.data, context=context)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def _detail(request, instance, serializer_class):
    context = {"request": request}
    if request.method in ("GET", "HEAD"):
        return Response(serializer_class(instance, context=context).data)
    if request.method == "DELETE":
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = serializer_class(
        instance, data=request.data,
        partial=request.method == "PATCH", context=context,
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


def _toggle(relation, user):
    if relation.filter(pk=user.pk).exists():
        relation.remove(user)
    else:
        relation.add(user)


# --- Experience -------------------------------------------------------------

@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([CanManageExperience])
def experience_list(request):
    experiences = Experience.objects.prefetch_related("liked_by").order_by(
        "-started_at", "title", "id"
    )
    q = request.query_params.get("q", "").strip()
    if q:
        experiences = experiences.filter(
            Q(title__icontains=q) | Q(organization__icontains=q)
        )
    return _list_or_create(request, experiences, ExperienceSerializer)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([CanManageExperience])
def experience_detail(request, experience_id):
    experience = get_object_or_404(
        Experience.objects.prefetch_related("liked_by"), pk=experience_id
    )
    return _detail(request, experience, ExperienceSerializer)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def experience_like(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    _toggle(experience.liked_by, request.user)
    return Response(ExperienceSerializer(experience, context={"request": request}).data)


# --- Skill ------------------------------------------------------------------

@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([CanManageSkill])
def skill_list(request):
    skills = Skill.objects.prefetch_related("endorsed_by").order_by("name", "id")
    q = request.query_params.get("q", "").strip()
    if q:
        skills = skills.filter(name__icontains=q)
    return _list_or_create(request, skills, SkillSerializer)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([CanManageSkill])
def skill_detail(request, skill_id):
    skill = get_object_or_404(
        Skill.objects.prefetch_related("endorsed_by"), pk=skill_id
    )
    return _detail(request, skill, SkillSerializer)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def skill_endorse(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    _toggle(skill.endorsed_by, request.user)
    return Response(SkillSerializer(skill, context={"request": request}).data)