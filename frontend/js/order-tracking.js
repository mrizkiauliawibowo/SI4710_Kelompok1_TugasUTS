// 📱 ORDER TRACKING - PANGGIL 2 SERVICES: orders + deliveries
document.addEventListener('DOMContentLoaded', function() {
    console.log("📱 Order tracking loading - Integrating orders + deliveries services");
    
    // Check for order_id parameter in URL
    const urlParams = new URLSearchParams(window.location.search);
    const orderId = urlParams.get('order_id');
    
    if (orderId) {
        loadSingleOrder(orderId);
    } else {
        loadOrderTrackingData();
    }
});

async function loadSingleOrder(orderId) {
    try {
        showMessage(`Memuat pesanan #${orderId}...`, 'info');
        
        // Try to get specific order
        const orderResponse = await apiCall(`api/order-service/api/orders/${orderId}`);
        
        if (orderResponse.success) {
            displaySingleOrder(orderResponse.data);
        } else {
            // Demo mode - create mock order data
            displaySingleOrder({
                id: parseInt(orderId),
                status: 'confirmed',
                total_amount: getCartTotal() + 10000,
                created_at: new Date().toISOString(),
                delivery_address: 'Jl. Contoh No. 123, Jakarta',
                customer_name: 'John Doe'
            });
        }
        
    } catch (error) {
        console.error('❌ Error loading single order:', error);
        // Demo mode
        displaySingleOrder({
            id: parseInt(orderId),
            status: 'confirmed',
            total_amount: getCartTotal() + 10000,
            created_at: new Date().toISOString(),
            delivery_address: 'Jl. Contoh No. 123, Jakarta',
            customer_name: 'John Doe'
        });
    }
}

async function loadOrderTrackingData() {
    try {
        showMessage('Memuat data pesanan...', 'info');
        
        // ✅ PANGGIL 2 SERVICES: orders + deliveries
        const [ordersResponse, deliveriesResponse] = await Promise.all([
            apiCall('api/order-service/api/orders'),      // Service: orders (Nadia)
            apiCall('api/delivery-service/api/deliveries') // Service: deliveries (aydin)
        ]);

        console.log("✅ Successfully called 2 services through API Gateway");

        if (ordersResponse.success && deliveriesResponse.success) {
            displayOrderTracking(ordersResponse.data, deliveriesResponse.data);
            console.log("📊 Order tracking data loaded successfully");
        } else {
            // Demo mode
            console.log("🔄 Demo mode: Using mock data");
            loadDemoData();
        }
        
    } catch (error) {
        console.error('❌ Error loading order tracking:', error);
        // Demo mode
        console.log("🔄 Demo mode: Using mock data due to error");
        loadDemoData();
    }
}

function displaySingleOrder(order) {
    const container = document.getElementById('active-orders');
    const historyContainer = document.getElementById('order-history');
    
    // Update main heading
    const heading = document.querySelector('h2');
    if (heading) {
        heading.textContent = `Tracking Pesanan #${order.id}`;
    }
    
    const statusColors = {
        'pending': 'bg-yellow-100 text-yellow-800',
        'confirmed': 'bg-blue-100 text-blue-800',
        'preparing': 'bg-orange-100 text-orange-800',
        'picked_up': 'bg-purple-100 text-purple-800',
        'on_the_way': 'bg-blue-100 text-blue-800',
        'delivered': 'bg-green-100 text-green-800',
        'cancelled': 'bg-red-100 text-red-800'
    };
    
    const statusLabels = {
        'pending': 'Menunggu Konfirmasi',
        'confirmed': 'Dikonfirmasi',
        'preparing': 'Sedang Dimasak',
        'picked_up': 'Diambil Driver',
        'on_the_way': 'Dalam Perjalanan',
        'delivered': 'Telah Dibutuhkan',
        'cancelled': 'Dibatalkan'
    };
    
    container.innerHTML = `
        <div class="border border-gray-200 rounded-xl p-6">
            <div class="flex justify-between items-start mb-4">
                <div>
                    <h3 class="text-xl font-bold">Order #${order.id}</h3>
                    <p class="text-gray-600">${formatDateTime(order.created_at)}</p>
                </div>
                <span class="px-3 py-1 rounded-full text-sm font-medium ${statusColors[order.status] || 'bg-gray-100 text-gray-800'}">
                    ${statusLabels[order.status] || order.status}
                </span>
            </div>
            
            <div class="space-y-3 mb-6">
                <div class="flex justify-between">
                    <span class="text-gray-600">Pelanggan</span>
                    <span class="font-medium">${order.customer_name || 'John Doe'}</span>
                </div>
                
                <div class="flex justify-between">
                    <span class="text-gray-600">Alamat Pengiriman</span>
                    <span class="font-medium">${order.delivery_address}</span>
                </div>
                
                <div class="flex justify-between">
                    <span class="text-gray-600">Total Pembayaran</span>
                    <span class="font-bold text-lg">${formatCurrency(order.total_amount)}</span>
                </div>
            </div>
            
            <div class="bg-gray-50 rounded-lg p-4 mb-4">
                <h4 class="font-semibold mb-2">Status Pesanan</h4>
                <div class="space-y-2">
                    ${getStatusProgress(order.status)}
                </div>
            </div>
            
            <div class="flex space-x-3">
                <button onclick="location.reload()" class="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700">
                    <i class="fas fa-sync mr-2"></i>Refresh
                </button>
                <a href="index.html" class="flex-1 bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 text-center">
                    <i class="fas fa-home mr-2"></i>Beranda
                </a>
            </div>
            
            <div class="mt-4 text-xs text-gray-400 text-center">
                Demo Mode - Service integration ready
            </div>
        </div>
    `;
    
    // Hide history section for single order view
    if (historyContainer) {
        historyContainer.style.display = 'none';
    }
}

