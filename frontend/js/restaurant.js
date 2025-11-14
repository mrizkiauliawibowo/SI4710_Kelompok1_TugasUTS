// 🍕 RESTAURANT PAGE - PANGGIL 2 SERVICES: restaurants + orders
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const restaurantId = urlParams.get('id');
    
    if (restaurantId) {
        console.log(`🍕 Loading restaurant ${restaurantId} - Integrating 2 services`);
        loadRestaurantData(restaurantId);
        updateFloatingCartCount();
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
            apiCall(`api/restaurant-service/api/restaurants/${restaurantId}`), // Service: restaurants (rizki)
            apiCall('api/order-service/api/orders')                           // Service: orders (Nadia)
        ]);

        console.log("✅ Successfully called 2 services through API Gateway");

        if (restaurantResponse.success) {
            displayRestaurantDetails(restaurantResponse.data);
            displayMenu(restaurantResponse.data.menu || []);
            console.log("📊 Restaurant data loaded successfully");
        } else {
            showMessage('Gagal memuat data restoran', 'error');
            // Fallback to sample data
            displayRestaurantDetails(getSampleRestaurant());
            displayMenu(getSampleMenu());
        }

        if (ordersResponse.success) {
            // Data orders bisa digunakan untuk analytics atau popular items
            console.log(`📦 Loaded ${ordersResponse.data?.length || 0} orders`);
        }
        
    } catch (error) {
        console.error('❌ Error loading restaurant:', error);
        showMessage('Error loading restaurant data', 'error');
        // Fallback to sample data
        displayRestaurantDetails(getSampleRestaurant());
        displayMenu(getSampleMenu());
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
    
    if (restaurant.phone) {
        document.getElementById('restaurant-phone').innerHTML = `
            <i class="fas fa-phone mr-1"></i>${restaurant.phone}
        `;
    }
}

function displayMenu(menuItems) {
    const container = document.getElementById('menu-list');
    
    if (!menuItems || menuItems.length === 0) {
        container.innerHTML = `
            <div class="col-span-2 text-center py-8">
                <i class="fas fa-utensils text-4xl text-gray-400 mb-4"></i>
                <p class="text-gray-600">Menu tidak tersedia</p>
            </div>
        `;
        return;
    }

    const html = menuItems.map(item => `
        <div class="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md transition menu-item">
            <div class="flex justify-between items-start mb-3">
                <div class="flex-1">
                    <h4 class="font-bold text-gray-800 text-lg">${item.name}</h4>
                    <p class="text-gray-600 text-sm mt-1">${item.description || 'Makanan lezat dan nikmat'}</p>
                    
                    <div class="flex items-center mt-2 space-x-2">
                        <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                            ${item.category || 'Main Course'}
                        </span>
                        ${item.is_available ? 
                            '<span class="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">Tersedia</span>' : 
                            '<span class="bg-red-100 text-red-800 px-2 py-1 rounded text-xs">Habis</span>'
                        }
                    </div>
                </div>
            </div>
            
            <div class="flex justify-between items-center">
                <p class="text-green-600 font-semibold text-lg">${formatCurrency(item.price || 25000)}</p>
                <button onclick="addToCart({
                    id: ${item.id},
                    name: '${item.name}',
                    price: ${item.price || 25000},
                    description: '${item.description || ''}',
                    category: '${item.category || 'Main Course'}'
                })" 
                        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center space-x-2"
                        ${!item.is_available ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : ''}>
                    <i class="fas fa-plus"></i>
                    <span>${item.is_available ? 'Tambah' : 'Habis'}</span>
                </button>
            </div>
            
            <div class="mt-2 text-xs text-gray-400 flex justify-between">
                <span>Source: Restaurant Service (5002)</span>
                <span>ID: ${item.id}</span>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

function updateFloatingCartCount() {
    const cart = getCart();
    const totalItems = cart.reduce((sum, item) => sum + (item.quantity || 1), 0);
    const floatingCart = document.getElementById('floating-cart-count');
    
    if (floatingCart) {
        if (totalItems > 0) {
            floatingCart.textContent = totalItems;
            floatingCart.classList.remove('hidden');
        } else {
            floatingCart.textContent = '0';
        }
    }
}

// Sample data for fallback
function getSampleRestaurant() {
    return {
        name: "Restoran Padang Sederhana",
        address: "Jl. Merdeka No. 123, Jakarta",
        cuisine_type: "Padang",
        phone: "021-1234567"
    };
}

function getSampleMenu() {
    return [
        {
            id: 1,
            name: "Rendang",
            description: "Daging sapi dimasak dengan bumbu rempah khas Padang",
            price: 35000,
            category: "Main Course",
            is_available: true
        },
        {
            id: 2,
            name: "Ayam Pop",
            description: "Ayam kampung dimasak dengan bumbu khas",
            price: 28000,
            category: "Main Course", 
            is_available: true
        },
        {
            id: 3,
            name: "Gulai Ikan",
            description: "Ikan kakap dalam kuah gulai yang gurih",
            price: 32000,
            category: "Main Course",
            is_available: true
        },
        {
            id: 4,
            name: "Es Teh Manis",
            description: "Minuman segar untuk teman makan",
            price: 8000,
            category: "Minuman",
            is_available: true
        }
    ];
}

// Override addToCart untuk update floating cart
const originalAddToCart = window.addToCart;
window.addToCart = function(item) {
    originalAddToCart(item);
    updateFloatingCartCount();
};