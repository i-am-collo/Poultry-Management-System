/**
 * Centralized API Client
 * Handles all API requests with automatic token refresh and error handling
 */

const API_BASE_URL = 'http://127.0.0.1:8001';

class APIClient {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    /**
     * Get access token from localStorage
     */
    getAccessToken() {
        return localStorage.getItem('accessToken');
    }

    /**
     * Get refresh token from localStorage
     */
    getRefreshToken() {
        return localStorage.getItem('refreshToken');
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.getAccessToken();
    }

    /**
     * Refresh access token using refresh token
     */
    async refreshTokens() {
        try {
            const refreshToken = this.getRefreshToken();
            if (!refreshToken) {
                throw new Error('No refresh token available');
            }

            const response = await fetch(`${this.baseURL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh_token: refreshToken }),
            });

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }

            const data = await response.json();

            // Store new tokens
            localStorage.setItem('accessToken', data.access_token);
            localStorage.setItem('refreshToken', data.refresh_token);
            localStorage.setItem('user', JSON.stringify(data.user));

            return data.access_token;
        } catch (error) {
            // Clear auth data and redirect to login
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('user');
            localStorage.removeItem('userRole');
            window.location.href = '/auth/login/login.html';
            throw error;
        }
    }

    /**
     * Make HTTP request with automatic token refresh
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        let token = this.getAccessToken();

        // Add authorization header if token exists
        if (token) {
            options.headers = options.headers || {};
            options.headers['Authorization'] = `Bearer ${token}`;
        }

        // Set default content type
        if (!options.headers) {
            options.headers = {};
        }
        if (options.body && !options.headers['Content-Type']) {
            options.headers['Content-Type'] = 'application/json';
        }

        try {
            let response = await fetch(url, options);

            // If 401, try refreshing token and retry
            if (
                response.status === 401 &&
                endpoint !== '/auth/login' &&
                endpoint !== '/auth/register' &&
                endpoint !== '/auth/refresh'
            ) {
                token = await this.refreshTokens();
                options.headers['Authorization'] = `Bearer ${token}`;
                response = await fetch(url, options);
            }

            let data;
            try {
                data = await response.json();
            } catch (parseError) {
                console.error('Failed to parse JSON response:', parseError);
                console.error('Response text:', await response.text());
                throw new Error(`Invalid response format from server. Status: ${response.status}`);
            }

            if (!response.ok) {
                let errorMessage = `HTTP ${response.status}`;

                // Handle FastAPI validation errors
                if (Array.isArray(data.detail)) {
                    errorMessage = data.detail.map(err => {
                        if (typeof err === 'object' && err.msg) {
                            return `${err.msg} (field: ${Array.isArray(err.loc) ? err.loc.join('.') : 'unknown'})`;
                        }
                        return String(err);
                    }).join('; ');
                } else if (typeof data.detail === 'string') {
                    errorMessage = data.detail;
                } else if (typeof data.detail === 'object' && data.detail.message) {
                    errorMessage = data.detail.message;
                }

                console.error(`API Error [${response.status}]:`, errorMessage, data);
                const error = new Error(errorMessage);
                error.status = response.status;
                error.data = data;
                throw error;
            }

            return data;
        } catch (error) {
            console.error(`Fetch failed for ${endpoint}:`, error);
            console.error('Full error object:', error);
            // Improve error message for network errors
            if (error instanceof TypeError && error.message === 'Failed to fetch') {
                const detailedError = new Error(`Network error: Unable to reach backend at ${url}. Make sure the server is running on port 8001.`);
                detailedError.status = 0;
                detailedError.originalError = error;
                throw detailedError;
            }
            throw error;
        }
    }

    /**
     * GET request
     */
    get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'GET' });
    }

    /**
     * POST request
     */
    post(endpoint, body, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'POST',
            body: JSON.stringify(body),
        });
    }

    /**
     * PUT request
     */
    put(endpoint, body, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(body),
        });
    }

    /**
     * DELETE request
     */
    delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'DELETE' });
    }

    /**
     * PATCH request
     */
    patch(endpoint, body, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PATCH',
            body: JSON.stringify(body),
        });
    }

    /**
     * Authentication API endpoints
     */
    auth = {
        register: (data) => this.post('/auth/register', data),
        login: (data) => this.post('/auth/login', data),
        refresh: (refreshToken) => this.post('/auth/refresh', { refresh_token: refreshToken }),
        forgotPassword: (data) => this.post('/auth/forgot-password', data),
        resetPassword: (data) => this.post('/auth/reset-password', data),
        logout: () => {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('user');
            localStorage.removeItem('userRole');
        },
    };

    /**
     * Farmer API endpoints (optional - add as needed)
     */
    farmer = {
        registerFlock: (data) => this.post('/farmers/register-flock', data),
        getFlocks: () => this.get('/farmers/flocks'), getFlockById: (id) => this.get(`/farmers/flocks/${id}`), updateFlock: (id, data) => this.put(`/farmers/flocks/${id}`, data),
        deleteFlock: (id) => this.delete(`/farmers/flocks/${id}`),
        getFarmProfile: () => this.get('/farmers/farm-profile'),
        createFarmProfile: (data) => this.post('/farmers/farm-profile', data),
        updateFarmProfile: (data) => this.put('/farmers/farm-profile', data),
        // Farmer product management
        addProduct: (data) => this.post('/farmers/products', data),
        getProducts: () => this.get('/farmers/products'),
        updateProduct: (id, data) => this.put(`/farmers/products/${id}`, data),
        deleteProduct: (id) => this.delete(`/farmers/products/${id}`),
        // Farmer order management
        getOrders: () => this.get('/farmers/orders'),
        dispatchOrder: (id) => this.put(`/farmers/orders/${id}/dispatch`, {}),
        // Farmer invitations & messaging
        getPendingInvitations: () => this.get('/farmers/invitations/pending'),
        acceptInvitation: (id) => this.put(`/farmers/invitations/${id}/accept`, {}),
        declineInvitation: (id) => this.put(`/farmers/invitations/${id}/decline`, {}),
        getConnectedSuppliers: () => this.get('/farmers/suppliers/connected'),
        getMessagesWithSupplier: (supplierId) => this.get(`/farmers/messages/${supplierId}`),
        sendMessageToSupplier: (supplierId, message) => this.post(`/farmers/messages/${supplierId}`, { content: message }),
        // Browse & connect with suppliers
        getAllSuppliers: () => this.get('/farmers/all-suppliers'),
        requestSupplierConnection: (supplierId, invitationData) => this.post(`/farmers/suppliers/${supplierId}/request-connection`, invitationData),
    };

    /**
     * Supplier API endpoints (optional - add as needed)
     */
    supplier = {
        addProduct: (data) => this.post('/suppliers/products', data),
        getProducts: () => this.get('/suppliers/products'),
        updateProduct: (id, data) => this.put(`/suppliers/products/${id}`, data),
        deleteProduct: (id) => this.delete(`/suppliers/products/${id}`),
        getOrders: () => this.get('/suppliers/orders'),
        getOrder: (id) => this.get(`/suppliers/orders/${id}`),
        updateOrderStatus: (id, status) => this.patch(`/suppliers/orders/${id}`, { status }),
        getCustomers: () => this.get('/suppliers/customers'),
        getCustomerStats: () => this.get('/suppliers/customers/stats'),
        getAllAvailableFarms: () => this.get('/suppliers/all-farms'),
        inviteFarm: (data) => this.post('/suppliers/invite-farm', data),
    };

    /**
     * Buyer API endpoints (optional - add as needed)
     */
    buyer = {
        getProfile: () => this.get('/buyers/profile'),
        getAllProducts: () => this.get('/buyers/search'),
        searchProducts: (query) => this.get(`/buyers/search?q=${query}`),
        createOrder: (data) => this.post('/buyers/orders', data),
        getOrders: () => this.get('/buyers/orders'),
        getOrder: (id) => this.get(`/buyers/orders/${id}`),

        // Marketplace endpoints with pagination and filtering
        getMarketplaceProducts: (filters = {}) => {
            const params = new URLSearchParams();
            if (filters.search) params.append('search', filters.search);
            if (filters.category && filters.category !== 'all' && filters.category !== 'All')
                params.append('category', filters.category);
            if (filters.source && filters.source !== 'all')
                params.append('source', filters.source);
            if (filters.min_price !== undefined && filters.min_price !== null)
                params.append('min_price', filters.min_price);
            if (filters.max_price !== undefined && filters.max_price !== null)
                params.append('max_price', filters.max_price);
            if (filters.in_stock === true)
                params.append('in_stock', 'true');
            params.append('page', filters.page || 1);
            params.append('limit', filters.limit || 20);
            return this.get('/buyers/products?' + params.toString());
        },

        getProductDetail: (productId) => this.get(`/buyers/products/${productId}`),
        getSellerProfile: (sellerId) => this.get(`/buyers/sellers/${sellerId}`),
        getStockStatus: (productId) => this.get(`/buyers/products/${productId}/stock`),
        cancelOrder: (orderId) => this.post(`/buyers/orders/${orderId}/cancel`, {}),
    };

    /**
     * Notifications API endpoints
     */
    notifications = {
        list: () => this.get('/notifications'),
        get: (id) => this.get(`/notifications/${id}`),
        markAsRead: (id) => this.put(`/notifications/${id}`, { is_read: true }),
        markAllAsRead: () => this.put('/notifications/mark-all-read', {}),
        delete: (id) => this.delete(`/notifications/${id}`),
        deleteAll: () => this.delete('/notifications'),
    };
}

/**
 * Auto-Refresh Manager
 * Handles periodic polling of data and immediate refresh triggers
 * Pauses polling when browser tab is hidden (visibility detection)
 */
class AutoRefreshManager {
    constructor() {
        this.intervals = {};  // Store interval IDs by data key
        this.isVisible = true;
        this.setupVisibilityListener();
    }

    /**
     * Setup visibility listener to pause/resume polling
     */
    setupVisibilityListener() {
        document.addEventListener('visibilitychange', () => {
            this.isVisible = !document.hidden;

            if (this.isVisible) {
                // Resume all active intervals when tab becomes visible
                console.log('🔄 Tab visible - resuming auto-refresh');
                Object.keys(this.intervals).forEach(key => {
                    if (this.intervals[key].func) {
                        this.intervals[key].func();
                    }
                });
            } else {
                // Pause all intervals when tab is hidden (optional - can keep running)
                console.log('⏸️ Tab hidden - pausing auto-refresh');
            }
        });
    }

    /**
     * Register a data refresh function with periodic polling
     * @param {string} key - Unique identifier for this refresh (e.g., 'buyerOrders')
     * @param {Function} refreshFunc - Async function to call for refresh
     * @param {number} intervalMs - Interval in milliseconds (default 5000ms)
     */
    register(key, refreshFunc, intervalMs = 5000) {
        if (typeof refreshFunc !== 'function') {
            console.warn(`AutoRefreshManager: refreshFunc for "${key}" is not a function`);
            return;
        }

        // Clear existing interval if it exists
        if (this.intervals[key]) {
            clearInterval(this.intervals[key].id);
        }

        // Store the function and start polling
        this.intervals[key] = {
            func: refreshFunc,
            interval: intervalMs,
            id: setInterval(() => {
                if (this.isVisible) {
                    refreshFunc().catch(err => {
                        console.warn(`AutoRefreshManager: Error in ${key}:`, err);
                    });
                }
            }, intervalMs),
        };

        console.log(`✅ Registered auto-refresh: ${key} (${intervalMs}ms)`);
    }

    /**
     * Unregister a refresh function (stop polling)
     * @param {string} key - Identifier of the refresh to stop
     */
    unregister(key) {
        if (this.intervals[key]) {
            clearInterval(this.intervals[key].id);
            delete this.intervals[key];
            console.log(`⏹️ Unregistered auto-refresh: ${key}`);
        }
    }

    /**
     * Immediately trigger a refresh (no delay)
     * @param {string} key - Identifier of the refresh to trigger
     */
    async trigger(key) {
        if (this.intervals[key] && typeof this.intervals[key].func === 'function') {
            try {
                await this.intervals[key].func();
                console.log(`🔄 Triggered refresh: ${key}`);
            } catch (err) {
                console.warn(`AutoRefreshManager: Error triggering ${key}:`, err);
            }
        }
    }

    /**
     * Get list of registered refresh keys
     */
    getRegistered() {
        return Object.keys(this.intervals);
    }

    /**
     * Clear all registered refreshes
     */
    clearAll() {
        Object.keys(this.intervals).forEach(key => this.unregister(key));
        console.log('🗑️ Cleared all auto-refresh registrations');
    }
}

// Create global API client instance
const api = new APIClient();

// Create global auto-refresh manager instance
const autoRefresh = new AutoRefreshManager();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIClient, api, AutoRefreshManager, autoRefresh };
}
