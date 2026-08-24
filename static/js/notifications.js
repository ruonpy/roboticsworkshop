document.addEventListener('DOMContentLoaded', function () {
    const notificationMenu = document.getElementById('notificationMenu');

    if (!notificationMenu) {
        return;
    }

    notificationMenu.addEventListener('click', function () {
        fetch(notificationMenu.dataset.readUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': notificationMenu.dataset.csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Bildirimler okunurken hata oluştu.');
            }

            const badge = notificationMenu.querySelector('.badge');

            if (badge) {
                badge.remove();
            }
        })
        .catch(error => {
            console.error('Notification Error:', error);
        });
    });
});