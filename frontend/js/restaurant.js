// 🍕 RESTAURANT PAGE - PANGGIL 2 SERVICES: restaurants + orders
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const restaurantId = urlParams.get('id');
    
    if (restaurantId) {
        console.log(`🍕 Loading restaurant ${restaurantId} - Integrating 2 services`);
        loadRestaurantData(restaurantId);
    } else {
        showMessage('Restaurant tidak ditemukan', 'error');
        setTimeout(() => window.location.href = 'index.html', 2000);
    }
});

async function loadRestaurantData(restaurantId) {
    try {
        showMessage('Memuat data restoran...', 'info');
        
        // ✅ PANGGIL 2 SERVICES: restaurants + orders
        const [restaurantResponse, ordersResponse] = await Promise.all([
            apiCall(`restaurants/api/restaurants/${restaurantId}`), // Service: restaurants (rizki)
            apiCall('orders/api/orders')                           // Service: orders (Nadia)
        ]);

        console.log("✅ Successfully called 2 services through API Gateway");

        if (restaurantResponse.success) {
            displayRestaurantDetails(restaurantResponse.data);
            displayMenu(restaurantResponse.data.menu || []);
            console.log("📊 Restaurant data loaded successfully");
        } else {
            showMessage('Gagal memuat data restoran', 'error');
        }

        if (ordersResponse.success) {
            // Data orders bisa digunakan untuk analytics atau popular items
            console.log(`📦 Loaded ${ordersResponse.data?.length || 0} orders`);
        }
        
    } catch (error) {
        console.error('❌ Error loading restaurant:', error);
        showMessage('Error loading restaurant data', 'error');
    }
}

function displayRestaurantDetails(restaurant) {
    document.getElementById('restaurant-title').textContent = restaurant.name;
    document.getElementById('restaurant-name').textContent = restaurant.name;
    document.getElementById('restaurant-address').innerHTML = `
        <i class="fas fa-map-marker-alt mr-2 text-blue-600"></i>
        ${restaurant.address || 'Alamat tidak tersedia'}
    `;
    document.getElementById('restaurant-cuisine').textContent = restaurant.cuisine_type || 'Berbagai Masakan';
}

function displayMenu(menuItems) {
    const container = document.getElementById('menu-list');
    
    if (!menuItems || menuItems.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-utensils text-4xl text-gray-400 mb-4"></i>
                <p class="text-gray-600">Menu tidak tersedia</p>
            </div>
        `;
        return;
    }

    const html = menuItems.map(item => `
        <div class="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md transition">
            <div class="flex justify-between items-start">
                <div class="flex-1">
                    <h4 class="font-bold text-gray-800">${item.name}</h4>
                    <p class="text-gray-600 text-sm mt-1">${item.description || 'Makanan lezat'}</p>
                    <p class="text-green-600 font-semibold mt-2">${formatCurrency(item.price || 25000)}</p>
                </div>
                <button onclick="addToCart({
                    id: ${item.id},
                    name: '${item.name}',
                    price: ${item.price || 25000},
                    restaurant_id: ${item.restaurant_id}
                })" 
                        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition ml-4">
                    <i class="fas fa-plus mr-1"></i>Tambah
                </button>
            </div>
            <div class="mt-2 text-xs text-gray-400">
                Source: Restaurant Service (5002)
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}