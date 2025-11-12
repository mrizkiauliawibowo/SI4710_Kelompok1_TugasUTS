// 🛒 CART PAGE - PANGGIL 2 SERVICES: users + restaurants
document.addEventListener('DOMContentLoaded', function() {
    console.log("🛒 Cart page loading - Integrating user data");
    loadCartPage();
});

function loadCartPage() {
    displayCartItems();
    updateCartSummary();
}

function displayCartItems() {
    const cart = getCart();
    const container = document.getElementById('cart-items');
    
    if (cart.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-shopping-cart text-4xl text-gray-300 mb-4"></i>
                <p class="text-gray-600">Keranjang Anda kosong</p>
                <a href="index.html" class="text-blue-600 hover:text-blue-700 mt-2 inline-block">
                    Mulai berbelanja →
                </a>
            </div>
        `;
        return;
    }

    const html = cart.map(item => `
        <div class="flex items-center justify-between border-b border-gray-200 pb-4">
            <div class="flex items-center space-x-4">
                <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <i class="fas fa-utensils text-blue-600"></i>
                </div>
                <div>
                    <h4 class="font-semibold">${item.name}</h4>
                    <p class="text-gray-600">${formatCurrency(item.price)}</p>
                </div>
            </div>
            
            <div class="flex items-center space-x-3">
                <button onclick="updateCartQuantity(${item.id}, ${item.quantity - 1})" 
                        class="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center hover:bg-gray-300">
                    <i class="fas fa-minus text-sm"></i>
                </button>
                
                <span class="font-semibold w-8 text-center">${item.quantity}</span>
                
                <button onclick="updateCartQuantity(${item.id}, ${item.quantity + 1})" 
                        class="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center hover:bg-gray-300">
                    <i class="fas fa-plus text-sm"></i>
                </button>
                
                <button onclick="removeFromCart(${item.id})" 
                        class="text-red-500 hover:text-red-700 ml-4">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

function updateCartSummary() {
    const subtotal = getCartTotal();
    const deliveryFee = 10000;
    const total = subtotal + deliveryFee;
    
    document.getElementById('subtotal').textContent = formatCurrency(subtotal);
    document.getElementById('delivery-fee').textContent = formatCurrency(deliveryFee);
    document.getElementById('total-amount').textContent = formatCurrency(total);
}

function proceedToCheckout() {
    const cart = getCart();
    if (cart.length === 0) {
        showMessage('Keranjang kosong', 'error');
        return;
    }
    
    window.location.href = 'checkout.html';
}