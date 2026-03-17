// Global State
let currentPage = 'overview';
let ordersData = [];
let profileData = null;
let notificationsData = [];
let currentFilter = 'all';
let notificationFilter = 'all';
let productCache = {}; // Cache product names by ID to avoid repeat API calls
let overviewRetryCount = 0;

// ============================================
// UTILITY FUNCTIONS
// ============================================

function formatCurrency(amount) {
    if (!amount && amount !== 0) return 'KES --';
    return 'KES ' + Number(amount).toLocaleString('en-KE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatDate(dateString) {
    if (!dateString) return '--';
    return new Date(dateString).toLocaleDateString('en-KE', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    });
}

function timeAgo(dateString) {
    if (!dateString) return '-';

    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    if (seconds < 60) return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days}d ago`;
    if (days < 30) return `${Math.floor(days / 7)}w ago`;
    if (days < 365) return `${Math.floor(days / 30)}mo ago`;
    return date.toLocaleDateString('en-KE');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================
// PAGE SWITCHING
// ============================================

function showPage(pageId, navElement) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));

    // Show selected page
    const pageEl = document.getElementById(`page-${pageId}`);
    if (pageEl) {
        pageEl.classList.add('active');
        currentPage = pageId;
    }

    // Update nav active state
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
    if (navElement) navElement.classList.add('active');

    // Update topbar title
    const titleMap = {
        'overview': 'Overview',
        'orders': 'My Orders',
        'profile': 'My Profile',
        'notifications': 'Notifications',
        'settings': 'Settings',
        'delivery-addresses': 'Delivery Addresses',
        'invoices': 'Invoices'
    };
    document.getElementById('pageTitle').textContent = titleMap[pageId] || 'Page';

    // Load page-specific data
    loadPageData(pageId);
}

// ============================================
// PAGE DATA LOADING
// ============================================

async function loadPageData(pageId) {
    try {
        switch (pageId) {
            case 'overview':
                await loadOverview();
                break;
            case 'orders':
                await loadOrders();
                break;
            case 'profile':
                await loadProfile();
                break;
            case 'notifications':
                await loadNotifications();
                break;
            case 'settings':
                loadSettings();
                break;
            case 'delivery-addresses':
                loadDeliveryAddresses();
                break;
            case 'invoices':
                await loadInvoices();
                break;
        }
    } catch (error) {
        console.error(`Error loading page ${pageId}:`, error);
        showToast('Error loading page data', 'error');
    }
}

// ============================================
// OVERVIEW PAGE
// ============================================

async function loadOverview() {
    try {
        showOverviewLoading(true);

        if (!profileData) {
            profileData = await api.buyer.getProfile();
        }

        const orders = await api.buyer.getOrders();
        if (!Array.isArray(orders)) {
            throw new Error('Invalid orders response');
        }

        const totalOrders = orders.length || 0;
        const totalSpent = orders.reduce((sum, order) => sum + (order.total_amount || 0), 0);
        const activeOrders = orders.filter(o =>
            ['pending', 'approved', 'shipped'].includes(o.order_status?.toLowerCase() || o.status?.toLowerCase())
        ).length;

        document.getElementById('kpi-total-orders').textContent = totalOrders;
        document.getElementById('kpi-total-spent').textContent = formatCurrency(totalSpent);
        document.getElementById('kpi-active-orders').textContent = activeOrders;

        document.getElementById('profile-name-display').textContent = (profileData?.full_name || profileData?.name || '-');
        document.getElementById('profile-email-display').textContent = profileData?.email || '-';
        document.getElementById('profile-county-display').textContent = profileData?.county || '-';

        const recentOrders = orders.slice(0, 5);

        const productIds = [];
        recentOrders.forEach(order => {
            if (order.items && Array.isArray(order.items)) {
                order.items.forEach(item => {
                    if (item.product_id && !productCache[item.product_id]) {
                        productIds.push(item.product_id);
                    }
                });
            }
        });

        for (const productId of productIds) {
            try {
                const product = await api.buyer.getProductDetail(productId);
                productCache[productId] = product?.name || `Product #${productId}`;
            } catch (err) {
                productCache[productId] = `Product #${productId}`;
            }
        }

        const recentOrdersHtml = recentOrders.length > 0
            ? recentOrders.map(order => {
                const status = order.order_status || order.status || 'pending';
                const firstItem = order.items?.[0];
                const productName = firstItem ? (productCache[firstItem.product_id] || `Product #${firstItem.product_id}`) : 'Unknown';
                const itemsCount = order.items?.length || 0;
                const itemsSuffix = itemsCount > 1 ? ` and ${itemsCount - 1} more` : '';

                return `
                    <div class="order-card">
                        <div class="order-card-header">
                            <div>
                                <div class="order-card-id">#ORD-${order.id}</div>
                                <div class="order-card-date">${timeAgo(order.created_at)}</div>
                            </div>
                            <span class="status-pill status-${status.toLowerCase()}">${status.charAt(0).toUpperCase() + status.slice(1)}</span>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <div class="order-card-items-count">${productName}${itemsSuffix}</div>
                        </div>
                        <div class="order-card-amount">${formatCurrency(order.total_amount)}</div>
                    </div>
                `;
            }).join('')
            : `<div class="empty-state" style="padding: 20px;">
                <div class="empty-state-icon">📦</div>
                <div class="empty-state-title">No orders yet</div>
                <div class="empty-state-message">Start shopping to see your orders here</div>
            </div>`;

        document.getElementById('recent-orders-list').innerHTML = recentOrdersHtml;

        const notifResponse = await api.get('/notifications/');
        const notifs = Array.isArray(notifResponse) ? notifResponse : [];
        const recentNotifs = notifs.slice(0, 3);
        const unreadCount = notifs.filter(n => !n.is_read).length;

        const notifPreviewHtml = recentNotifs.length > 0
            ? recentNotifs.map(notif => `
                <div class="notification-item" id="notif-preview-${notif.id}">
                    <div class="notification-dot" style="${notif.is_read ? 'background: #d0d0d0;' : 'background: var(--green-bright);'}"></div>
                    <div class="notification-content" style="flex:1;">
                        <div class="notification-title" style="font-weight: ${notif.is_read ? '400' : '600'};">${notif.title || 'Notification'}</div>
                        <div class="notification-message" style="font-size: 12px; color: var(--text-light);">${notif.message || '-'}</div>
                    </div>
                    <div class="notification-time">${timeAgo(notif.created_at)}</div>
                </div>
            `).join('')
            : `<div class="empty-state" style="padding: 20px 10px;">
                <div class="empty-state-icon">🔔</div>
                <div class="empty-state-title">All clear</div>
                <div class="empty-state-message" style="font-size: 12px;">No new notifications</div>
            </div>`;

        const notifSection = document.getElementById('notif-preview');
        if (unreadCount > 0) {
            notifSection.innerHTML = notifPreviewHtml + `
                <div style="padding: 12px 16px; border-top: 1px solid #e5e5e5; text-align: center;">
                    <button class="button btn-secondary btn-sm" onclick="markAllNotificationsRead()" style="width: 100%;">Mark all read</button>
                </div>
            `;
        } else {
            notifSection.innerHTML = notifPreviewHtml;
        }

        showOverviewLoading(false);
        overviewRetryCount = 0;

    } catch (error) {
        console.error('Error loading overview:', error);
        showOverviewLoading(false);

        const errorHtml = `
            <div class="empty-state" style="padding: 40px 20px;">
                <div class="empty-state-icon">⚠️</div>
                <div class="empty-state-title">Could not load overview</div>
                <div class="empty-state-message" style="margin-bottom: 16px; font-size: 13px;">${error.message || 'Please try again'}</div>
                <button class="button btn-primary" onclick="loadPageData('overview')" style="margin: 0 auto;">Retry</button>
            </div>
        `;

        document.getElementById('kpi-total-orders').textContent = '--';
        document.getElementById('kpi-total-spent').textContent = 'KES --';
        document.getElementById('kpi-active-orders').textContent = '--';
        document.getElementById('recent-orders-list').innerHTML = errorHtml;
        document.getElementById('notif-preview').innerHTML = `
            <div class="empty-state" style="padding: 20px 10px;">
                <div class="empty-state-icon">⚠️</div>
                <div class="empty-state-title">Error loading notifications</div>
            </div>
        `;

        showToast('Failed to load overview data', 'error');
    }
}

