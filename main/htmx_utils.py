import json

from django.http import HttpResponse


def plain_error(message, status):
    """Return a plain-text error.

    The global HTMX handler (static/js/htmx-events.js) reads this body and
    shows it in a toast, so keep it as text and not as an HTML page.
    """
    return HttpResponse(
        message, status=status, content_type="text/plain; charset=utf-8"
    )


def with_toast(response, title, message, kind="success"):
    """Make the browser show a toast by attaching an HX-Trigger header."""
    response["HX-Trigger"] = json.dumps(
        {"showToast": {"title": title, "message": message, "type": kind}}
    )
    return response


def form_errors_text(form):
    """Flatten form errors into one readable sentence for the toast."""
    parts = []
    for field, errors in form.errors.get_json_data().items():
        prefix = "" if field == "__all__" else f"{field}: "
        parts.extend(f"{prefix}{error['message']}" for error in errors)
    return " ".join(parts)
