document.addEventListener('DOMContentLoaded', () => {
    const voteButtons = document.querySelectorAll('.vote-btn[data-vote-id]');

    // ================= CSRF COOKIE =================
    function getCookie(name) {
        let cookieValue = null;

        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');

            for (let cookie of cookies) {
                cookie = cookie.trim();

                if (cookie.substring(0, name.length + 1) === `${name}=`) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );

                    break;
                }
            }
        }

        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    // ================= VOTE =================
    voteButtons.forEach(button => {
        button.addEventListener('click', async () => {
            // Do nothing if the button is already disabled
            if (button.disabled) return;

            const voteUrl = button.dataset.voteUrl;

            if (!voteUrl) {
                console.error('Vote URL information not found.');
                return;
            }

            button.disabled = true;

            try {
                const response = await fetch(voteUrl, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    credentials: 'same-origin'
                });

                const data = await response.json();

                if (!response.ok || data.status === 'error') {
                    alert(data.message || 'Voting failed.');
                    button.disabled = false;
                    return;
                }

                if (data.status === 'success' && data.action === 'added') {
                    button.classList.add('voted');

                    button.innerHTML =
                        `<i class="fa-solid fa-check"></i> Oy Verildi`;

                    button.classList.remove('pulse');
                    void button.offsetWidth;
                    button.classList.add('pulse');

                    setTimeout(() => {
                        window.location.reload();
                    }, 500);
                }

            } catch (error) {
                console.error('Vote error:', error);

                alert(
                    'An error occurred while voting. ' +
                    'Please refresh the page and try again.'
                );

                button.disabled = false;
            }
        });
    });

    // ================= CONFETTI =================
    const resultsPage = document.querySelector('.contest-results-page');

    // Do nothing if this is not the results page
    if (!resultsPage) {
        return;
    }

    const competitionId = resultsPage.dataset.competitionId;

    // Create a unique key for each competition
    const confettiKey = `contest-confetti-${competitionId}`;

    // Do not show confetti if it has already been shown
    if (localStorage.getItem(confettiKey)) {
        return;
    }

    // Start the confetti animation
    startConfetti();

    // Mark this competition's confetti as shown
    localStorage.setItem(confettiKey, 'true');

    // ================= CONFETTI FUNCTION =================
    function startConfetti() {
        const confettiCount = 100;

        for (let i = 0; i < confettiCount; i++) {
            createConfetti();
        }
    }

    function createConfetti() {
        const confetti = document.createElement('div');

        confetti.classList.add('confetti');

        confetti.style.left = `${Math.random() * 100}vw`;

        confetti.style.animationDelay =
            `${Math.random() * 0.8}s`;

        confetti.style.animationDuration =
            `${2.5 + Math.random() * 2}s`;

        confetti.style.transform =
            `rotate(${Math.random() * 360}deg)`;

        document.body.appendChild(confetti);

        setTimeout(() => {
            confetti.remove();
        }, 5000);
    }
});