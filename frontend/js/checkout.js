// 💳 CHECKOUT PAGE - PANGGIL 2 SERVICES: orders + payments
document.addEventListener('DOMContentLoaded', function() {
    console.log("💳 Checkout page loading - Integrating orders + payments services");
    loadCheckoutData();
    setupCheckoutForm();
});

function loadCheckoutData() {
    const cart = getCart();
    if (cart.length === 0) {
        showMessage('Keranjang Anda kosong', 'error');
        setTimeout(() => window.location.href = 'index.html', 2000);
        return;
    }

    displayOrderSummary(cart);
    loadUserData();
}

function displayOrderSummary(cart) {
    const container = document.getElementById('order-summary');
    const subtotal = getCartTotal();
    const deliveryFee = 10000;
    const total = subtotal + deliveryFee;
    
    const itemsHtml = cart.map(item => `
        <div class="flex justify-between items-center">
            <span>${item.name} x${item.quantity}</span>
            <span>${formatCurrency(item.price * item.quantity)}</span>
        </div>
    `).join('');
    
    container.innerHTML = itemsHtml;
    
    document.getElementById('summary-subtotal').textContent = formatCurrency(subtotal);
    document.getElementById('summary-delivery').textContent = formatCurrency(deliveryFee);
    document.getElementById('summary-total').textContent = formatCurrency(total);
}

async function loadUserData() {
    try {
        // Load user data untuk pre-fill form
        const userResponse = await apiCall('users/api/users/1'); // Sample user ID 1
        if (userResponse.success) {
            populateUserForm(userResponse.data);
        }
    } catch (error) {
        console.error('Error loading user data:', error);
    }
}

function populateUserForm(user) {
    document.querySelector('input[name="customer-name"]').value = user.name || '';
    document.querySelector('input[name="customer-email"]').value = user.email || '';
    document.querySelector('input[name="customer-phone"]').value = user.phone || '';
    document.querySelector('textarea[name="delivery-address"]').value = user.address || '';
}

function setupCheckoutForm() {
    const form = document.getElementById('checkout-form');
    form.addEventListener('submit', handleCheckout);
}

async function handleCheckout(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const checkoutData = {
        customerName: formData.get('customer-name'),
        customerEmail: formData.get('customer-email'),
        customerPhone: formData.get('customer-phone'),
        deliveryAddress: formData.get('delivery-address'),
        paymentMethod: formData.get('payment-method')
    };

    // Validate form
    if (!checkoutData.customerName || !checkoutData.deliveryAddress) {
        showMessage('Harap isi semua field yang wajib', 'error');
        return;
    }

    try {
        showMessage('Memproses pesanan Anda...', 'info');
        
        const cart = getCart();
        const restaurantId = 1; // Assuming first restaurant for demo
        
        console.log("💳 Creating order with services: orders + payments + deliveries");
        
        // Create order dengan integration multiple services
        const result = await createOrder(1, restaurantId, cart, checkoutData.deliveryAddress);
        
        if (result.payment.status === 'completed') {
            showMessage('Pesanan berhasil dibuat!', 'success');
            clearCart();
            
            // Redirect to order tracking
            setTimeout(() => {
                window.location.href = `order-tracking.html?order_id=${result.order.id}`;
            }, 2000);
        } else {
            showMessage('Pembayaran gagal. Silakan coba lagi.', 'error');
        }
        
    } catch (error) {
        console.error('Checkout error:', error);
        showMessage('Gagal membuat pesanan. Silakan coba lagi.', 'error');
    }
}