function getStatusProgress(currentStatus) {
    const statuses = [
        { key: 'pending', label: 'Pesanan Diterima', icon: 'fa-clock' },
        { key: 'confirmed', label: 'Konfirmasi', icon: 'fa-check-circle' },
        { key: 'preparing', label: 'Dimasak', icon: 'fa-utensils' },
        { key: 'picked_up', label: 'Diambil Driver', icon: 'fa-motorcycle' },
        { key: 'on_the_way', label: 'Dalam Perjalanan', icon: 'fa-truck' },
        { key: 'delivered', label: 'Tersampaikan', icon: 'fa-home' }
    ];
    
    const currentIndex = statuses.findIndex(s => s.key === currentStatus);
    
    return statuses.map((status, index) => {
        const isCompleted = index <= currentIndex;
        const isCurrent = index === currentIndex;
        
        return `
            <div class="flex items-center ${isCompleted ? 'text-green-600' : 'text-gray-400'}">
                <i class="fas ${status.icon} mr-3 ${isCompleted ? '' : 'text-gray-300'}"></i>
                <span class="${isCurrent ? 'font-semibold' : ''}">${status.label}</span>
                ${isCurrent ? '<span class="ml-2 text-xs">(current)</span>' : ''}
            </div>
        `;
    }).join('');
}

function loadDemoData() {
    // Generate demo order data
    const demoOrders = [
        {
            id: 101,
            status: 'on_the_way',
            total_amount: 85000,
            created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
            delivery_address: 'Jl. Sudirman No. 123, Jakarta Pusat'
        },
        {
            id: 102,
            status: 'delivered',
            total_amount: 125000,
            created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
            delivery_address: 'Jl. Thamrin No. 456, Jakarta Pusat'
        }
    ];
    
    const demoDeliveries = [
        {
            order_id: 101,
            status: 'picked_up',
            delivery_person_name: 'Budi Santoso',
            estimated_delivery_time: new Date(Date.now() + 15 * 60 * 1000).toISOString()
        },
        {
            order_id: 102,
            status: 'delivered',
            delivery_person_name: 'Siti Nurhaliza',
            estimated_delivery_time: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
        }
    ];
    
    displayOrderTracking(demoOrders, demoDeliveries);
    showMessage('Demo data loaded - Services not available', 'warning');
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

function getStatusBadge(status) {
    const statusColors = {
        'pending': 'bg-yellow-100 text-yellow-800',
        'confirmed': 'bg-blue-100 text-blue-800',
        'preparing': 'bg-orange-100 text-orange-800',
        'picked_up': 'bg-purple-100 text-purple-800',
        'on_the_way': 'bg-blue-100 text-blue-800',
        'delivered': 'bg-green-100 text-green-800',
        'cancelled': 'bg-red-100 text-red-800'
    };
    
    const statusLabels = {
        'pending': 'Pending',
        'confirmed': 'Confirmed',
        'preparing': 'Preparing',
        'picked_up': 'Picked Up',
        'on_the_way': 'On The Way',
        'delivered': 'Delivered',
        'cancelled': 'Cancelled'
    };
    
    return `<span class="px-2 py-1 rounded-full text-xs font-medium ${statusColors[status] || 'bg-gray-100 text-gray-800'}">${statusLabels[status] || status}</span>`;
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('id-ID', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}