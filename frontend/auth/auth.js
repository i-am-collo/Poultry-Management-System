/**
 * Authentication Module
 * Handles registration, login, forgot password, and reset password flows
 */

// ==================== UTILITY FUNCTIONS ====================

/**
 * Validates email format
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validates phone number format
 */
function validatePhone(phone) {
    const re = /^[\d\s\-\+\(\)]+$/;
    return phone.length >= 10 && re.test(phone);
}

/**
 * Shows error message for a form field
 */
function showError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const errorSpan = document.getElementById(fieldId + 'Error');

    if (field) {
        field.classList.add('error');
    }
    if (errorSpan) {
        errorSpan.textContent = message;
        errorSpan.classList.add('show');
    }
}

/**
 * Clears error message for a form field
 */
function clearError(fieldId) {
    const field = document.getElementById(fieldId);
    const errorSpan = document.getElementById(fieldId + 'Error');

    if (field) {
        field.classList.remove('error');
    }
    if (errorSpan) {
        errorSpan.classList.remove('show');
    }
}

/**
 * Shows a message to the user
 */
function showMessage(message, type = 'success') {
    const messageDiv = document.getElementById('message');
    if (messageDiv) {
        messageDiv.textContent = message;
        messageDiv.className = `message ${type}`;
        messageDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

/**
 * Hides the message div
 */
function hideMessage() {
    const messageDiv = document.getElementById('message');
    if (messageDiv) {
        messageDiv.className = 'message';
    }
}



/**
 * Stores authentication data in localStorage
 */
function storeAuthData(accessToken, refreshToken, user) {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('userRole', user.role);
}

/**
 * Retrieves access token from localStorage
 */
function getAuthToken() {
    return localStorage.getItem('accessToken');
}

/**
 * Retrieves refresh token from localStorage
 */
function getRefreshToken() {
    return localStorage.getItem('refreshToken');
}

/**
 * Get user data from localStorage
 */
function getStoredUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

/**
 * Clears all authentication data
 */
function clearAuthData() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    localStorage.removeItem('userRole');
}

/**
 * Refreshes access token using refresh token
 */
async function refreshAccessToken() {
    try {
        const refreshToken = getRefreshToken();
        if (!refreshToken) {
            clearAuthData();
            window.location.href = './login/login.html';
            return null;
        }

        const response = await api.auth.refresh(refreshToken);

        // Store new tokens
        storeAuthData(response.access_token, response.refresh_token, response.user);
        return response.access_token;
    } catch (error) {
        clearAuthData();
        window.location.href = './login/login.html';
        return null;
    }
}

// ==================== REGISTRATION HANDLER ====================

/**
 * Initialize registration form handler
 */
function initializeRegistrationForm() {
    const form = document.getElementById('registrationForm');
    const submitBtn = document.getElementById('submitBtn');

    if (!form) return;

    // Real-time validation
    document.getElementById('firstName')?.addEventListener('blur', function () {
        if (this.value.trim() === '') {
            showError('firstName', 'Please enter your first name');
        } else {
            clearError('firstName');
        }
    });

    document.getElementById('lastName')?.addEventListener('blur', function () {
        if (this.value.trim() === '') {
            showError('lastName', 'Please enter your last name');
        } else {
            clearError('lastName');
        }
    });

    document.getElementById('email')?.addEventListener('blur', function () {
        if (this.value && !validateEmail(this.value)) {
            showError('email', 'Please enter a valid email address');
        } else {
            clearError('email');
        }
    });

    document.getElementById('phone')?.addEventListener('blur', function () {
        if (this.value && !validatePhone(this.value)) {
            showError('phone', 'Please enter a valid phone number');
        } else {
            clearError('phone');
        }
    });

    document.getElementById('password')?.addEventListener('blur', function () {
        if (this.value && this.value.length < 8) {
            showError('password', 'Password must be at least 8 characters');
        } else {
            clearError('password');
        }
    });

    document.getElementById('confirmPassword')?.addEventListener('blur', function () {
        const password = document.getElementById('password').value;
        if (this.value !== password) {
            showError('confirmPassword', 'Passwords do not match');
        } else {
            clearError('confirmPassword');
        }
    });

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideMessage();

        // Get form values
        const firstName = document.getElementById('firstName').value.trim();
        const lastName = document.getElementById('lastName').value.trim();
        const email = document.getElementById('email').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const role = document.getElementById('role').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        // Validate all fields
        let hasErrors = false;

        if (!firstName) {
            showError('firstName', 'Please enter your first name');
            hasErrors = true;
        }

        if (!lastName) {
            showError('lastName', 'Please enter your last name');
            hasErrors = true;
        }

        if (!email || !validateEmail(email)) {
            showError('email', 'Please enter a valid email address');
            hasErrors = true;
        }

        if (!phone || !validatePhone(phone)) {
            showError('phone', 'Please enter a valid phone number');
            hasErrors = true;
        }

        if (!role) {
            showError('role', 'Please select a role');
            hasErrors = true;
        }

        if (!password || password.length < 8) {
            showError('password', 'Password must be at least 8 characters');
            hasErrors = true;
        }

        if (password !== confirmPassword) {
            showError('confirmPassword', 'Passwords do not match');
            hasErrors = true;
        }

        if (hasErrors) {
            showMessage('Please fix the errors above', 'error');
            return;
        }

        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.textContent = 'Registering...';

        try {
            const response = await api.auth.register({
                name: `${firstName} ${lastName}`,
                email,
                phone,
                role,
                password,
            });

            showMessage('Registration successful! Redirecting to login...', 'success');

            // Redirect to login page after 2 seconds
            setTimeout(() => {
                window.location.href = '../login/login.html';
            }, 2000);
        } catch (error) {
            showMessage(error.message || 'Registration failed. Please try again.', 'error');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Register';
        }
    });
}

