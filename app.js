// app.js - Lógica del Carrito Global
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// Actualiza el número rojo en el botón del carrito
function updateCartBadge() {
    const badges = document.querySelectorAll('.cart-badge');
    const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
    badges.forEach(badge => badge.innerText = totalItems);
}

// Función global para añadir productos
window.addToCart = function(id, name, price, image) {
    const existingItem = cart.find(item => item.id === id);
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ id, name, price, image, quantity: 1 });
    }
    
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartBadge();
    renderCart();

    // Abre automáticamente el panel del carrito al agregar algo
    const offcanvasElement = document.getElementById('offcanvasCart');
    const bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvasElement) || new bootstrap.Offcanvas(offcanvasElement);
    bsOffcanvas.show();
};

// Dibuja los productos dentro del panel lateral
function renderCart() {
    const container = document.getElementById('cart-items-container');
    const totalElement = document.getElementById('cart-total');
    if (!container) return;

    container.innerHTML = '';
    let total = 0;

    if (cart.length === 0) {
        container.innerHTML = '<div class="text-center py-5 text-muted"><i class="bi bi-cart-x fs-1"></i><p>Tu carrito está vacío</p></div>';
        if (totalElement) totalElement.innerText = '0';
        return;
    }

    cart.forEach((item, index) => {
        const subtotal = item.price * item.quantity;
        total += subtotal;
        container.innerHTML += `
            <div class="d-flex align-items-center mb-3 pb-3 border-bottom">
                <img src="${item.image}" alt="${item.name}" style="width: 50px; height: 50px; object-fit: cover;" class="rounded me-3">
                <div class="flex-grow-1">
                    <h6 class="mb-0 small fw-bold">${item.name}</h6>
                    <div class="d-flex align-items-center mt-1">
                        <button class="btn btn-sm btn-light border py-0 px-2" onclick="updateQuantity(${index}, ${item.quantity - 1})">-</button>
                        <span class="mx-2 small">${item.quantity}</span>
                        <button class="btn btn-sm btn-light border py-0 px-2" onclick="updateQuantity(${index}, ${item.quantity + 1})">+</button>
                    </div>
                </div>
                <div class="text-end">
                    <span class="d-block fw-bold small">$${subtotal.toFixed(2)}</span>
                    <button class="btn btn-sm text-danger p-0" onclick="removeFromCart(${index})"><i class="bi bi-trash"></i></button>
                </div>
            </div>`;
    });
    
    if (totalElement) totalElement.innerText = total.toFixed(2);
}

window.updateQuantity = function(index, newQty) {
    if (newQty > 0) cart[index].quantity = newQty;
    else cart.splice(index, 1);
    saveAndRefresh();
};

window.removeFromCart = function(index) {
    cart.splice(index, 1);
    saveAndRefresh();
};

function saveAndRefresh() {
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartBadge();
    renderCart();
}

document.addEventListener('DOMContentLoaded', () => {
    updateCartBadge();
    renderCart();
});