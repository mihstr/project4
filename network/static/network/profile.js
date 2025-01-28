document.addEventListener('DOMContentLoaded', function() {
    const followForm = document.querySelector('.follow-form');
    if (followForm) {
        followForm.onsubmit = async function(e) {
            e.preventDefault();
            const username = this.dataset.username;
            
            try {
                const response = await fetch(`/follow/${username}`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    const button = document.querySelector('#follow-button');
                    const followersCount = document.querySelector('#followers-count');
                    
                    button.textContent = data.is_following ? 'Prenehaj slediti' : 'Sledi';
                    followersCount.textContent = data.followers_count;
                }
            } catch (error) {
                console.error('Error:', error);
            }
        };
    }
}); 