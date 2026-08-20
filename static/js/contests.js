document.addEventListener('DOMContentLoaded', () => {

    const voteButtons = document.querySelectorAll(
        '.vote-btn[data-vote-id]'
    );


    // =========================================================
    // CSRF COOKIE
    // =========================================================

    function getCookie(name) {

        let cookieValue = null;

        if (document.cookie && document.cookie !== '') {

            const cookies = document.cookie.split(';');

            for (let cookie of cookies) {

                cookie = cookie.trim();

                if (
                    cookie.substring(0, name.length + 1) ===
                    `${name}=`
                ) {
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


    // =========================================================
    // VOTE
    // =========================================================

    voteButtons.forEach(button => {

        button.addEventListener('click', async () => {

            // Buton zaten devre dışıysa işlem yapma
            if (button.disabled) {
                return;
            }


            const voteUrl = button.dataset.voteUrl;


            // URL yoksa işlemi durdur
            if (!voteUrl) {

                console.error(
                    'Oy verme URL bilgisi bulunamadı.'
                );

                return;
            }


            // Çift tıklamayı engelle
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


                // =================================================
                // DJANGO HATA DÖNDÜRDÜ
                // =================================================

                if (
                    !response.ok ||
                    data.status === 'error'
                ) {

                    alert(
                        data.message ||
                        'Oy verme işlemi başarısız.'
                    );

                    button.disabled = false;

                    return;
                }


                // =================================================
                // BAŞARILI OY
                // =================================================

                if (
                    data.status === 'success' &&
                    data.action === 'added'
                ) {

                    // Butonu "Oy Verildi" durumuna getir
                    button.classList.add('voted');

                    button.innerHTML = `
                        <i class="fa-solid fa-check"></i>
                        Oy Verildi
                    `;


                    // Küçük animasyon
                    button.classList.remove('pulse');

                    void button.offsetWidth;

                    button.classList.add('pulse');


                    // Sayfayı yenile
                    // Böylece kullanılan/kalan oy bilgisi güncellenir
                    setTimeout(() => {

                        window.location.reload();

                    }, 500);
                }

            } catch (error) {

                console.error(
                    'Vote error:',
                    error
                );


                alert(
                    'Oy verme sırasında bir hata oluştu. ' +
                    'Lütfen sayfayı yenileyip tekrar deneyin.'
                );


                button.disabled = false;
            }

        });

    });

});