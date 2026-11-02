// Connects HTMX events to the toast component (toast.js).

// Success toasts: the server sends an HX-Trigger header named "showToast".
document.addEventListener('showToast', function (event) {
  const { title, message, type } = event.detail;
  showToast(title, message, type);
});

// Use the response text only when it is a plain-text message from our views.
// Anything else (e.g. an HTML 403 page from a CSRF failure) gets a generic text.
function errorMessageFrom(xhr) {
  const contentType = xhr.getResponseHeader('Content-Type') || '';
  if (contentType.startsWith('text/plain') && xhr.responseText) {
    return xhr.responseText;
  }
  return `Something went wrong (status ${xhr.status}).`;
}

// The toast title comes from the closest data-error-title attribute.
function errorTitleFrom(element) {
  const source = element && element.closest('[data-error-title]');
  return source ? source.dataset.errorTitle : 'Request failed';
}

// 4xx/5xx responses are not swapped into the page by HTMX, so show them here.
document.addEventListener('htmx:responseError', function (event) {
  showToast(errorTitleFrom(event.detail.elt), errorMessageFrom(event.detail.xhr), 'error');
});

document.addEventListener('htmx:sendError', function (event) {
  showToast(errorTitleFrom(event.detail.elt),
            'Could not reach the server. Please try again.', 'error');
});
