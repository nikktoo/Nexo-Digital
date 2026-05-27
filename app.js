// app.js - Lógica del Carrito Global
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// Actualiza el número rojo en el botón del carrito
function updateCartBadge() {
    const badges = document.querySelectorAll('.cart-badge');
    const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
    badges.forEach(badge => badge.innerText = totalItems);
}

// Funcion global para añadir productos
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

//PAGINA PAGO
// RENDERIZA LOS PRODUCTOS EN LA PÁGINA DE PAGO
function renderCheckout() {
    // Obtiene carrito guardado
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    // Contenedor productos
    const container = document.getElementById('checkout-items');
    // Elemento total
    const totalElement = document.getElementById('checkout-total');
    // Texto despacho
    const shippingElement = document.getElementById('shipping-price');
    // Método entrega seleccionado
    const selectedDelivery =
        document.querySelector('input[name="delivery"]:checked')?.value;
    // Costo despacho
    let shippingCost = 0;
    // Si es despacho
    if(selectedDelivery === "delivery"){
        shippingCost = 10990;
    }
    // Si no existe página
    if (!container || !totalElement) return;
    // Limpia contenido
    container.innerHTML = "";
    // Total productos
    let total = 0;
    // Si carrito vacío
    if(cart.length === 0){
        container.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="bi bi-cart-x fs-1"></i>
                <p class="mt-3">
                    Tu carrito está vacío
                </p>
            </div>
        `;
        return;
    }
    // Recorre productos
    cart.forEach(item => {
        // Subtotal producto
        const subtotal = item.price * item.quantity;
        // Suma subtotal
        total += subtotal;
        // Inserta producto
        container.innerHTML += `
            <div class="d-flex align-items-center mb-3 pb-3 border-bottom">
                <img src="${item.image}"
                     class="rounded me-3"
                     width="70"
                     height="70"
                     style="object-fit: cover;">
                <div class="flex-grow-1">
                    <h6 class="fw-bold mb-1">
                        ${item.name}
                    </h6>
                    <small class="text-muted">
                        Cantidad: ${item.quantity}
                    </small>
                </div>
                <div class="fw-bold text-primary">
                    $${subtotal.toFixed(2)}
                </div>
            </div>
        `;
    });
    // Suma despacho
    total += shippingCost;
    // Muestra despacho
    if(shippingElement){
        shippingElement.innerText =
            shippingCost === 0
            ? "Gratis"
            : "$" + shippingCost.toFixed(2);
    }
    // Muestra total final
    totalElement.innerText = total.toFixed(2);
}
// MOSTRAR / OCULTAR CAMPOS DE TARJETA
function togglePaymentFields(){
    // Método seleccionado
    const selectedPayment =
        document.querySelector('input[name="payment"]:checked').value;
    // Campos tarjeta
    const cardFields =
        document.getElementById('card-fields');
    // Si no existen
    if(!cardFields) return;
    // Oculta o muestra
    if(selectedPayment === "paypal"){
        cardFields.style.display = "none";
    } else {
        cardFields.style.display = "block";
    }
}
// MOSTRAR / OCULTAR DIRECCIÓN
function toggleDeliveryFields(){
    // Método entrega
    const selectedDelivery =
        document.querySelector('input[name="delivery"]:checked').value;
    // Dirección
    const addressField =
        document.getElementById('address-field');
    // Si no existe
    if(!addressField) return;
    // Oculta o muestra
    if(selectedDelivery === "pickup"){
        addressField.style.display = "none";
    } else {
        addressField.style.display = "block";
    }
    // Actualiza resumen
    renderCheckout();
}
// AL CARGAR PÁGINA
document.addEventListener('DOMContentLoaded', () => {
    // Actualiza badge
    updateCartBadge();
    // Renderiza carrito lateral
    renderCart();
    // Renderiza checkout
    renderCheckout();
    // Verifica pago
    togglePaymentFields();
    // Verifica entrega
    toggleDeliveryFields();
});