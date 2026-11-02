from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsPortfolioOwnerOrReadOnly(BasePermission):
    """Read: semua orang. Tulis (POST/PUT/PATCH/DELETE): hanya pemilik."""

    message = "Only the portfolio owner can change this."

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_superuser


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    """Read: semua. PUT/PATCH: pemilik atau Editor. POST/DELETE: pemilik saja."""

    change_perm = None  # diisi subclass
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


class CanManageSkill(IsPortfolioOwnerOrEditorOrReadOnly):
    change_perm = "main.change_skill"