// ==================== LOGIN HANDLER ====================

/**
 * Initialize login form handler
 */
function initializeLoginForm() {
    const form = document.getElementById('loginForm');
    const submitBtn = document.getElementById('submitBtn');

    if (!form) return;

    // Real-time validation
    document.getElementById('email')?.addEventListener('blur', function () {
        if (this.value && !validateEmail(this.value)) {
            showError('email', 'Please enter a valid email address');
        } else {
            clearError('email');
        }
    });

    document.getElementById('password')?.addEventListener('blur', function () {
        if (this.value === '') {
            showError('password', 'Please enter your password');
        } else {
            clearError('password');
        }
    });

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideMessage();

        // Get form values
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const remember = document.getElementById('remember')?.checked || false;

        // Validate fields
        let hasErrors = false;

        if (!email || !validateEmail(email)) {
            showError('email', 'Please enter a valid email address');
            hasErrors = true;
        }

        if (!password) {
            showError('password', 'Please enter your password');
            hasErrors = true;
        }

        if (hasErrors) {
            showMessage('Please fix the errors above', 'error');
            return;
        }

        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.textContent = 'Signing In...';

        // Log credentials for debugging
        console.log('📤 Login credentials:', {
            email: email,
            password: '***hidden***' // Don't log actual password
        });

        try {
            console.log('📤 Sending login request to /auth/login');
            const response = await api.auth.login({
                email,
                password,
            });

            console.log('✅ Login response:', response);

            // Store authentication data with access and refresh tokens
            storeAuthData(response.access_token, response.refresh_token, response.user);

            showMessage('Login successful! Redirecting...', 'success');

            // Redirect based on user role
            setTimeout(() => {
                const role = response.user.role;
                switch (role) {
                    case 'farmer':
                        window.location.href = '../../main/farmer_dashboard/farmer.html';
                        break;
                    case 'supplier':
                        window.location.href = '../../main/supplier-dashboard/supplier.html';
                        break;
                    case 'buyer':
                        window.location.href = '../../main/buyer_dashboard/buyer.html';
                        break;
                    default:
                        window.location.href = '../../index.html';
                }
            }, 1500);
        } catch (error) {
            console.error('❌ Login error:', error);
            showMessage(error.message || 'Login failed. Please check your credentials.', 'error');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Sign In';
        }
    });
}

// ==================== FORGOT PASSWORD HANDLER ====================

/**
 * Initialize forgot password form handler
 */
