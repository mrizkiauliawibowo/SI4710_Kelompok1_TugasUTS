// 🔧 UTILITIES & API GATEWAY INTEGRATION
const API_GATEWAY = 'http://localhost:5000';
const DEBUG_MODE = true;

// Universal API Call function
async function apiCall(endpoint, options = {}) {
    try {
        if (DEBUG_MODE) console.log(`🔄 Calling: ${API_GATEWAY}/${endpoint}`);
        
        const response = await fetch(`${API_GATEWAY}/${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (DEBUG_MODE) console.log(`✅ Response from ${endpoint}:`, data);
        return data;
        
    } catch (error) {
        console.error(`❌ API Call failed [${endpoint}]:`, error);
        return { 
            success: false, 
            error: 'Service unavailable. Please try again later.' 
        };
    }
}

// Utility Functions
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `fixed top-4 right-4 px-6 py-3 rounded-lg text-white font-semibold z-50 ${
        type === 'success' ? 'bg-green-500' : 
        type === 'error' ? 'bg-red-500' : 'bg-blue-500'
    }`;
    messageDiv.textContent = message;
    document.body.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.style.opacity = '0';
        messageDiv.style.transition = 'opacity 0.5s';
        setTimeout(() => messageDiv.remove(), 500);
    }, 3000);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0
    }).format(amount);
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('id-ID');
}

function getStatusBadge(status) {
    const statusConfig = {
        'pending': { color: 'bg-yellow-100 text-yellow-800', icon: 'fa-clock' },
        'confirmed': { color: 'bg-blue-100 text-blue-800', icon: 'fa-check' },
        'preparing': { color: 'bg-orange-100 text-orange-800', icon: 'fa-utensils' },
        'ready': { color: 'bg-purple-100 text-purple-800', icon: 'fa-box' },
        'on_the_way': { color: 'bg-indigo-100 text-indigo-800', icon: 'fa-truck' },
        'delivered': { color: 'bg-green-100 text-green-800', icon: 'fa-check-circle' },
        'cancelled': { color: 'bg-red-100 text-red-800', icon: 'fa-times' }
    };
    
    const config = statusConfig[status] || { color: 'bg-gray-100 text-gray-800', icon: 'fa-question' };
    return `<span class="px-2 py-1 rounded-full text-xs ${config.color}">
        <i class="fas ${config.icon} mr-1"></i>${status}
    </span>`;
}

// Cart Management
function getCart() {
    return JSON.parse(localStorage.getItem('cart')) || [];
}

function saveCart(cart) {
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
}

function clearCart() {
    localStorage.removeItem('cart');
    updateCartCount();
}

function addToCart(item) {
    const cart = getCart();
    const existingItem = cart.find(cartItem => cartItem.id === item.id);
    
    if (existingItem) {
        existingItem.quantity = (existingItem.quantity || 1) + 1;
    } else {
        cart.push({ ...item, quantity: 1 });
    }
    
    saveCart(cart);
    showMessage(`${item.name} ditambahkan ke keranjang!`, 'success');
}

function removeFromCart(itemId) {
    const cart = getCart().filter(item => item.id !== itemId);
    saveCart(cart);
    showMessage('Item dihapus dari keranjang', 'success');
}

function updateCartQuantity(itemId, quantity) {
    const cart = getCart();
    const item = cart.find(item => item.id === itemId);
    if (item) {
        if (quantity <= 0) {
            removeFromCart(itemId);
        } else {
            item.quantity = quantity;
            saveCart(cart);
        }
    }
}

function getCartTotal() {
    const cart = getCart();
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
}

function updateCartCount() {
    const cart = getCart();
    const totalItems = cart.reduce((sum, item) => sum + (item.quantity || 1), 0);
    const cartCount = document.getElementById('cart-count');
    
    if (cartCount) {
        if (totalItems > 0) {
            cartCount.textContent = totalItems;
            cartCount.classList.remove('hidden');
        } else {
            cartCount.classList.add('hidden');
        }
    }
}

// Order Management
async function createOrder(userId, restaurantId, items, deliveryAddress) {
    try {
        const orderData = {
            user_id: userId,
            restaurant_id: restaurantId,
            items: items.map(item => ({
                menu_item_id: item.id,
                menu_item_name: item.name,
                quantity: item.quantity,
                price: item.price
            }))
        };

        console.log('Creating order:', orderData);
        const orderResponse = await apiCall('orders/api/orders', {
            method: 'POST',
            body: JSON.stringify(orderData)
        });

        if (orderResponse.success) {
            // Create delivery
            const deliveryResponse = await apiCall('deliveries/api/deliveries', {
                method: 'POST',
                body: JSON.stringify({
                    order_id: orderResponse.data.id,
                    delivery_address: deliveryAddress
                })
            });

            // Create payment
            const paymentResponse = await apiCall('payments/api/payments', {
                method: 'POST',
                body: JSON.stringify({
                    order_id: orderResponse.data.id,
                    amount: orderResponse.data.total_amount,
                    payment_method: 'credit_card'
                })
            });

            // Process payment
            if (paymentResponse.success) {
                const processResponse = await apiCall(`payments/api/payments/${paymentResponse.data.id}/process`, {
                    method: 'POST'
                });

                return {
                    order: orderResponse.data,
                    delivery: deliveryResponse.data,
                    payment: processResponse.data
                };
            }
        }

        throw new Error('Failed to create order');
    } catch (error) {
        console.error('Order creation error:', error);
        throw error;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    updateCartCount();
});

// Scroll function for homepage
function scrollToRestaurants() {
    document.getElementById('restaurants-list').scrollIntoView({ 
        behavior: 'smooth' 
    });
}