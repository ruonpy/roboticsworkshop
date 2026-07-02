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
    // Intercept all active like button elements inside the showcase viewport
    const likeButtons = document.querySelectorAll('.like-btn');

    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Extract local DOM state variables
            const projectId = this.getAttribute('data-project-id');
            const countText = this.querySelector('.count-text');
            const iconHeart = this.querySelector('.icon-heart');
            const currentButton = this;
            const csrftoken = getCookie('csrftoken');

            // Dispatch secure asynchronous POST payload to the server-side validator
            fetch(`/project/${projectId}/like/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Update user interface parameters dynamically without reloading
                    countText.textContent = data.like_count;
                    iconHeart.classList.remove('fa-regular');
                    iconHeart.classList.add('fa-solid');
                    
                    currentButton.classList.remove('text-muted');
                    currentButton.classList.add('text-danger', 'btn-light');
                    currentButton.setAttribute('disabled', 'true');
                }
            })
            .catch(error => console.error('Operational Error:', error));
        });
    });
});