function initializeForgotPasswordForm() {
    const form = document.getElementById('forgotPasswordForm');
    const submitBtn = document.getElementById('submitBtn');

    if (!form) return;

    // Real-time validation
    document.getElementById('email')?.addEventListener('blur', function () {
        if (this.value && !validateEmail(this.value)) {
            showError('email', 'Please enter a valid email address');
        } else {
            clearError('email');
        }
    });

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideMessage();

        // Get form value
        const email = document.getElementById('email').value.trim();

        // Validate email
        if (!email || !validateEmail(email)) {
            showError('email', 'Please enter a valid email address');
            showMessage('Please enter a valid email address', 'error');
            return;
        }

        clearError('email');

        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.textContent = 'Sending...';

        try {
            const response = await api.auth.forgotPassword({
                email,
            });

            showMessage(
                'If the email exists, password reset instructions will be sent.',
                'success'
            );

            // Reset form
            form.reset();

            // Redirect to login after 3 seconds
            setTimeout(() => {
                window.location.href = '../login/login.html';
            }, 3000);
        } catch (error) {
            showMessage(
                error.message || 'Failed to send reset link. Please try again.',
                'error'
            );
            submitBtn.disabled = false;
            submitBtn.textContent = 'Send Reset Link';
        }
    });
}

// ==================== RESET PASSWORD HANDLER ====================

/**
 * Initialize reset password form handler
 */
function initializeResetPasswordForm() {
    const form = document.getElementById('resetPasswordForm');
    const submitBtn = document.getElementById('submitBtn');

    if (!form) return;

    // Get reset token from URL
    const urlParams = new URLSearchParams(window.location.search);
    const resetToken = urlParams.get('token');

    // Check if token exists
    if (!resetToken) {
        showMessage('Invalid or missing reset link. Please request a new one.', 'error');
        submitBtn.disabled = true;
    }

    // Real-time validation
    document.getElementById('newPassword')?.addEventListener('blur', function () {
        if (this.value && this.value.length < 8) {
            showError('newPassword', 'Password must be at least 8 characters');
        } else {
            clearError('newPassword');
        }
    });

    document.getElementById('confirmPassword')?.addEventListener('blur', function () {
        const newPassword = document.getElementById('newPassword').value;
        if (this.value !== newPassword) {
            showError('confirmPassword', 'Passwords do not match');
        } else {
            clearError('confirmPassword');
        }
    });

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideMessage();

        // Get form values
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        // Validate passwords
        let hasErrors = false;

        if (!newPassword || newPassword.length < 8) {
            showError('newPassword', 'Password must be at least 8 characters');
            hasErrors = true;
        }

        if (newPassword !== confirmPassword) {
            showError('confirmPassword', 'Passwords do not match');
            hasErrors = true;
        }

        if (hasErrors) {
            showMessage('Please fix the errors above', 'error');
            return;
        }

        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.textContent = 'Resetting...';

        try {
            const response = await api.auth.resetPassword({
                token: resetToken,
                new_password: newPassword,
            });

            showMessage('Password reset successful! Redirecting to login...', 'success');

            // Redirect to login after 2 seconds
            setTimeout(() => {
                window.location.href = '../login/login.html';
            }, 2000);
        } catch (error) {
            showMessage(
                error.message || 'Failed to reset password. Please try again.',
                'error'
            );
            submitBtn.disabled = false;
            submitBtn.textContent = 'Reset Password';
        }
    });
}

// ==================== INITIALIZATION ====================

/**
 * Initialize all auth forms when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', () => {
    // Initialize appropriate form based on current page
    if (document.getElementById('registrationForm')) {
        initializeRegistrationForm();
    }

    if (document.getElementById('loginForm')) {
        initializeLoginForm();
    }

    if (document.getElementById('forgotPasswordForm')) {
        initializeForgotPasswordForm();
    }

    if (document.getElementById('resetPasswordForm')) {
        initializeResetPasswordForm();
    }
});

// Export functions for external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        validateEmail,
        validatePhone,
        showError,
        clearError,
        showMessage,
        hideMessage,
        storeAuthData,
        getAuthToken,
        getRefreshToken,
        getStoredUser,
        clearAuthData,
        refreshAccessToken,
    };
}