function showOverviewLoading(isLoading) {
    if (isLoading) {
        document.getElementById('kpi-total-orders').innerHTML = '<div style="background: #e0e0e0; height: 28px; border-radius: 4px; animation: pulse 1.5s infinite;"></div>';
        document.getElementById('kpi-total-spent').innerHTML = '<div style="background: #e0e0e0; height: 28px; border-radius: 4px; animation: pulse 1.5s infinite;"></div>';
        document.getElementById('kpi-active-orders').innerHTML = '<div style="background: #e0e0e0; height: 28px; border-radius: 4px; animation: pulse 1.5s infinite;"></div>';
    }
}

// ============================================
// ORDERS PAGE
// ============================================

async function loadOrders() {
    try {
        showOrdersLoading(true);

        ordersData = await api.buyer.getOrders();

        const productIds = [];
        ordersData.forEach(order => {
            if (order.items && Array.isArray(order.items)) {
                order.items.forEach(item => {
                    if (item.product_id && !productCache[item.product_id]) {
                        productIds.push(item.product_id);
                    }
                });
            }
        });

        await Promise.all(
            productIds.map(productId =>
                api.buyer.getProductDetail(productId)
                    .then(product => {
                        productCache[productId] = product?.name || `Product #${productId}`;
                    })
                    .catch(() => {
                        productCache[productId] = `Product #${productId}`;
                    })
            )
        );

        showOrdersLoading(false);
        renderOrdersList(currentFilter);
    } catch (error) {
        console.error('Error loading orders:', error);
        showOrdersLoading(false);

        document.getElementById('orders-list').innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <div class="empty-state-title">Could not load orders</div>
                <div class="empty-state-message" style="margin-bottom: 16px;">${error.message || 'Please try again'}</div>
                <button class="button btn-primary" onclick="loadPageData('orders')" style="margin: 0 auto;">Retry</button>
            </div>
        `;
        showToast('Failed to load orders', 'error');
    }
}

function showOrdersLoading(isLoading) {
    if (!isLoading) return;

    document.getElementById('orders-list').innerHTML = `
        <div class="order-card" style="opacity: 0.6;">
            <div style="height: 16px; background: #e0e0e0; border-radius: 4px; margin-bottom: 8px; animation: pulse 1.5s infinite;"></div>
            <div style="height: 12px; background: #e0e0e0; border-radius: 4px; width: 60%; animation: pulse 1.5s infinite;"></div>
        </div>
        <div class="order-card" style="opacity: 0.6;">
            <div style="height: 16px; background: #e0e0e0; border-radius: 4px; margin-bottom: 8px; animation: pulse 1.5s infinite;"></div>
            <div style="height: 12px; background: #e0e0e0; border-radius: 4px; width: 60%; animation: pulse 1.5s infinite;"></div>
        </div>
    `;
}

function renderOrdersList(filter) {
    const filtered = filter === 'all'
        ? ordersData
        : ordersData.filter(o => {
            const status = o.order_status || o.status || '';
            return status.toLowerCase() === filter.toLowerCase();
        });

    const html = filtered.length > 0
        ? filtered.map(order => {
            const status = order.order_status || order.status || 'pending';
            const paymentStatus = order.payment_status || 'pending';
            const itemsList = order.items?.map(item => {
                const productName = productCache[item.product_id] || `Product #${item.product_id}`;
                return `${item.quantity} × ${productName}`;
            }).join(', ') || 'No items';

            return `
            <div class="order-card">
                <div class="order-card-header">
                    <div>
                        <div class="order-card-id">#ORD-${order.id}</div>
                        <div class="order-card-date">${timeAgo(order.created_at)}</div>
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <span style="background: ${paymentStatus === 'completed' ? 'var(--green-pale)' : paymentStatus === 'pending' ? 'var(--amber-pale)' : 'var(--red-pale)'}; color: ${paymentStatus === 'completed' ? 'var(--green-mid)' : paymentStatus === 'pending' ? 'var(--amber)' : 'var(--red-soft)'}; padding: 2px 8px; border-radius: 6px; font-size: 10px; font-weight: 600;">
                            ${paymentStatus.toUpperCase().substring(0, 3)}
                        </span>
                        <span class="status-pill status-${status.toLowerCase()}">${status.charAt(0).toUpperCase() + status.slice(1)}</span>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div>
                        <div class="order-card-items-count">${order.items?.length || 0} items</div>
                        <div class="order-card-from" style="font-size: 12px; color: var(--text-light); margin-top: 2px;">${itemsList}</div>
                    </div>
                    <div class="order-card-amount">${formatCurrency(order.total_amount)}</div>
                </div>
                <div style="display: flex; gap: 8px; margin-top: 12px;">
                    <button class="button btn-secondary btn-sm" onclick="viewOrderDetails(${order.id})" style="flex: 1;">View Details</button>
                    <button class="button btn-secondary btn-sm" onclick="generateInvoice(${order.id})" style="flex: 1;">Invoice</button>
                    ${['pending', 'approved'].includes(status.toLowerCase())
                    ? `<button class="button btn-danger btn-sm" onclick="cancelOrderWithConfirm(${order.id})" style="flex: 1;">Cancel</button>`
                    : ''}
                </div>
            </div>
        `;
        }).join('')
        : `<div class="empty-state">
        <div class="empty-state-icon">📋</div>
        <div class="empty-state-title">No ${filter !== 'all' ? filter : ''} orders</div>
        <div class="empty-state-message" style="margin-bottom: 16px;">
            ${filter === 'all' ? 'You haven\'t placed any orders yet' : `You have no ${filter} orders`}
        </div>
        <a href="marketplace.html" class="button btn-primary" style="text-decoration: none;">Browse Marketplace →</a>
    </div>`;

    document.getElementById('orders-list').innerHTML = html;
}

