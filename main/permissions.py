from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    """Read: everyone. PUT/PATCH: owner or Editor. POST/DELETE: owner only."""

    change_perm = None  # diisi subclass, mis. "main.change_experience"
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return (
            request.method in ("PUT", "PATCH")
            and self.change_perm is not None
            and user.has_perm(self.change_perm)
        )


class CanManageExperience(IsPortfolioOwnerOrEditorOrReadOnly):
    change_perm = "main.change_experience"


class CanManageSkill(IsPortfolioOwnerOrEditorOrReadOnly):
    change_perm = "main.change_skill"