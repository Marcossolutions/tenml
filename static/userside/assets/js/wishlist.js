document.addEventListener('DOMContentLoaded', function() {
    const wishlistButtons = document.querySelectorAll('.wishlist-button');
    
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const variantId = this.dataset.variantId;
            
            fetch('/toggle-wishlist/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({variant_id: variantId})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'added') {
                    this.innerHTML = '❤️'; // Filled heart
                    this.classList.add('text-red-500');
                } else if (data.status === 'removed') {
                    this.innerHTML = '🤍'; // Empty heart
                    this.classList.remove('text-red-500');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});

// Function to get CSRF token
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