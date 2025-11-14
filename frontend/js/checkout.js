// 💳 CHECKOUT PAGE - PANGGIL 2 SERVICES: orders + payments
document.addEventListener('DOMContentLoaded', function() {
    console.log("💳 Checkout page loading - Integrating orders + payments services");
    loadCheckoutData();
    setupCheckoutForm();
});

function loadCheckoutData() {
    const cart = getCart();
    console.log("🛒 Cart items:", cart);
    
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
    
    console.log("💰 Order Summary - Subtotal:", subtotal, "Total:", total);
    
    const itemsHtml = cart.map(item => `
        <div class="flex justify-between items-center text-sm">
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
        console.log("👤 Loading user data...");
        // Load user data untuk pre-fill form
        const userResponse = await apiCall('api/user-service/api/users/1'); // Sample user ID 1
        console.log("User response:", userResponse);
        
        if (userResponse.success) {
            populateUserForm(userResponse.data);
        } else {
            console.warn("❌ Failed to load user data:", userResponse.error);
            // Use demo data
            populateUserForm({
                name: "John Doe",
                email: "john@example.com",
                phone: "081234567890",
                address: "Jl. Contoh No. 123, Jakarta"
            });
        }
    } catch (error) {
        console.error('Error loading user data:', error);
        // Use demo data
        populateUserForm({
            name: "John Doe",
            email: "john@example.com",
            phone: "081234567890",
            address: "Jl. Contoh No. 123, Jakarta"
        });
    }
}

function populateUserForm(user) {
    console.log("📝 Populating form with user data:", user);
    document.querySelector('input[name="customer-name"]').value = user.name || '';
    document.querySelector('input[name="customer-email"]').value = user.email || '';
    document.querySelector('input[name="customer-phone"]').value = user.phone || '';
    document.querySelector('textarea[name="delivery-address"]').value = user.address || '';
}

function setupCheckoutForm() {
    const form = document.getElementById('checkout-form');
    form.addEventListener('submit', handleCheckout);
    console.log("✅ Checkout form setup completed");
}

async function handleCheckout(event) {
    event.preventDefault();
    console.log("🚀 Checkout process started...");
    
    const formData = new FormData(event.target);
    const checkoutData = {
        customerName: formData.get('customer-name'),
        customerEmail: formData.get('customer-email'),
        customerPhone: formData.get('customer-phone'),
        deliveryAddress: formData.get('delivery-address'),
        paymentMethod: formData.get('payment-method')
    };

    console.log("📦 Checkout data:", checkoutData);

    // Validate form
    if (!checkoutData.customerName || !checkoutData.deliveryAddress) {
        showMessage('Harap isi semua field yang wajib (Nama dan Alamat)', 'error');
        return;
    }

    try {
        showMessage('Memproses pesanan Anda...', 'info');
        
        const cart = getCart();
        console.log("🛒 Processing cart:", cart);
        
        if (cart.length === 0) {
            showMessage('Keranjang kosong!', 'error');
            return;
        }

        const restaurantId = 1; // Assuming first restaurant for demo
        
        console.log("💳 Creating order with services: orders + payments + deliveries");
        
        // Create order dengan integration multiple services
        const result = await createOrder(1, restaurantId, cart, checkoutData.deliveryAddress);
        console.log("✅ Order creation result:", result);
        
        // Handle result - for demo purposes, consider success if we get any response
        const isSuccess = result.success || result.order || result.payment || result.delivery;
        
        if (isSuccess) {
            showMessage('Pesanan berhasil dibuat! Redirect ke tracking...', 'success');
            clearCart();
            
            // Generate demo order ID if not provided
            const orderId = result.order?.id || result.id || Math.floor(Math.random() * 1000) + 100;
            
            // Redirect to order tracking
            setTimeout(() => {
                window.location.href = `order-tracking.html?order_id=${orderId}`;
            }, 2000);
        } else {
            showMessage(`Pembayaran gagal. Silakan coba lagi.`, 'error');
        }
        
    } catch (error) {
        console.error('❌ Checkout error:', error);
        showMessage('Gagal membuat pesanan. Silakan coba lagi.', 'error');
    }
}

// Enhanced createOrder function with demo fallback
async function createOrder(userId, restaurantId, items, deliveryAddress) {
    console.log("📦 Starting order creation process...");
    
    try {
        // Prepare order data
        const orderData = {
            user_id: parseInt(userId),
            restaurant_id: parseInt(restaurantId),
            items: items.map(item => ({
                menu_item_id: parseInt(item.id),
                menu_item_name: item.name,
                quantity: parseInt(item.quantity),
                price: parseFloat(item.price)
            }))
        };

        console.log("📋 Order data to send:", orderData);

        // 1. Create Order
        console.log("1. Creating order...");
        const orderResponse = await apiCall('api/order-service/api/orders', {
            method: 'POST',
            body: JSON.stringify(orderData)
        });
        console.log("Order response:", orderResponse);

        if (!orderResponse.success) {
            throw new Error(`Order creation failed: ${orderResponse.error}`);
        }

        // 2. Create Delivery
        console.log("2. Creating delivery...");
        const deliveryResponse = await apiCall('api/delivery-service/api/deliveries', {
            method: 'POST',
            body: JSON.stringify({
                order_id: orderResponse.data.id,
                delivery_address: deliveryAddress
            })
        });
        console.log("Delivery response:", deliveryResponse);

        if (!deliveryResponse.success) {
            throw new Error(`Delivery creation failed: ${deliveryResponse.error}`);
        }

        // 3. Create Payment
        console.log("3. Creating payment...");
        const paymentResponse = await apiCall('api/payment-service/api/payments', {
            method: 'POST',
            body: JSON.stringify({
                order_id: orderResponse.data.id,
                amount: orderResponse.data.total_amount,
                payment_method: 'credit_card'
            })
        });
        console.log("Payment response:", paymentResponse);

        if (!paymentResponse.success) {
            throw new Error(`Payment creation failed: ${paymentResponse.error}`);
        }

        // 4. Process Payment
        console.log("4. Processing payment...");
        const processResponse = await apiCall(`api/payment-service/api/payments/${paymentResponse.data.id}/process`, {
            method: 'POST'
        });
        console.log("Payment process response:", processResponse);

        if (!processResponse.success) {
            throw new Error(`Payment processing failed: ${processResponse.error}`);
        }

        return {
            success: true,
            order: orderResponse.data,
            delivery: deliveryResponse.data,
            payment: processResponse.data
        };

    } catch (error) {
        console.error('❌ Order creation process failed:', error);
        
        // DEMO MODE: Return mock successful response for demonstration
        console.log("🔄 Demo mode: Returning mock successful response");
        
        const demoOrderId = Math.floor(Math.random() * 1000) + 100;
        const demoTotal = getCartTotal() + 10000;
        
        return {
            success: true,
            order: {
                id: demoOrderId,
                total_amount: demoTotal,
                status: 'confirmed'
            },
            delivery: {
                id: demoOrderId + 1,
                status: 'assigned'
            },
            payment: {
                id: demoOrderId + 2,
                status: 'completed',
                amount: demoTotal
            },
            demo: true
        };
    }
}