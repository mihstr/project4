document.addEventListener('DOMContentLoaded', function() {
    // Poslušaj klike na gumbe za urejanje
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.onclick = function() {
            const postId = this.dataset.postId;
            const postContent = document.querySelector(`#post-content-${postId}`);
            const editArea = document.querySelector(`#edit-area-${postId}`);
            const textarea = editArea.querySelector('textarea');
            
            // Prikaži področje za urejanje in skrij originalno vsebino
            postContent.classList.add('d-none');
            editArea.classList.remove('d-none');
            
            // Nastavi fokus na textarea in postavi kurzor na konec
            textarea.focus();
            textarea.setSelectionRange(textarea.value.length, textarea.value.length);
            
            // Poslušaj klik na gumb za preklic
            editArea.querySelector('.cancel-btn').onclick = function() {
                postContent.classList.remove('d-none');
                editArea.classList.add('d-none');
                textarea.value = postContent.textContent.trim();
            };
            
            // Poslušaj klik na gumb za shranjevanje
            editArea.querySelector('.save-btn').onclick = async function() {
                const content = textarea.value.trim();
                
                try {
                    const response = await fetch(`/posts/${postId}/edit`, {
                        method: 'PUT',
                        body: JSON.stringify({
                            content: content
                        }),
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        // Posodobi vsebino in skrij področje za urejanje
                        postContent.textContent = content;
                        postContent.classList.remove('d-none');
                        editArea.classList.add('d-none');
                    } else {
                        alert(result.error);
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Prišlo je do napake pri shranjevanju.');
                }
            };
        };
    });

    // Dodaj funkcionalnost za všečkanje
    document.querySelectorAll('.like-btn').forEach(button => {
        button.onclick = async function() {
            const postId = this.dataset.postId;
            const icon = this.querySelector('i');
            const likesCountElement = this.parentElement.querySelector('.likes-count');
            const besedilo = likesCountElement.nextSibling;
            
            try {
                const response = await fetch(`/posts/${postId}/like`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    // Posodobi ikono srčka
                    icon.classList.toggle('fas', result.liked);
                    icon.classList.toggle('far', !result.liked);
                    
                    // Posodobi število všečkov in besedilo
                    likesCountElement.textContent = result.likes_count;
                    besedilo.textContent = ` ${sklanjajVsecke(result.likes_count)}`;
                } else {
                    alert(result.error);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Prišlo je do napake pri všečkanju.');
            }
        };
    });
});

// Pomožna funkcija za pridobivanje CSRF žetona
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function sklanjajVsecke(stevilo) {
    if (stevilo % 100 === 1) {
        return "všeček";
    } else if (stevilo % 100 === 2) {
        return "všečka";
    } else if (stevilo % 100 === 3 || stevilo % 100 === 4) {
        return "všečki";
    } else {
        return "všečkov";
    }
} 