/**
 * AcuMeds - Main JavaScript
 */

// Document Ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Setup form validation
    setupFormValidation();
    
    // Setup search functionality
    setupSearch();
});

/**
 * Initialize Bootstrap Tooltips
 */
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Format currency
 */
function formatCurrency(value) {
    return '₹' + parseFloat(value).toFixed(2);
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * Setup search functionality
 */
function setupSearch() {
    const searchInput = document.querySelector('input[name="search"]');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            // You can add real-time search here
        });
    }
}

/**
 * Add to cart functionality
 */
function addToCart(medicineId, quantity = 1) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/cart/add/' + medicineId;
    
    const quantityInput = document.createElement('input');
    quantityInput.type = 'hidden';
    quantityInput.name = 'quantity';
    quantityInput.value = quantity;
    
    form.appendChild(quantityInput);
    document.body.appendChild(form);
    form.submit();
}

/**
 * Update cart quantity
 */
function updateQuantity(itemId) {
    const input = document.querySelector(`input[data-item-id="${itemId}"]`);
    if (input && input.value > 0) {
        // Form will be submitted with updated value
    }
}

/**
 * Calculate order total
 */
function calculateOrderTotal() {
    const items = document.querySelectorAll('.order-item');
    let total = 0;
    
    items.forEach(item => {
        const price = parseFloat(item.dataset.price);
        const quantity = parseInt(item.dataset.quantity);
        total += price * quantity;
    });
    
    return total;
}

/**
 * Show loading indicator
 */
function showLoading(message = 'Loading...') {
    const loader = document.createElement('div');
    loader.id = 'loading-indicator';
    loader.innerHTML = `
        <div class="position-fixed top-50 start-50 translate-middle">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">${message}</span>
            </div>
        </div>
    `;
    document.body.appendChild(loader);
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    const loader = document.getElementById('loading-indicator');
    if (loader) {
        loader.remove();
    }
}

/**
 * Confirm action
 */
function confirmAction(message = 'Are you sure?') {
    return confirm(message);
}

/**
 * Show notification
 */
function showNotification(message, type = 'success', duration = 3000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-dismiss
    setTimeout(() => {
        alertDiv.remove();
    }, duration);
}

/**
 * Format date
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

/**
 * Setup real-time search
 */
function setupRealTimeSearch() {
    const searchInput = document.querySelector('input[placeholder*="Search"]');
    
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            
            searchTimeout = setTimeout(() => {
                const query = this.value;
                
                if (query.length > 0) {
                    // Perform search
                    fetch(`/api/search?q=${encodeURIComponent(query)}`)
                        .then(response => response.json())
                        .then(data => {
                            // Handle search results
                            console.log('Search results:', data);
                        })
                        .catch(error => console.error('Search error:', error));
                }
            }, 300); // Debounce 300ms
        });
    }
}

/**
 * Cart operations
 */
const Cart = {
    /**
     * Remove item from cart
     */
    removeItem: function(itemId) {
        if (confirmAction('Remove this item from cart?')) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/cart/remove/${itemId}`;
            document.body.appendChild(form);
            form.submit();
        }
    },
    
    /**
     * Update item quantity
     */
    updateQuantity: function(itemId, quantity) {
        if (quantity < 1) {
            this.removeItem(itemId);
            return;
        }
        
        // Quantity will be updated on form submission
    },
    
    /**
     * Clear cart
     */
    clear: function() {
        if (confirmAction('Clear entire cart?')) {
            // Implement clear cart functionality
        }
    }
};

/**
 * Medicine operations
 */
const Medicine = {
    /**
     * Add to cart
     */
    addToCart: function(medicineId, quantity = 1) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/cart/add/${medicineId}`;
        
        const quantityInput = document.createElement('input');
        quantityInput.type = 'hidden';
        quantityInput.name = 'quantity';
        quantityInput.value = quantity;
        
        form.appendChild(quantityInput);
        document.body.appendChild(form);
        form.submit();
    },
    
    /**
     * View details
     */
    viewDetails: function(medicineId) {
        window.location.href = `/medicines/${medicineId}`;
    }
};

/**
 * Order operations
 */
const Order = {
    /**
     * Cancel order
     */
    cancel: function(orderId) {
        if (confirmAction('Cancel this order?')) {
            // Implement cancel order functionality
        }
    },
    
    /**
     * Track order
     */
    track: function(orderId) {
        window.location.href = `/orders/${orderId}`;
    }
};

/**
 * User operations
 */
const User = {
    /**
     * Edit profile
     */
    editProfile: function() {
        window.location.href = '/profile';
    },
    
    /**
     * View orders
     */
    viewOrders: function() {
        window.location.href = '/orders/history';
    }
};

// Export for use in templates
window.Cart = Cart;
window.Medicine = Medicine;
window.Order = Order;
window.User = User;
