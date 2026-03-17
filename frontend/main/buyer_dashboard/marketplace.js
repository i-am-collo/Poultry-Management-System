/**
 * Marketplace Module
 * Handles product discovery, filtering, and product details
 * All data sourced from backend API — no hardcoded product data
 */

// ════════════════════════════════════════════════════════════
// CONSTANTS
// ════════════════════════════════════════════════════════════

const PAGE_LIMIT = 20;
const STOCK_POLL_INTERVAL = 30000; // 30 seconds

// ════════════════════════════════════════════════════════════
// STATE OBJECT (Single source of truth)
// ════════════════════════════════════════════════════════════

const state = {
    filters: {
        search: '',
        category: 'All',
        source: 'all',
        min_price: null,
        max_price: null,
        in_stock: false
    },
    currentPage: 1,
    totalPages: 1,
    totalProducts: 0,
    loading: false,
    stockPollInterval: null
};

// ════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ════════════════════════════════════════════════════════════

/**
 * Debounce function to limit API calls
 */
function debounce(func, delay) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
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

/**
 * Close modal by ID
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

/**
 * Toggle cart drawer
 */
function toggleCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    drawer.classList.toggle('open');
}

/**
 * Increment quantity in stepper
 */
function incrementQty(inputId) {
    const input = document.getElementById(inputId);
    input.value = (parseInt(input.value) || 1) + 1;
}

/**
 * Decrement quantity in stepper
 */
function decrementQty(inputId) {
    const input = document.getElementById(inputId);
    const newVal = Math.max(1, (parseInt(input.value) || 1) - 1);
    input.value = newVal;
}

/**
 * Clear all filters and reset to defaults
 */
function clearFilters() {
    state.filters = {
        search: '',
        category: 'All',
        source: 'all',
        min_price: null,
        max_price: null,
        in_stock: false
    };

    // Reset HTML input values
    document.getElementById('filter-search').value = '';
    document.getElementById('filter-farmers').checked = true;
    document.getElementById('filter-suppliers').checked = true;
    document.getElementById('filter-min-price').value = '';
    document.getElementById('filter-max-price').value = '';
    document.getElementById('filter-in-stock').checked = false;

    // Reset category chips
    document.querySelectorAll('.category-chip').forEach(chip => {
        chip.classList.remove('active');
        if (chip.textContent.trim() === 'All') {
            chip.classList.add('active');
        }
    });

    state.currentPage = 1;
    loadProducts();
}

// ════════════════════════════════════════════════════════════
// PRODUCT LOADING & RENDERING
// ════════════════════════════════════════════════════════════

/**
 * Load products from backend with current filters
 */
async function loadProducts(append = false) {
    try {
        state.loading = true;

        const grid = document.getElementById('product-grid');
        if (!append) {
            grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--text-light);">⏳ Loading products...</div>';
        }

        // Build filter object for API call
        const filters = {
            ...state.filters,
            page: state.currentPage,
            limit: PAGE_LIMIT
        };

        const response = await api.buyer.getMarketplaceProducts(filters);

        state.totalProducts = response.total;
        state.totalPages = response.pages;

        // Update results count
        const resultsCount = document.getElementById('results-count');
        if (response.items.length === 0 && !append) {
            resultsCount.textContent = 'No products match your filters.';
            grid.innerHTML = `
                <div style="grid-column:1/-1;text-align:center;padding:40px;">
                    <div style="color:var(--text-muted);font-size:14px;">
                        📭 No products found. Try adjusting your filters.
                    </div>
                    <button class="btn-clear" onclick="clearFilters()" 
                        style="margin-top:16px;background:var(--green-mid);color:white;padding:8px 16px;">
                        🔄 Clear All Filters
                    </button>
                </div>
            `;
        } else {
            resultsCount.textContent = `Showing ${response.items.length} of ${state.totalProducts} products`;

            // Render products
            if (!append) {
                grid.innerHTML = '';
            }

            response.items.forEach(product => {
                const card = document.createElement('div');
                card.innerHTML = renderProductCard(product);
                grid.appendChild(card.firstElementChild);
            });
        }

        // Show/hide Load More button
        const loadMoreBtn = document.getElementById('load-more-btn');
        if (state.currentPage < state.totalPages) {
            loadMoreBtn.style.display = 'block';
        } else {
            loadMoreBtn.style.display = 'none';
        }

        state.loading = false;
    } catch (error) {
        console.error('Error loading products:', error);
        showToast(error.message || 'Failed to load products', 'error');
        state.loading = false;
    }
}

