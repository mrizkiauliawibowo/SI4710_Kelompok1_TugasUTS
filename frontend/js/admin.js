// ⚙️ ADMIN DASHBOARD - PANGGIL SEMUA SERVICES
document.addEventListener('DOMContentLoaded', function() {
    console.log("⚙️ Admin dashboard loading - Integrating all services");
    loadAdminDashboard();
});

async function loadAdminDashboard() {
    try {
        // Load all services data concurrently
        const [
            usersResponse,
            restaurantsResponse, 
            ordersResponse,
            deliveriesResponse,
            healthResponse
        ] = await Promise.all([
            apiCall('users/api/users'),
            apiCall('restaurants/api/restaurants'),
            apiCall('orders/api/orders'),
            apiCall('deliveries/api/deliveries'),
            apiCall('health')
        ]);

        console.log("✅ Successfully loaded data from all services");

        // Update statistics
        updateStatistics(
            usersResponse,
            restaurantsResponse,
            ordersResponse,
            deliveriesResponse
        );

        // Update services health
        updateServicesHealth(healthResponse);

        // Update recent data
        updateRecentData(ordersResponse);

    } catch (error) {
        console.error('❌ Error loading admin dashboard:', error);
        showMessage('Error loading dashboard data', 'error');
    }
}

function updateStatistics(users, restaurants, orders, deliveries) {
    // Users count
    if (users.success) {
        document.getElementById('users-count').textContent = users.count || users.data?.length || 0;
    }

    // Restaurants count
    if (restaurants.success) {
        document.getElementById('restaurants-count').textContent = restaurants.count || restaurants.data?.length || 0;
    }

    // Orders count
    if (orders.success) {
        document.getElementById('orders-count').textContent = orders.count || orders.data?.length || 0;
    }

    // Active deliveries count
    if (deliveries.success) {
        const activeDeliveries = deliveries.data?.filter(d => 
            d.status !== 'delivered' && d.status !== 'cancelled'
        ).length || 0;
        document.getElementById('deliveries-count').textContent = activeDeliveries;
    }
}

function updateServicesHealth(healthResponse) {
    const container = document.getElementById('services-health');
    
    if (!healthResponse.success || !healthResponse.services) {
        container.innerHTML = `
            <div class="text-center py-4">
                <p class="text-red-600">Gagal memuat status services</p>
            </div>
        `;
        return;
    }

    const services = [
        { name: 'API Gateway', key: 'api-gateway', port: 5000 },
        { name: 'User Service', key: 'users', port: 5001 },
        { name: 'Restaurant Service', key: 'restaurants', port: 5002 },
        { name: 'Order Service', key: 'orders', port: 5003 },
        { name: 'Delivery Service', key: 'deliveries', port: 5004 },
        { name: 'Payment Service', key: 'payments', port: 5005 }
    ];

    const html = services.map(service => {
        const status = healthResponse.services[service.key];
        const isHealthy = status && status.status === 'healthy';
        
        return `
            <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div class="flex items-center space-x-3">
                    <div class="w-3 h-3 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-500'}"></div>
                    <div>
                        <p class="font-medium">${service.name}</p>
                        <p class="text-sm text-gray-500">Port ${service.port}</p>
                    </div>
                </div>
                <span class="px-2 py-1 rounded text-sm ${isHealthy ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                    ${isHealthy ? 'Healthy' : 'Unhealthy'}
                </span>
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}

function updateRecentData(ordersResponse) {
    const container = document.getElementById('recent-orders');
    
    if (!ordersResponse.success || !ordersResponse.data || ordersResponse.data.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4">
                <p class="text-gray-600">Tidak ada pesanan</p>
            </div>
        `;
        return;
    }

    const recentOrders = ordersResponse.data.slice(0, 5); // Get 5 most recent orders
    
    const html = recentOrders.map(order => `
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
                <p class="font-medium">Order #${order.id}</p>
                <p class="text-sm text-gray-500">${formatDateTime(order.created_at)}</p>
            </div>
            <div class="text-right">
                <p class="font-semibold">${formatCurrency(order.total_amount)}</p>
                ${getStatusBadge(order.status)}
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}