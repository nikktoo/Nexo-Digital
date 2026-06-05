let cart = JSON.parse(localStorage.getItem('cart')) || [];
function getCart() {
    return JSON.parse(localStorage.getItem('cart')) || [];
}
function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}
function updateCartBadge() {
    const badges = document.querySelectorAll('.cart-badge');
    const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
    badges.forEach(badge => badge.innerText = totalItems);
}
window.addToCart = function (id, name, price, image) {
    const existingItem = cart.find(item => item.id === id);
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({ id, name, price, image, quantity: 1 });
    }
    saveCart();
    updateCartBadge();
    renderCart();
    const offcanvasElement = document.getElementById('offcanvasCart');
    if (offcanvasElement) {
        const bsOffcanvas =
            bootstrap.Offcanvas.getInstance(offcanvasElement) ||
            new bootstrap.Offcanvas(offcanvasElement);
        bsOffcanvas.show();
    }
};
function renderCart() {
    const container = document.getElementById('cart-items-container');
    const totalElement = document.getElementById('cart-total');
    if (!container) return;
    const cart = getCart();
    container.innerHTML = '';
    let total = 0;
    if (cart.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5 text-muted">
                <i class="bi bi-cart-x fs-1"></i>
                <p>Tu carrito está vacío</p>
            </div>
        `;
        if (totalElement) totalElement.innerText = '0';
        return;
    }
    cart.forEach((item) => {
        const subtotal = item.price * item.quantity;
        total += subtotal;
        container.innerHTML += `
            <div class="d-flex align-items-center mb-3 pb-3 border-bottom">
                <img src="${item.image}" class="rounded me-3" style="width:50px;height:50px;object-fit:cover;">
                <div class="flex-grow-1">
                    <h6 class="mb-0 small fw-bold">${item.name}</h6>
                    <div class="d-flex align-items-center mt-1">
                        <button class="btn btn-sm btn-light border px-2 py-0"
                            onclick="updateQuantity('${item.id}', ${item.quantity - 1})">-</button>
                        <span class="mx-2 small">${item.quantity}</span>
                        <button class="btn btn-sm btn-light border px-2 py-0"
                            onclick="updateQuantity('${item.id}', ${item.quantity + 1})">+</button>
                    </div>
                </div>
                <div class="text-end">
                    <span class="fw-bold small d-block">
                        $${subtotal.toLocaleString('es-CL')}
                    </span>
                    <button class="btn btn-sm text-danger p-0"
                        onclick="removeFromCart('${item.id}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    if (totalElement) {
        totalElement.innerText = total.toLocaleString('es-CL');
    }
}
window.updateQuantity = function (id, newQty) {
    const item = cart.find(p => p.id === id);
    if (!item) return;
    if (newQty > 0) {
        item.quantity = newQty;
    } else {
        cart = cart.filter(p => p.id !== id);
    }
    saveCart();
    refresh();
};
window.removeFromCart = function (id) {
    cart = cart.filter(item => item.id !== id);
    saveCart();
    refresh();
};
function refresh() {
    updateCartBadge();
    renderCart();
    renderCheckout();
}
function renderCheckout() {
    const cart = getCart();
    const container = document.getElementById('checkout-items');
    const totalElement = document.getElementById('checkout-total');
    const shippingElement = document.getElementById('shipping-price');
    if (!container || !totalElement) return;
    container.innerHTML = '';
    if (cart.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="bi bi-cart-x fs-1"></i>
                <p class="mt-3">Tu carrito está vacío</p>
            </div>
        `;
        totalElement.innerText = '0';
        return;
    }
    let total = 0;
    cart.forEach(item => {
        const subtotal = item.price * item.quantity;
        total += subtotal;
        container.innerHTML += `
            <div class="d-flex align-items-center mb-3 pb-3 border-bottom">
                <img src="${item.image}" width="70" height="70"
                    class="rounded me-3" style="object-fit:cover;">
                <div class="flex-grow-1">
                    <h6 class="fw-bold mb-1">${item.name}</h6>
                    <small class="text-muted">Cantidad: ${item.quantity}</small>
                </div>
                <div class="fw-bold text-primary">
                    $${subtotal.toLocaleString('es-CL')}
                </div>
            </div>
        `;
    });
    const delivery = document.querySelector('input[name="delivery"]:checked')?.value;
    let shippingCost = delivery === "delivery" ? 10990 : 0;
    if (shippingElement) {
        shippingElement.innerText =
            shippingCost === 0
                ? "Gratis"
                : "$" + shippingCost.toLocaleString('es-CL');
    }
    total += shippingCost;
    totalElement.innerText = total.toLocaleString('es-CL');
}
function togglePaymentFields() {
    const method = document.querySelector('input[name="payment"]:checked')?.value;
    const cardFields = document.getElementById('card-fields');
    if (!cardFields) return;
    cardFields.style.display = method === "paypal" ? "none" : "block";
}
function toggleDeliveryFields() {
    const method = document.querySelector('input[name="delivery"]:checked')?.value;
    const address = document.getElementById('address-field');
    if (!address) return;
    address.style.display = method === "pickup" ? "none" : "block";
    renderCheckout();
}
document.addEventListener('DOMContentLoaded', () => {
    updateCartBadge();
    renderCart();
    renderCheckout();
    togglePaymentFields();
    toggleDeliveryFields();
});