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

            const data = await response.json();

            if (!response.ok) {
                const error = new Error(data.detail || `HTTP ${response.status}`);
                error.status = response.status;
                error.data = data;
                throw error;
            }

            return data;
        } catch (error) {
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
        getFlocks: () => this.get('/farmers/flocks'),
        updateFlock: (id, data) => this.put(`/farmers/flocks/${id}`, data),
        deleteFlock: (id) => this.delete(`/farmers/flocks/${id}`),
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
        inviteFarm: (data) => this.post('/suppliers/invite-farm', data),
    };

    /**
     * Buyer API endpoints (optional - add as needed)
     */
    buyer = {
        getAllProducts: () => this.get('/buyers/search'),
        searchProducts: (query) => this.get(`/buyers/search?q=${query}`),
        createOrder: (data) => this.post('/buyers/orders', data),
        getOrders: () => this.get('/buyers/orders'),
        getOrder: (id) => this.get(`/buyers/orders/${id}`),
    };
}

// Create global API client instance
const api = new APIClient();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIClient, api };
}
