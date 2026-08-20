document.addEventListener('DOMContentLoaded', () => {

    const overlay = document.getElementById(
        'announcement-overlay'
    );

    if (!overlay) {
        return;
    }


    const closeButton = document.getElementById(
        'announcement-close'
    );

    const dismissButton = document.getElementById(
        'announcement-dismiss'
    );


    const announcementId = overlay.dataset.announcementId;

    const storageKey = `announcement_${announcementId}_dismissed`;


    // Daha önce kapatılmışsa gösterme

    if (localStorage.getItem(storageKey) === 'true') {

        overlay.remove();

        return;
    }


    function closeAnnouncement() {

        localStorage.setItem(
            storageKey,
            'true'
        );

        overlay.remove();

    }


    closeButton.addEventListener(
        'click',
        closeAnnouncement
    );


    dismissButton.addEventListener(
        'click',
        closeAnnouncement
    );


    // Overlay'e tıklayınca kapat

    overlay.addEventListener('click', (event) => {

        if (event.target === overlay) {
            closeAnnouncement();
        }

    });

});