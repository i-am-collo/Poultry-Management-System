/**
 * Cart Module
 * Manages shopping cart state in localStorage and UI rendering
 * All calculations and API calls use real data — no hardcoding
 */

// ════════════════════════════════════════════════════════════
// CONSTANTS
// ════════════════════════════════════════════════════════════

const CART_KEY = 'pms_cart';
const VAT_RATE = 0.16;
const DELIVERY_COST = 850;

// ════════════════════════════════════════════════════════════
// CART STATE MANAGEMENT
// ════════════════════════════════════════════════════════════

/**
 * Get cart from localStorage
 */
function getCart() {
    try {
        const cartJson = localStorage.getItem(CART_KEY);
        return cartJson ? JSON.parse(cartJson) : [];
    } catch (error) {
        console.error('Error reading cart:', error);
        return [];
    }
}

/**
 * Save cart to localStorage and update badge
 */
function saveCart(items) {
    try {
        localStorage.setItem(CART_KEY, JSON.stringify(items));
        updateCartBadge();
    } catch (error) {
        console.error('Error saving cart:', error);
        showToast('Failed to save cart', 'error');
    }
}

/**
 * Add product to cart (or increment if exists)
 */
function addToCart(product, quantity) {
    try {
        quantity = parseInt(quantity) || 1;

        if (quantity < 1) {
            showToast('Quantity must be at least 1', 'error');
            return;
        }

        if (quantity > product.stock_quantity) {
            showToast(`Only ${product.stock_quantity} available in stock`, 'error');
            return;
        }

        const cart = getCart();
        const existingItem = cart.find(item => item.product_id === product.id);

        if (existingItem) {
            const newQty = existingItem.quantity + quantity;
            if (newQty > product.stock_quantity) {
                showToast(`Cannot add more — only ${product.stock_quantity} in stock`, 'error');
                return;
            }
            existingItem.quantity = newQty;
        } else {
            cart.push({
                product_id: product.id,
                name: product.name,
                seller_name: product.farmer_name || product.supplier_name || 'Unknown',
                image: product.product_image || null,
                unit_price: product.unit_price,
                unit_of_measure: product.unit_of_measure || 'unit',
                quantity: quantity,
                stock_quantity: product.stock_quantity
            });
        }

        saveCart(cart);
        renderCartDrawer();
        showToast(`${product.name} added to cart`, 'success');

    } catch (error) {
        console.error('Error adding to cart:', error);
        showToast('Failed to add to cart', 'error');
    }
}

/**
 * Remove item from cart
 */
function removeFromCart(productId) {
    const cart = getCart().filter(item => item.product_id !== productId);
    saveCart(cart);
    renderCartDrawer();
}

/**
 * Update item quantity in cart
 */
function updateCartQty(productId, newQty) {
    try {
        newQty = parseInt(newQty);

        if (newQty < 1) {
            removeFromCart(productId);
            return;
        }

        const cart = getCart();
        const item = cart.find(i => i.product_id === productId);

        if (item) {
            if (newQty > item.stock_quantity) {
                showToast(`Only ${item.stock_quantity} available`, 'error');
                return;
            }
            item.quantity = newQty;
            saveCart(cart);
            renderCartDrawer();
        }
    } catch (error) {
        console.error('Error updating cart quantity:', error);
        showToast('Failed to update quantity', 'error');
    }
}

/**
 * Clear entire cart
 */
function clearCart() {
    localStorage.removeItem(CART_KEY);
    updateCartBadge();
}

/**
 * Get total item count in cart
 */
function getCartCount() {
    return getCart().reduce((sum, item) => sum + item.quantity, 0);
}

/**
 * Calculate cart totals (subtotal, delivery, VAT, total)
 */
function getCartTotals(deliveryMethod = 'delivery') {
    const cart = getCart();
    const subtotal = cart.reduce((sum, item) => sum + (item.unit_price * item.quantity), 0);
    const delivery = deliveryMethod === 'delivery' ? DELIVERY_COST : 0;
    const subtotalPlusDel = subtotal + delivery;
    const vat = subtotalPlusDel * VAT_RATE;
    const total = subtotalPlusDel + vat;

    return {
        subtotal: parseFloat(subtotal.toFixed(2)),
        delivery: parseFloat(delivery.toFixed(2)),
        vat: parseFloat(vat.toFixed(2)),
        total: parseFloat(total.toFixed(2))
    };
}

// ════════════════════════════════════════════════════════════
// CART UI MANAGEMENT
// ════════════════════════════════════════════════════════════

/**
 * Update cart badge count in topbar
 */
function updateCartBadge() {
    const badge = document.getElementById('cart-badge');
    const count = getCartCount();

    if (count > 0) {
        badge.textContent = count;
        badge.style.display = 'inline-block';
    } else {
        badge.style.display = 'none';
    }
}

/**
 * Toggle cart drawer open/closed
 */
function toggleCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    if (drawer) {
        drawer.classList.toggle('open');
    }
}

/**
 * Close cart drawer
 */
function closeCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    if (drawer) {
        drawer.classList.remove('open');
    }
}

/**
 * Render cart drawer with items and totals
 */