function filterOrders(filter, element) {
    currentFilter = filter;

    document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
    if (element) {
        element.classList.add('active');
    }

    renderOrdersList(filter);
}

async function viewOrderDetails(orderId) {
    try {
        const order = await api.buyer.getOrder(orderId);

        for (const item of order.items || []) {
            if (item.product_id && !productCache[item.product_id]) {
                try {
                    const product = await api.buyer.getProductDetail(item.product_id);
                    productCache[item.product_id] = product?.name || `Product #${item.product_id}`;
                } catch (err) {
                    productCache[item.product_id] = `Product #${item.product_id}`;
                }
            }
        }

        const status = order.order_status || order.status || 'pending';
        const paymentStatus = order.payment_status || 'pending';
        const itemsHtml = (order.items || []).map(item => `
        <div style="padding: 10px 0; border-bottom: 1px solid #e5e5e5; display: flex; justify-content: space-between;">
            <div>
                <div style="font-weight: 500;">${productCache[item.product_id] || `Product #${item.product_id}`}</div>
                <div style="font-size: 12px; color: var(--text-light); margin-top: 2px;">Qty: ${item.quantity}</div>
            </div>
            <div>
                <div style="font-weight: 500; text-align: right;">${formatCurrency(item.total_price)}</div>
                <div style="font-size: 12px; color: var(--text-light); text-align: right;">@ ${formatCurrency(item.unit_price)}/unit</div>
            </div>
        </div>
    `).join('');

        const modalHtml = `
        <div style="position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000;">
            <div style="background: white; border-radius: 12px; width: 90%; max-width: 600px; max-height: 90vh; overflow-y: auto; padding: 24px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #e5e5e5;">
                    <h2 style="margin: 0; font-size: 18px;">Order #${order.id}</h2>
                    <span class="status-pill status-${status.toLowerCase()}">${status.charAt(0).toUpperCase() + status.slice(1)}</span>
                </div>

                <div style="margin-bottom: 16px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding: 12px 0; border-bottom: 1px solid #e5e5e5;">
                        <div>
                            <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; margin-bottom: 4px;">Order Date</div>
                            <div style="font-size: 13px;">${formatDate(order.created_at)}</div>
                        </div>
                        <div>
                            <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; margin-bottom: 4px;">Payment Status</div>
                            <div style="font-size: 13px;">
                                <span style="background: ${paymentStatus === 'completed' ? 'var(--green-pale)' : paymentStatus === 'pending' ? 'var(--amber-pale)' : 'var(--red-pale)'}; color: ${paymentStatus === 'completed' ? 'var(--green-mid)' : paymentStatus === 'pending' ? 'var(--amber)' : 'var(--red-soft)'}; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 600;">
                                    ${paymentStatus.charAt(0).toUpperCase() + paymentStatus.slice(1)}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <div style="margin-bottom: 16px;">
                    <h3 style="margin: 0 0 12px 0; font-size: 14px; font-weight: 600;">Items</h3>
                    <div>${itemsHtml}</div>
                </div>

                <div style="background: var(--green-ghost); border-radius: 8px; padding: 12px; margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 12px; color: var(--text-light);">Total Amount</div>
                            <div style="font-size: 20px; font-weight: 700; color: var(--green-deep);">${formatCurrency(order.total_amount)}</div>
                        </div>
                    </div>
                </div>

                ${order.note ? `
                    <div style="background: #fffacd; border-left: 4px solid var(--amber); border-radius: 4px; padding: 12px; margin-bottom: 16px;">
                        <div style="font-size: 11px; color: #9a6e00; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;">Note to Seller</div>
                        <div style="font-size: 13px;">${order.note}</div>
                    </div>
                ` : ''}

                <div style="display: flex; gap: 8px; justify-content: flex-end;">
                    <button class="button btn-secondary" onclick="this.closest('[style*=position]')?.remove()">Close</button>
                    <button class="button btn-primary" onclick="generateInvoice(${order.id}); this.closest('[style*=position]')?.remove();">Download Invoice</button>
                </div>
            </div>
        </div>
    `;

        const modal = document.createElement('div');
        modal.innerHTML = modalHtml;
        document.body.appendChild(modal.firstElementChild);
    } catch (error) {
        console.error('Error viewing order details:', error);
        showToast('Failed to load order details', 'error');
    }
}

async function cancelOrderWithConfirm(orderId) {
    const modalHtml = `
    <div style="position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000;">
        <div style="background: white; border-radius: 12px; width: 90%; max-width: 400px; padding: 24px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
            <h2 style="margin: 0 0 8px 0; font-size: 18px; color: var(--red-soft);">Cancel Order</h2>
            <p style="margin: 0 0 20px 0; font-size: 14px; color: var(--text-light);">
                Are you sure you want to cancel order #${orderId}? This action cannot be undone.
            </p>
            <div style="display: flex; gap: 8px; justify-content: flex-end;">
                <button class="button btn-secondary" onclick="this.closest('[style*=position]')?.remove()">Keep Order</button>
                <button class="button btn-danger" onclick="performCancelOrder(${orderId}); this.closest('[style*=position]')?.remove();">Cancel Order</button>
            </div>
        </div>
    </div>
`;

    const modal = document.createElement('div');
    modal.innerHTML = modalHtml;
    document.body.appendChild(modal.firstElementChild);
}

async function performCancelOrder(orderId) {
    try {
        showToast('Cancelling order...', 'info');
        await api.buyer.cancelOrder(orderId);
        showToast(`Order #${orderId} cancelled successfully`, 'success');

        await loadOrders();
        renderOrdersList(currentFilter);
    } catch (error) {
        console.error('Error cancelling order:', error);
        showToast(error.message || 'Failed to cancel order', 'error');
    }
}

// ============================================
// PROFILE PAGE
// ============================================

async function loadProfile() {
    try {
        if (!profileData) {
            profileData = await api.buyer.getProfile();
        }

        document.getElementById('form-fullname').value = (profileData?.full_name || profileData?.name || '');
        document.getElementById('form-email').value = profileData.email || '';
        document.getElementById('form-phone').value = profileData.phone || '';
        document.getElementById('form-business-name').value = profileData.business_name || '';
        document.getElementById('form-county').value = profileData.county || '';
        document.getElementById('form-buyer-type').value = profileData.buyer_type || 'individual';
        document.getElementById('form-payment-method').value = profileData.preferred_payment || 'mpesa';
    } catch (error) {
        console.error('Error loading profile:', error);
        showToast('Failed to load profile', 'error');
    }
}

async function saveProfile(event) {
    event.preventDefault();

    const button = event.target.querySelector('button[type="submit"]');
    const originalText = button.textContent;

    try {
        const fullName = document.getElementById('form-fullname').value;
        if (!fullName || fullName.trim().length === 0) {
            showToast('Full name is required', 'error');
            return;
        }

        const phone = document.getElementById('form-phone').value;
        const phoneRegex = /^(\+254|0)[17]\d{8}$/;
        if (phone && !phoneRegex.test(phone)) {
            showToast('Please enter a valid Kenyan phone number (e.g., +254712345678)', 'error');
            return;
        }

        button.disabled = true;
        button.textContent = 'Saving...';

        const formData = {
            full_name: fullName,
            phone: phone || null,
            business_name: document.getElementById('form-business-name').value || null,
            county: document.getElementById('form-county').value || null,
            buyer_type: document.getElementById('form-buyer-type').value || null,
            preferred_payment: document.getElementById('form-payment-method').value || null
        };

        const response = await api.put('/buyers/profile', formData);
        profileData = response;

        const user = JSON.parse(localStorage.getItem('user') || '{}');
        user.name = fullName;
        user.phone = phone;
        localStorage.setItem('user', JSON.stringify(user));

        document.getElementById('sidebarName').textContent = fullName;

        showToast('Profile updated successfully', 'success');

        setTimeout(() => {
            showPage('overview', document.querySelector('[data-page=overview]'));
        }, 500);
    } catch (error) {
        console.error('Error saving profile:', error);
        showToast(error.message || 'Failed to save profile', 'error');
    } finally {
        button.disabled = false;
        button.textContent = originalText;
    }
}

// ============================================
// NOTIFICATIONS PAGE
// ============================================

async function loadNotifications() {
    try {
        notificationsData = await api.get('/notifications/');
        renderNotificationsList(notificationFilter);
        updateNotificationBadge();
    } catch (error) {
        console.error('Error loading notifications:', error);
        showToast('Failed to load notifications', 'error');
    }
}

function renderNotificationsList(filter) {
    const filtered = filter === 'all'
        ? notificationsData
        : notificationsData.filter(n =>
            (filter === 'unread' && !n.is_read) ||
            (filter === 'read' && n.is_read)
        );

    const html = filtered.length > 0
        ? filtered.map(notif => `
        <div class="notification-item" id="notif-${notif.id}">
            <div class="notification-dot" style="${notif.is_read ? 'display:none;' : ''}"></div>
            <div class="notification-content" style="flex:1;">
                <div class="notification-title" onclick="markNotificationRead(${notif.id}); return false;">${notif.title || 'Notification'}</div>
                <div class="notification-message">${notif.message || '-'}</div>
            </div>
            <div class="notification-time">${timeAgo(notif.created_at)}</div>
            <button class="notification-delete-btn" onclick="deleteNotification(${notif.id})">×</button>
        </div>
    `).join('')
        : `<div class="empty-state">
        <div class="empty-state-icon">🔔</div>
        <div class="empty-state-title">No ${filter !== 'all' ? filter : ''} notifications</div>
    </div>`;

    document.getElementById('notifications-list').innerHTML = html;
}

function filterNotifications(filter, element) {
    notificationFilter = filter;
    document.querySelectorAll('[data-filter]').forEach(t => t.classList.remove('active'));
    element.classList.add('active');
    renderNotificationsList(filter);
}

async function markNotificationRead(notifId) {
    try {
        try {
            await api.put(`/notifications/${notifId}`, { is_read: true });
        } catch (err) {
            if (err.status === 405) {
                await api.post(`/notifications/${notifId}/mark-read`, {});
            } else {
                throw err;
            }
        }

        const notif = notificationsData.find(n => n.id === notifId);
        if (notif) notif.is_read = true;
        renderNotificationsList(notificationFilter);
        updateNotificationBadge();
        showToast('Marked as read', 'success');
    } catch (error) {
        console.error('Error marking notification as read:', error);
        showToast(error.message || 'Failed to mark as read', 'error');
    }
}

async function markAllNotificationsRead() {
    try {
        try {
            await api.put('/notifications/mark-all-read', {});
        } catch (err) {
            await api.post('/notifications/mark-all-read', {});
        }

        notificationsData.forEach(n => n.is_read = true);
        renderNotificationsList(notificationFilter);
        updateNotificationBadge();
        showToast('All notifications marked as read', 'success');
    } catch (error) {
        console.error('Error marking all as read:', error);
        showToast(error.message || 'Failed to mark as read', 'error');
    }
}

async function deleteNotification(notifId) {
    try {
        await api.delete(`/notifications/${notifId}`);
        notificationsData = notificationsData.filter(n => n.id !== notifId);
        const element = document.getElementById(`notif-${notifId}`);
        if (element) {
            element.style.opacity = '0.5';
            setTimeout(() => element.remove(), 300);
        }
        updateNotificationBadge();
        showToast('Notification deleted', 'success');
    } catch (error) {
        console.error('Error deleting notification:', error);
    }
}

function updateNotificationBadge() {
    const unreadCount = notificationsData.filter(n => !n.is_read).length;
    const badgeEl = document.getElementById('notifBadge');
    const topbarDot = document.getElementById('topbarNotifDot');

    if (unreadCount > 0) {
        badgeEl.textContent = unreadCount;
        badgeEl.style.display = 'inline-block';
        topbarDot.style.display = 'block';
    } else {
        badgeEl.style.display = 'none';
        topbarDot.style.display = 'none';
    }
}

// ============================================
// SETTINGS PAGE
// ============================================

function loadSettings() {
    const prefs = JSON.parse(localStorage.getItem('pms_notif_prefs') || '{}');
    document.getElementById('notif-orders').checked = prefs.notif_orders !== false;
    document.getElementById('notif-messages').checked = prefs.notif_messages !== false;
    document.getElementById('notif-promos').checked = prefs.notif_promos === true;
}

async function changePassword(event) {
    event.preventDefault();

    const newPass = document.getElementById('form-new-password').value;
    const confirmPass = document.getElementById('form-confirm-password').value;

    if (newPass !== confirmPass) {
        showToast('New passwords do not match', 'error');
        return;
    }

    if (newPass.length < 8) {
        showToast('Password must be at least 8 characters', 'error');
        return;
    }

    try {
        const button = event.target.querySelector('button[type="submit"]');
        button.disabled = true;
        button.textContent = 'Changing Password...';

        showToast('Password change endpoint not yet available. Please contact support.', 'error');

        button.disabled = false;
        button.textContent = 'Change Password';
    } catch (error) {
        console.error('Error changing password:', error);
        showToast(error.message || 'Failed to change password', 'error');
    }
}

function saveNotificationPreferences() {
    const prefs = {
        notif_orders: document.getElementById('notif-orders').checked,
        notif_messages: document.getElementById('notif-messages').checked,
        notif_promos: document.getElementById('notif-promos').checked
    };
    localStorage.setItem('pms_notif_prefs', JSON.stringify(prefs));
    showToast('Preferences saved', 'success');
}

// ============================================
// DELIVERY ADDRESSES PAGE
// ============================================

function loadDeliveryAddresses() {
    if (profileData) {
        document.getElementById('current-county').textContent = profileData.county || '-';
    }
}

// ============================================
// INVOICES PAGE
// ============================================

async function loadInvoices() {
    try {
        let orders = ordersData;
        if (!orders || orders.length === 0) {
            orders = await api.buyer.getOrders();

            const productIds = [];
            orders.forEach(order => {
                if (order.items && Array.isArray(order.items)) {
                    order.items.forEach(item => {
                        if (item.product_id && !productCache[item.product_id]) {
                            productIds.push(item.product_id);
                        }
                    });
                }
            });

            for (const productId of productIds) {
                try {
                    const product = await api.buyer.getProductDetail(productId);
                    productCache[productId] = product?.name || `Product #${productId}`;
                } catch (err) {
                    productCache[productId] = `Product #${productId}`;
                }
            }
        }

        const invoiceOrders = orders.sort((a, b) =>
            new Date(b.created_at) - new Date(a.created_at)
        );

        const html = invoiceOrders.length > 0
            ? invoiceOrders.map(order => {
                const status = order.order_status || order.status || 'pending';
                return `
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 500; margin-bottom: 4px;">INV-${order.id}</div>
                            <div style="font-size: 12px; color: var(--text-light);">${formatDate(order.created_at)}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-weight: 500; font-size: 16px; margin-bottom: 8px;">${formatCurrency(order.total_amount)}</div>
                            <span class="status-pill status-${status.toLowerCase()}" style="margin-right: 8px;">${status.charAt(0).toUpperCase() + status.slice(1)}</span>
                            <button class="button btn-secondary btn-sm" onclick="generateInvoice(${order.id})" style="margin-left: 4px;">
                                Download PDF
                            </button>
                        </div>
                    </div>
                </div>
            `;
            }).join('')
            : `<div class="empty-state">
            <div class="empty-state-icon">🧾</div>
            <div class="empty-state-title">No invoices yet</div>
            <div class="empty-state-message">Invoices will be available once you place orders</div>
        </div>`;

        document.getElementById('invoices-list').innerHTML = html;
    } catch (error) {
        console.error('Error loading invoices:', error);
        document.getElementById('invoices-list').innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">⚠️</div>
            <div class="empty-state-title">Could not load invoices</div>
            <div class="empty-state-message" style="margin-bottom: 16px;">${error.message || 'Please try again'}</div>
            <button class="button btn-primary" onclick="loadPageData('invoices')">Retry</button>
        </div>
    `;
        showToast('Failed to load invoices', 'error');
    }
}

async function generateInvoice(orderId) {
    try {
        const order = await api.buyer.getOrder(orderId);

        for (const item of order.items || []) {
            if (item.product_id && !productCache[item.product_id]) {
                try {
                    const product = await api.buyer.getProductDetail(item.product_id);
                    productCache[item.product_id] = product?.name || `Product #${item.product_id}`;
                } catch (err) {
                    productCache[item.product_id] = `Product #${item.product_id}`;
                }
            }
        }

        const user = JSON.parse(localStorage.getItem('user') || '{}');

        const subtotal = (order.total_amount / 1.16);
        const vat = order.total_amount - subtotal;

        const invoiceHtml = `
        <div style="max-width: 800px; margin: 0 auto; font-family: 'DM Sans', sans-serif;">
            <div class="invoice-header" style="border-bottom: 2px solid #333; padding-bottom: 16px; margin-bottom: 20px;">
                <h1 style="margin: 0 0 8px 0; font-size: 24px;">POULTRY MANAGEMENT SYSTEM</h1>
                <h2 style="margin: 0; font-size: 16px; color: #666;">Invoice</h2>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div>
                    <h3 style="margin: 0 0 8px 0; font-size: 12px; color: #999; text-transform: uppercase;">Billed To</h3>
                    <div style="font-size: 14px; line-height: 1.6;">
                        <div style="font-weight: 600;">${user.name || '-'}</div>
                        <div>${profileData?.county || '-'}</div>
                        <div>${user.email || '-'}</div>
                        <div>${user.phone || '-'}</div>
                    </div>
                </div>
                <div>
                    <h3 style="margin: 0 0 8px 0; font-size: 12px; color: #999; text-transform: uppercase;">Invoice Details</h3>
                    <div style="font-size: 14px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span>Invoice No:</span>
                            <span style="font-weight: 600;">INV-${order.id}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span>Date:</span>
                            <span style="font-weight: 600;">${formatDate(order.created_at)}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span>Status:</span>
                            <span style="font-weight: 600;">${(order.order_status || order.status || 'pending').toUpperCase()}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div style="margin-bottom: 20px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead style="border-bottom: 1px solid #333;">
                        <tr>
                            <th style="text-align: left; padding: 8px 0; font-weight: 600;">Item</th>
                            <th style="text-align: center; padding: 8px 0; font-weight: 600;">Qty</th>
                            <th style="text-align: right; padding: 8px 0; font-weight: 600;">Unit Price</th>
                            <th style="text-align: right; padding: 8px 0; font-weight: 600;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${(order.items || []).map(item => `
                            <tr style="border-bottom: 1px solid #eee;">
                                <td style="padding: 8px 0;">${productCache[item.product_id] || `Product #${item.product_id}`}</td>
                                <td style="text-align: center; padding: 8px 0;">${item.quantity}</td>
                                <td style="text-align: right; padding: 8px 0;">${formatCurrency(item.unit_price)}</td>
                                <td style="text-align: right; padding: 8px 0;">${formatCurrency(item.total_price)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>

            <div style="margin-bottom: 20px; text-align: right; max-width: 300px; margin-left: auto;">
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #ddd;">
                    <span>Subtotal:</span>
                    <span>${formatCurrency(subtotal)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #ddd;">
                    <span>VAT (16%):</span>
                    <span>${formatCurrency(vat)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 12px 0; font-weight: 700; font-size: 16px;">
                    <span>Total:</span>
                    <span>${formatCurrency(order.total_amount)}</span>
                </div>
            </div>

            <div style="padding: 20px; background: #f9f9f9; border-radius: 8px; margin-bottom: 20px;">
                <h3 style="margin: 0 0 8px 0; font-size: 12px; color: #999; text-transform: uppercase;">Payment Status</h3>
                <div style="font-size: 14px; font-weight: 600;">${(order.payment_status || 'pending').toUpperCase()}</div>
            </div>

            ${order.note ? `
                <div style="padding: 12px; background: #fffacd; border-left: 4px solid var(--amber); border-radius: 4px;">
                    <h3 style="margin: 0 0 4px 0; font-size: 12px; font-weight: 600;">Note to Seller</h3>
                    <div style="font-size: 13px;">${order.note}</div>
                </div>
            ` : ''}
        </div>
    `;

        document.getElementById('invoice-print').innerHTML = invoiceHtml;

        // Auto-download invoice as HTML file
        const blob = new Blob([invoiceHtml], { type: 'text/html' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `INV-${orderId}.html`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error generating invoice:', error);
        showToast('Failed to generate invoice', 'error');
    }
}

function downloadInvoicePDF(orderId) {
    generateInvoice(orderId);
}

// ============================================
// LOGOUT
// ============================================

function logout() {
    if (confirm('Are you sure you want to log out?')) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        localStorage.removeItem('userRole');
        localStorage.removeItem('pms_cart');
        window.location.href = '../../auth/login/login.html';
    }
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('accessToken');
    const role = localStorage.getItem('userRole');

    if (!token) {
        window.location.href = '../../auth/login/login.html';
        return;
    }

    if (role && !['buyer', 'farmer'].includes(role)) {
        window.location.href = '../../auth/login/login.html';
        return;
    }

    try {
        const user = JSON.parse(localStorage.getItem('user') || '{}');

        const initials = (user.name || user.full_name || 'B')
            .split(' ')
            .map(n => n[0])
            .join('')
            .toUpperCase()
            .substring(0, 2);

        document.getElementById('sidebarAvatar').textContent = initials;
        document.getElementById('topbarAvatar').textContent = initials;
        document.getElementById('sidebarName').textContent = (user.name || user.full_name || 'Buyer');

        profileData = await api.buyer.getProfile();

        notificationsData = await api.get('/notifications/');
        updateNotificationBadge();

        ordersData = await api.buyer.getOrders();
        const activeOrdersCount = ordersData.filter(o =>
            ['pending', 'approved', 'shipped'].includes(o.order_status?.toLowerCase() || o.status?.toLowerCase())
        ).length;

        const ordersBadge = document.getElementById('ordersBadge');
        if (activeOrdersCount > 0) {
            ordersBadge.textContent = activeOrdersCount;
            ordersBadge.style.display = 'inline-block';
        }

        showPage('overview', document.querySelector('[data-page=overview]'));
    } catch (error) {
        console.error('Initialization error:', error);
        showToast('Failed to load buyer portal', 'error');
    }
});
