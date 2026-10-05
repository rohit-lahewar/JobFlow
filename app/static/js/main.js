/**
 * JobFlow Main Client-Side JavaScript
 * Manages UI interactions, sidebar toggling, delete confirmation modals, and alerts.
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Mobile Sidebar Toggle
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebarBackdrop = document.getElementById('sidebarBackdrop');

  if (sidebarToggle && sidebar && sidebarBackdrop) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('show');
      sidebarBackdrop.classList.toggle('show');
    });

    sidebarBackdrop.addEventListener('click', function () {
      sidebar.classList.remove('show');
      sidebarBackdrop.classList.remove('show');
    });
  }

  // 2. Initialize Bootstrap Toasts
  const toastElList = [].slice.call(document.querySelectorAll('.toast'));
  toastElList.forEach(function (toastEl) {
    const toast = new bootstrap.Toast(toastEl, { delay: 5000 });
    toast.show();
  });

  // 3. Reusable Delete Confirmation Modal Setup
  const confirmDeleteModal = document.getElementById('confirmDeleteModal');
  if (confirmDeleteModal) {
    confirmDeleteModal.addEventListener('show.bs.modal', function (event) {
      const button = event.relatedTarget;
      const actionUrl = button.getAttribute('data-action-url');
      const itemName = button.getAttribute('data-item-name') || 'this item';

      const deleteForm = confirmDeleteModal.querySelector('#deleteItemForm');
      const itemSpan = confirmDeleteModal.querySelector('#deleteItemName');

      if (deleteForm && actionUrl) {
        deleteForm.action = actionUrl;
      }
      if (itemSpan) {
        itemSpan.textContent = itemName;
      }
    });
  }

  // 4. Auto-dismiss alerts after 6 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 6000);
  });
});