/**
 * Render a single product card as HTML
 */
function renderProductCard(product) {
    // Determine stock badge
    let stockBadgeClass = 'in-stock';
    let stockBadgeText = 'In Stock';

    if (product.stock_quantity === 0) {
        stockBadgeClass = 'out-of-stock';
        stockBadgeText = 'Out of Stock';
    } else if (product.stock_quantity <= 10) {
        stockBadgeClass = 'low-stock';
        stockBadgeText = `Low Stock (${product.stock_quantity} left)`;
    }

    // Determine seller badge
    const sellerIcon = product.product_source === 'farmer' ? '🌾' : '📦';
    const sellerName = product.farmer_name || product.supplier_name || 'Unknown Seller';

    // Product image or placeholder
    const imageHtml = product.product_image ?
        `<img src="${product.product_image}" alt="${product.name}" onerror="this.style.display='none'">` :
        `<svg viewBox="0 0 220 160" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;">
            <rect width="220" height="160" fill="var(--green-ghost)"/>
            <text x="110" y="90" text-anchor="middle" font-size="48" font-family="sans-serif" fill="var(--text-light)">🐔</text>
        </svg>`;

    // Button state - disable if out of stock
    const buttonHtml = product.stock_quantity === 0 ?
        `<button class="card-actions" disabled style="opacity:0.5;cursor:not-allowed;flex:1;padding:6px 8px;border:none;border-radius:var(--radius-sm);font-size:11px;font-weight:600;background:var(--text-light);color:white;">Out of Stock</button>` :
        `<button class="btn-cart" onclick="addToCartFromCard(${product.id})" style="flex:1;">🛒 Add to Cart</button>`;

    return `
        <div class="product-card" data-product-id="${product.id}">
            <div class="card-image">
                ${imageHtml}
                <div class="stock-badge ${stockBadgeClass}">${stockBadgeText}</div>
            </div>
            <div class="card-body">
                <div class="name">${escapeHtml(product.name)}</div>
                <div class="seller-badge ${product.product_source}">${sellerIcon} ${escapeHtml(sellerName)}</div>
                <div class="price">KES ${product.unit_price.toFixed(2)} / ${escapeHtml(product.unit_of_measure)}</div>
                <p class="description">${product.description ? escapeHtml(product.description.substring(0, 80)) + '...' : ''}</p>
                <div class="card-actions">
                    ${buttonHtml}
                    <button class="btn-detail" onclick="openProductDetail(${product.id})">👁️ View</button>
                </div>
            </div>
        </div>
    `;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Add product to cart from product card
 */
function addToCartFromCard(productId) {
    // Find product in the grid to get its data
    const grid = document.getElementById('product-grid');
    const cardEl = grid.querySelector(`[data-product-id="${productId}"]`);

    if (!cardEl) {
        showToast('Product not found', 'error');
        return;
    }

    // Reconstruct product object from card
    const nameEl = cardEl.querySelector('.name');
    const priceEl = cardEl.querySelector('.price');
    const sellerEl = cardEl.querySelector('.seller-badge');

    const priceText = priceEl.textContent;
    const [priceStr, unitStr] = priceText.split(' / ');
    const unitPrice = parseFloat(priceStr.replace('KES ', ''));

    const product = {
        id: productId,
        name: nameEl.textContent,
        farmer_name: cardEl.querySelector('[data-product-id]')?.dataset.farmerName || '',
        supplier_name: cardEl.querySelector('[data-product-id]')?.dataset.supplierName || '',
        product_image: cardEl.querySelector('.card-image img')?.src || null,
        unit_price: unitPrice,
        unit_of_measure: unitStr || 'unit',
        stock_quantity: parseInt(cardEl.querySelector('.stock-badge').textContent.match(/\d+/)?.[0]) || 1
    };

    // For simplicity, add 1 item. User can adjust in cart drawer
    addToCart(product, 1);
    toggleCartDrawer();
}

// ════════════════════════════════════════════════════════════
// PRODUCT DETAIL & SELLER PROFILE MODALS
// ════════════════════════════════════════════════════════════

/**
 * Open product detail modal and populate with data
 */
async function openProductDetail(productId) {
    try {
        const modal = document.getElementById('product-modal');
        modal.innerHTML = `
            <div class="mp-modal" style="text-align:center;padding:40px;">
                ⏳ Loading product details...
            </div>
        `;
        modal.classList.add('active');

        const product = await api.buyer.getProductDetail(productId);

        // Determine stock badge
        let stockBadgeClass = 'in-stock';
        let stockBadgeText = 'In Stock';

        if (product.stock_quantity === 0) {
            stockBadgeClass = 'out-of-stock';
            stockBadgeText = 'Out of Stock';
        } else if (product.stock_quantity <= 10) {
            stockBadgeClass = 'low-stock';
            stockBadgeText = `Low Stock (${product.stock_quantity} left)`;
        }

        // Product image or placeholder
        const imageHtml = product.product_image ?
            `<img src="${product.product_image}" alt="${product.name}">` :
            `<svg viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">
                <rect width="300" height="300" fill="var(--green-ghost)"/>
                <text x="150" y="160" text-anchor="middle" font-size="80" font-family="sans-serif" fill="var(--text-light)">🐔</text>
            </svg>`;

        const sellerName = product.farmer_name || product.supplier_name || 'Seller';
        const sellerIcon = product.product_source === 'farmer' ? '🌾 Farmer' : '📦 Supplier';

        // Fetch related products from this seller
        let relatedProducts = '';
        const sellerId = product.farmer_id || product.supplier_id;
        if (sellerId) {
            try {
                const sellerData = await api.buyer.getSellerProfile(sellerId);
                const otherProducts = sellerData.products.filter(p => p.id !== productId).slice(0, 4);
                if (otherProducts.length > 0) {
                    relatedProducts = `
                        <div style="margin-top:20px;padding-top:20px;border-top:1px solid var(--green-pale);">
                            <h4 style="font-size:14px;font-weight:600;color:var(--text-dark);margin-bottom:12px;">More from ${escapeHtml(sellerName)}</h4>
                            <div style="display:flex;gap:12px;overflow-x:auto;padding-bottom:8px;">
                                ${otherProducts.map(p => `
                                    <div style="min-width:140px;cursor:pointer;border:1px solid var(--green-pale);border-radius:var(--radius-sm);padding:8px;text-align:center;" onclick="openProductDetail(${p.id})">
                                        <div style="font-size:32px;margin-bottom:4px;">🐔</div>
                                        <div style="font-size:11px;font-weight:600;color:var(--text-dark);">${escapeHtml(p.name.substring(0, 20))}</div>
                                        <div style="font-size:10px;color:var(--text-light);">KES ${p.unit_price.toFixed(2)}</div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }
            } catch (err) {
                console.error('Error loading related products:', err);
            }
        }

        const modalContent = `
            <button class="close-btn" onclick="closeModal('product-modal')">×</button>
            <div class="modal-body">
                <div class="detail-grid">
                    <div class="detail-image">${imageHtml}</div>
                    <div class="detail-info">
                        <h3>${escapeHtml(product.name)}</h3>
                        <div class="seller-section">
                            <strong>${escapeHtml(sellerName)}</strong><br>
                            <span style="font-size:11px;color:var(--text-light);">${sellerIcon}</span>
                            ${product.seller_location ? `<br><span style="font-size:11px;color:var(--text-light);">📍 ${escapeHtml(product.seller_location)}</span>` : ''}
                        </div>
                        <div class="price-large">KES ${product.unit_price.toFixed(2)}</div>
                        <span class="stock-status ${stockBadgeClass}">${stockBadgeText}</span>
                        
                        <p style="font-size:13px;color:var(--text-mid);margin:16px 0;">
                            ${product.description ? escapeHtml(product.description) : 'No description'}
                        </p>
                        
                        <div style="margin-bottom:16px;">
                            <label style="display:block;font-size:12px;font-weight:600;margin-bottom:8px;">Quantity</label>
                            <div class="qty-stepper">
                                <button onclick="decrementQty('detail-qty')">−</button>
                                <input type="number" id="detail-qty" value="1" min="1" max="${product.stock_quantity || 1}">
                                <button onclick="incrementQty('detail-qty')">+</button>
                            </div>
                        </div>
                        
                        <div class="detail-actions">
                            <button class="btn-add" ${product.stock_quantity === 0 ? 'disabled' : ''} 
                                onclick="addDetailProductToCart(${product.id}, '${escapeHtml(product.name)}', ${product.unit_price}, '${escapeHtml(product.unit_of_measure)}', ${product.stock_quantity}, '${product.product_image || ''}', '${escapeHtml(product.farmer_name || product.supplier_name || '')}')">
                                🛒 Add to Cart
                            </button>
                            <button class="btn-save" onclick="showToast('Added to wishlist!', 'success')">❤️ Save</button>
                        </div>
                        
                        ${product.seller_description ? `<p style="font-size:12px;color:var(--text-light);margin-top:16px;padding:12px;background:var(--green-ghost);border-radius:var(--radius-sm);">${escapeHtml(product.seller_description)}</p>` : ''}
                        
                        ${relatedProducts}
                    </div>
                </div>
            </div>
        `;

        modal.innerHTML = modalContent;

    } catch (error) {
        console.error('Error loading product detail:', error);
        showToast(error.message || 'Failed to load product', 'error');
        closeModal('product-modal');
    }
}

/**
 * Add product from detail modal to cart
 */
function addDetailProductToCart(productId, name, unitPrice, unitOfMeasure, stockQuantity, image, sellerName) {
    const qtyInput = document.getElementById('detail-qty');
    const quantity = parseInt(qtyInput.value) || 1;

    const product = {
        id: productId,
        name: name,
        farmer_name: sellerName,
        supplier_name: sellerName,
        product_image: image || null,
        unit_price: unitPrice,
        unit_of_measure: unitOfMeasure,
        stock_quantity: stockQuantity
    };

    addToCart(product, quantity);
    closeModal('product-modal');
    toggleCartDrawer();
}

/**
 * Open seller profile modal
 */
async function openSellerProfile(sellerId) {
    try {
        const modal = document.getElementById('seller-modal');
        modal.innerHTML = `
            <div class="mp-modal" style="text-align:center;padding:40px;">
                ⏳ Loading seller profile...
            </div>
        `;
        modal.classList.add('active');

        const seller = await api.buyer.getSellerProfile(sellerId);

        const productsHtml = seller.products.length > 0 ?
            `<div class="product-grid" style="grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;">
                ${seller.products.map(p => renderProductCard(p)).join('')}
            </div>` :
            `<div style="text-align:center;padding:40px;color:var(--text-light);">📭 No active listings</div>`;

        const modalContent = `
            <button class="close-btn" onclick="closeModal('seller-modal')">×</button>
            <div class="modal-body">
                <h3 style="font-size:20px;font-weight:700;color:var(--text-dark);margin-bottom:8px;">
                    ${escapeHtml(seller.name)}
                </h3>
                <div style="display:flex;gap:8px;align-items:center;margin-bottom:12px;">
                    <span style="display:inline-block;background:var(--green-pale);color:var(--green-deep);padding:4px 8px;border-radius:4px;font-size:11px;font-weight:600;">
                        ${seller.role === 'farmer' ? '🌾' : '📦'} ${seller.role}
                    </span>
                    ${seller.county ? `<span style="font-size:12px;color:var(--text-light);">📍 ${escapeHtml(seller.county)}</span>` : ''}
                </div>
                
                ${seller.description ? `<p style="font-size:13px;color:var(--text-mid);margin-bottom:16px;">${escapeHtml(seller.description)}</p>` : ''}
                
                <button class="btn-secondary" onclick="showToast('Messaging coming soon', 'info')" style="width:100%;margin-bottom:20px;padding:10px;background:transparent;color:var(--green-mid);border:1px solid var(--green-pale);border-radius:var(--radius-sm);cursor:pointer;">
                    💬 Message Seller
                </button>
                
                <h4 style="font-size:14px;font-weight:600;color:var(--text-dark);margin-bottom:12px;">Active Listings</h4>
                ${productsHtml}
            </div>
        `;

        modal.innerHTML = modalContent;

    } catch (error) {
        console.error('Error loading seller profile:', error);
        showToast(error.message || 'Failed to load seller', 'error');
        closeModal('seller-modal');
    }
}

// ════════════════════════════════════════════════════════════
// STOCK POLLING
// ════════════════════════════════════════════════════════════

/**
 * Poll stock status every 30 seconds
 */
async function pollStockStatus() {
    const grid = document.getElementById('product-grid');
    const cards = grid.querySelectorAll('[data-product-id]');

    for (const card of cards) {
        const productId = parseInt(card.dataset.productId);

        try {
            const stock = await api.buyer.getStockStatus(productId);

            // Update stock badge
            const badge = card.querySelector('.stock-badge');
            const button = card.querySelector('.card-actions button.btn-cart');

            if (badge) {
                badge.className = 'stock-badge';
                if (stock.stock_quantity === 0) {
                    badge.classList.add('out-of-stock');
                    badge.textContent = 'Out of Stock';
                    if (button) button.disabled = true;
                } else if (stock.stock_quantity <= 10) {
                    badge.classList.add('low-stock');
                    badge.textContent = `Low Stock (${stock.stock_quantity} left)`;
                    if (button) button.disabled = false;
                } else {
                    badge.classList.add('in-stock');
                    badge.textContent = 'In Stock';
                    if (button) button.disabled = false;
                }
            }
        } catch (error) {
            // Silently fail on polling errors — no toast
            console.debug(`Stock poll error for product ${productId}:`, error);
        }
    }
}

// ════════════════════════════════════════════════════════════
// INITIALIZATION
// ════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', async () => {
    // Auth check
    const token = localStorage.getItem('accessToken');
    if (!token) {
        window.location.href = '../../auth/login/login.html';
        return;
    }

    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userRole = localStorage.getItem('userRole');

    if (!userRole || (userRole !== 'buyer' && userRole !== 'farmer')) {
        window.location.href = '../../auth/login/login.html';
        return;
    }

    // Load initial products
    loadProducts();

    // Start stock polling
    state.stockPollInterval = setInterval(pollStockStatus, STOCK_POLL_INTERVAL);

    // Stop polling on unload
    window.addEventListener('beforeunload', () => {
        if (state.stockPollInterval) {
            clearInterval(state.stockPollInterval);
        }
    });

    // Initialize cart badge
    updateCartBadge();

    // Set up filter event listeners

    // Search input with debounce
    const searchDebounc = debounce(() => {
        state.filters.search = document.getElementById('filter-search').value.trim();
        state.currentPage = 1;
        loadProducts();
    }, 400);
    document.getElementById('filter-search').addEventListener('input', searchDebounc);

    // Topbar search with debounce
    const topbarSearchDebounc = debounce(() => {
        state.filters.search = document.getElementById('topbar-search').value.trim();
        state.currentPage = 1;
        loadProducts();
    }, 400);
    document.getElementById('topbar-search').addEventListener('input', topbarSearchDebounc);

    // Category chips
    document.querySelectorAll('.category-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            document.querySelectorAll('.category-chip').forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            state.filters.category = chip.textContent.trim().split(' ')[0] === 'All' ? 'All' : chip.textContent.trim();
            state.currentPage = 1;
            loadProducts();
        });
    });

    // Source toggle (farmers/suppliers)
    document.getElementById('filter-farmers').addEventListener('change', () => {
        const isFarmer = document.getElementById('filter-farmers').checked;
        const isSupplier = document.getElementById('filter-suppliers').checked;

        if (isFarmer && !isSupplier) {
            state.filters.source = 'farmer';
        } else if (!isFarmer && isSupplier) {
            state.filters.source = 'supplier';
        } else {
            state.filters.source = 'all';
        }
        state.currentPage = 1;
        loadProducts();
    });

    document.getElementById('filter-suppliers').addEventListener('change', () => {
        const isFarmer = document.getElementById('filter-farmers').checked;
        const isSupplier = document.getElementById('filter-suppliers').checked;

        if (isFarmer && !isSupplier) {
            state.filters.source = 'farmer';
        } else if (!isFarmer && isSupplier) {
            state.filters.source = 'supplier';
        } else {
            state.filters.source = 'all';
        }
        state.currentPage = 1;
        loadProducts();
    });

    // Price range inputs with debounce
    const priceDebounce = debounce(() => {
        const minVal = document.getElementById('filter-min-price').value;
        const maxVal = document.getElementById('filter-max-price').value;

        state.filters.min_price = minVal ? parseFloat(minVal) : null;
        state.filters.max_price = maxVal ? parseFloat(maxVal) : null;
        state.currentPage = 1;
        loadProducts();
    }, 600);

    document.getElementById('filter-min-price').addEventListener('input', priceDebounce);
    document.getElementById('filter-max-price').addEventListener('input', priceDebounce);

    // In stock toggle
    document.getElementById('filter-in-stock').addEventListener('change', () => {
        state.filters.in_stock = document.getElementById('filter-in-stock').checked;
        state.currentPage = 1;
        loadProducts();
    });

    // Load More button
    document.getElementById('load-more-btn').addEventListener('click', () => {
        state.currentPage++;
        loadProducts(append = true);
    });
});
