let toastTimer;

function showToast(title, message, type = 'normal', duration = 3000) {
  const toastComponent = document.getElementById('toast-component');
  const toastTitle = document.getElementById('toast-title');
  const toastMessage = document.getElementById('toast-message');

  if (!toastComponent) return;

  // Remove the previous type class
  toastComponent.classList.remove('toast-success', 'toast-error', 'toast-normal');

  // Apply the class that matches the new type
  if (type === 'success') {
    toastComponent.classList.add('toast-success');
  } else if (type === 'error') {
    toastComponent.classList.add('toast-error');
  } else {
    toastComponent.classList.add('toast-normal');
  }

  // textContent (not innerHTML) so server messages can never inject HTML
  toastTitle.textContent = title;
  toastMessage.textContent = message;

  // Cancel the previous timer if a toast is still visible
  clearTimeout(toastTimer);

  // Show in the browser top layer, above everything else including modals
  if (!toastComponent.matches(':popover-open')) {
    toastComponent.showPopover();
    void toastComponent.offsetHeight; // force style calculation so the transition runs
  }
  toastComponent.classList.remove('toast-hidden');
  toastComponent.classList.add('toast-show');

  // Auto-hide, then close the popover once the animation ends
  toastTimer = setTimeout(() => {
    toastComponent.classList.remove('toast-show');
    toastComponent.classList.add('toast-hidden');
    toastTimer = setTimeout(() => toastComponent.hidePopover(), 300);
  }, duration);
}