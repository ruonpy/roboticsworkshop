/* ==========================================================================
   🔐 SECURITY UTILITIES: CSRF TOKEN ENGINE
   ========================================================================== */

/**
 * Parses browser cookies to retrieve the secure Django CSRF token.
 * Necessary for securing state-changing asynchronous requests.
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/* ==========================================================================
   ⚡ SOCIAL ENGAGEMENT MECHANICS: ASYNCHRONOUS LIKE ENGINE
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
    const likeButtons = document.querySelectorAll('.like-btn');

    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const projectId = this.getAttribute('data-project-id');
            const countText = this.querySelector('.count-text');
            const iconHeart = this.querySelector('.icon-heart');
            const currentButton = this;
            const csrftoken = getCookie('csrftoken');

            fetch(`/project/${projectId}/like/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken
                }
            })
            .then(async response => {
                // Sunucu 200 OK dönmediyse (500, 403, 302 vs.) gelen hatayı yakala
                if (!response.ok) {
                    if (response.status === 403 || response.redirected) {
                        alert("Beğenmek için lütfen önce giriş yapın.");
                        window.location.href = "/login/"; // Veya login sayfanızın adresi
                        return;
                    }
                    const errorText = await response.text();
                    throw new Error(`Sunucu Hatası (${response.status}): ${errorText.substring(0, 100)}...`);
                }
                return response.json();
            })
            .then(data => {
                if (data && data.status === 'success') {
                    countText.textContent = data.like_count;
                    if (iconHeart) {
                        iconHeart.classList.remove('fa-regular');
                        iconHeart.classList.add('fa-solid');
                    }
                    
                    currentButton.classList.remove('text-muted');
                    currentButton.classList.add('text-danger', 'btn-light');
                    currentButton.setAttribute('disabled', 'true');
                } else if (data && data.message) {
                    alert(data.message);
                }
            })
            .catch(error => console.error('Operational Error:', error));
        });
    });
});