function renderCartDrawer() {
    try {
        const cartItemsContainer = document.getElementById('cart-items');
        const cart = getCart();

        if (cart.length === 0) {
            cartItemsContainer.innerHTML = `
                <div class="cart-empty">
                    <div class="cart-empty-icon">🛒</div>
                    <div class="cart-empty-text">Your cart is empty</div>
                    <div class="cart-empty-sub">Start browsing to add items</div>
                </div>
            `;

            // Disable checkout
            document.getElementById('checkout-btn').disabled = true;

            return;
        }

        // Render cart items
        cartItemsContainer.innerHTML = cart.map(item => `
            <div class="cart-item">
                <div class="item-icon">
                    ${item.image ? `<img src="${item.image}" alt="${item.name}" style="width:40px;height:40px;object-fit:cover;border-radius:4px;">` : '🐔'}
                </div>
                <div class="item-info">
                    <div class="item-name">${escapeHtml(item.name)}</div>
                    <div class="item-meta">${escapeHtml(item.seller_name)} • ${escapeHtml(item.unit_of_measure)}</div>
                </div>
                <div style="display:flex;flex-direction:column;align-items:center;gap:4px;">
                    <div class="qty-stepper" style="margin:0;">
                        <button onclick="updateCartQty(${item.product_id}, ${item.quantity - 1})" style="width:20px;height:20px;padding:0;">−</button>
                        <input type="number" value="${item.quantity}" min="1" max="${item.stock_quantity}" 
                            style="width:30px;height:20px;text-align:center;border:none;border-left:1px solid var(--green-light);border-right:1px solid var(--green-light);" 
                            onchange="updateCartQty(${item.product_id}, this.value)">
                        <button onclick="updateCartQty(${item.product_id}, ${item.quantity + 1})" style="width:20px;height:20px;padding:0;">+</button>
                    </div>
                    <div class="item-price">KES ${(item.unit_price * item.quantity).toFixed(2)}</div>
                </div>
                <button class="remove-btn" onclick="removeFromCart(${item.product_id})">×</button>
            </div>
        `).join('');

        // Update totals
        const deliveryMethod = document.querySelector('input[name="delivery"]:checked')?.value || 'delivery';
        const totals = getCartTotals(deliveryMethod);

        document.getElementById('subtotal').textContent = `KES ${totals.subtotal.toFixed(2)}`;
        document.getElementById('delivery-cost').textContent = deliveryMethod === 'delivery' ? `KES ${totals.delivery.toFixed(2)}` : 'Free';
        document.getElementById('vat-cost').textContent = `KES ${totals.vat.toFixed(2)}`;
        document.getElementById('total-cost').textContent = `KES ${totals.total.toFixed(2)}`;

        // Enable checkout
        document.getElementById('checkout-btn').disabled = false;

    } catch (error) {
        console.error('Error rendering cart:', error);
        showToast('Failed to render cart', 'error');
    }
}

// ════════════════════════════════════════════════════════════
// ORDER PLACEMENT
// ════════════════════════════════════════════════════════════

/**
 * Place order with current cart items
 */
async function placeOrder() {
    try {
        const cart = getCart();

        if (cart.length === 0) {
            showToast('Your cart is empty', 'error');
            return;
        }

        const note = document.getElementById('order-note').value.trim();
        const checkoutBtn = document.getElementById('checkout-btn');

        // Disable button and show loading state
        checkoutBtn.disabled = true;
        const originalText = checkoutBtn.textContent;
        checkoutBtn.textContent = '⏳ Placing order...';

        // Create order payload
        const orderPayload = {
            items: cart.map(item => ({
                product_id: item.product_id,
                quantity: item.quantity
            })),
            note: note || null
        };

        // Call API
        const response = await api.buyer.createOrder(orderPayload);

        // Success
        clearCart();
        closeCartDrawer();
        showToast(`Order #${response.id} placed successfully!`, 'success');

        // Redirect to orders page after 1.5 seconds
        setTimeout(() => {
            window.location.href = 'buyer.html#orders';
        }, 1500);

    } catch (error) {
        console.error('Error placing order:', error);
        showToast(error.message || 'Failed to place order', 'error');

        // Re-enable button
        const checkoutBtn = document.getElementById('checkout-btn');
        checkoutBtn.disabled = false;
        checkoutBtn.textContent = 'Place Order';
    }
}

/**
 * Escape HTML for safe rendering
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container') || document.body;
    const toast = document.createElement('div');
    toast.className = `toast-message ${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 12px 16px;
        background: ${type === 'success' ? 'var(--green-mid)' :
            type === 'error' ? 'var(--red-soft)' :
                'var(--text-dark)'};
        color: white;
        border-radius: var(--radius-sm);
        font-size: 13px;
        z-index: 400;
        animation: slideIn 0.3s ease;
        box-shadow: var(--shadow-lg);
    `;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ════════════════════════════════════════════════════════════
// INITIALIZATION
// ════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    try {
        // Initialize cart display
        renderCartDrawer();
        updateCartBadge();

        // Listen for delivery method changes to update totals
        document.querySelectorAll('input[name="delivery"]').forEach(radio => {
            radio.addEventListener('change', () => {
                renderCartDrawer();
            });
        });

        // Checkout button listener
        const checkoutBtn = document.getElementById('checkout-btn');
        if (checkoutBtn) {
            checkoutBtn.addEventListener('click', placeOrder);
        }

    } catch (error) {
        console.error('Error initializing cart:', error);
    }
});

// Listen for storage changes (cart updated in another tab/window)
window.addEventListener('storage', (event) => {
    if (event.key === CART_KEY) {
        renderCartDrawer();
        updateCartBadge();
    }
});
