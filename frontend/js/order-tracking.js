// 📱 ORDER TRACKING - PANGGIL 2 SERVICES: orders + deliveries
document.addEventListener('DOMContentLoaded', function() {
    console.log("📱 Order tracking loading - Integrating orders + deliveries services");
    loadOrderTrackingData();
});

async function loadOrderTrackingData() {
    try {
        showMessage('Memuat data pesanan...', 'info');
        
        // ✅ PANGGIL 2 SERVICES: orders + deliveries
        const [ordersResponse, deliveriesResponse] = await Promise.all([
            apiCall('orders/api/orders'),      // Service: orders (Nadia)
            apiCall('deliveries/api/deliveries') // Service: deliveries (aydin)
        ]);

        console.log("✅ Successfully called 2 services through API Gateway");

        if (ordersResponse.success && deliveriesResponse.success) {
            displayOrderTracking(ordersResponse.data, deliveriesResponse.data);
            console.log("📊 Order tracking data loaded successfully");
        } else {
            showMessage('Gagal memuat data pesanan', 'error');
        }
        
    } catch (error) {
        console.error('❌ Error loading order tracking:', error);
        showMessage('Error loading order data', 'error');
    }
}

function displayOrderTracking(orders, deliveries) {
    displayActiveOrders(orders, deliveries);
    displayOrderHistory(orders);
}

function displayActiveOrders(orders, deliveries) {
    const container = document.getElementById('active-orders');
    const activeOrders = orders.filter(order => 
        order.status !== 'delivered' && order.status !== 'cancelled'
    );
    
    if (activeOrders.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-box-open text-4xl text-gray-300 mb-4"></i>
                <p class="text-gray-600">Tidak ada pesanan aktif</p>
            </div>
        `;
        return;
    }

    const html = activeOrders.map(order => {
        const delivery = deliveries.find(d => d.order_id === order.id);
        return `
            <div class="border border-gray-200 rounded-xl p-4">
                <div class="flex justify-between items-start mb-3">
                    <div>
                        <h4 class="font-bold">Order #${order.id}</h4>
                        <p class="text-gray-600 text-sm">${formatDateTime(order.created_at)}</p>
                    </div>
                    ${getStatusBadge(order.status)}
                </div>
                
                <div class="space-y-2">
                    <div class="flex justify-between">
                        <span>Total</span>
                        <span class="font-semibold">${formatCurrency(order.total_amount)}</span>
                    </div>
                    
                    ${delivery ? `
                    <div class="flex justify-between">
                        <span>Status Pengiriman</span>
                        <span class="font-semibold">${delivery.status}</span>
                    </div>
                    
                    ${delivery.delivery_person_name ? `
                    <div class="flex justify-between">
                        <span>Kurir</span>
                        <span>${delivery.delivery_person_name}</span>
                    </div>
                    ` : ''}
                    
                    ${delivery.estimated_delivery_time ? `
                    <div class="flex justify-between">
                        <span>Estimasi Tiba</span>
                        <span>${formatDateTime(delivery.estimated_delivery_time)}</span>
                    </div>
                    ` : ''}
                    ` : ''}
                </div>
                
                <div class="mt-3 text-xs text-gray-400">
                    Integrated: Order Service + Delivery Service
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}

function displayOrderHistory(orders) {
    const container = document.getElementById('order-history');
    const completedOrders = orders.filter(order => 
        order.status === 'delivered' || order.status === 'cancelled'
    );
    
    if (completedOrders.length === 0) {
        return; // Keep the default empty state
    }

    const html = completedOrders.map(order => `
        <div class="border border-gray-200 rounded-xl p-4">
            <div class="flex justify-between items-start">
                <div>
                    <h4 class="font-bold">Order #${order.id}</h4>
                    <p class="text-gray-600 text-sm">${formatDateTime(order.created_at)}</p>
                </div>
                ${getStatusBadge(order.status)}
            </div>
            
            <div class="flex justify-between mt-2">
                <span>Total</span>
                <span class="font-semibold">${formatCurrency(order.total_amount)}</span>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}