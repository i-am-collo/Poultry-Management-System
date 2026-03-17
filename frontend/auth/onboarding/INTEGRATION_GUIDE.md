# Onboarding Integration Guide

## Overview
This guide explains how to integrate the onboarding wizard with the rest of your PoultryHub system.

---

## 1. Modify `register.html` 

**File**: `frontend/auth/register/register.html`

After successful registration, redirect users to the onboarding wizard.

### Code Changes

Find the success handler in your register form's JavaScript. Replace it with:

```javascript
// In register.html submit handler (likely at the end of the auth.js file):

async function handleRegisterSuccess() {
  // Clear error messages
  document.getElementById('errorMsg').style.display = 'none';
  
  // Show success message
  const btn = document.getElementById('registerBtn');
  btn.disabled = true;
  btn.textContent = '✅ Account created!';
  btn.style.background = 'var(--g600, #16a34a)';
  
  // Store user info in localStorage (if needed)
  // localStorage.setItem('userEmail', email);
  
  // Wait 2 seconds then redirect to onboarding
  setTimeout(() => {
    window.location.href = '../onboarding/onboarding.html';
  }, 2000);
}
```

### Alternative: If Using api-client Pattern

If your register form uses the centralized `api-client.js`:

```javascript
// In register.html form submit handler:

async function onRegisterSubmit(e) {
  e.preventDefault();
  
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirmPassword').value;
  
  if (password !== confirmPassword) {
    showError('Passwords do not match');
    return;
  }
  
  try {
    const result = await api.auth.register({ email, password });
    
    // Success! Store token and user info
    localStorage.setItem('token', result.token);
    localStorage.setItem('user', JSON.stringify(result.user));
    localStorage.setItem('userRole', result.user.role || 'farmer');
    
    // Show success
    document.getElementById('successMsg').style.display = 'block';
    document.getElementById('successMsg').textContent = 'Account created! Redirecting…';
    
    // Redirect to onboarding after 1.5 seconds
    setTimeout(() => {
      window.location.href = '../onboarding/onboarding.html';
    }, 1500);
    
  } catch (error) {
    showError('Registration failed: ' + error.message);
  }
}
```

---

## 2. Modify Dashboards to Fetch & Display Onboarding Data

Each dashboard (farmer, supplier, buyer) needs to:
1. Fetch the user's profile from the API on page load
2. Display the onboarding data that was saved

### For `farmer.html` Dashboard

**File**: `frontend/main/farmer_dashboard/farmer.html`

Add this function to fetch farmer profile:

```javascript
// Add this function to farmer.html or farmer.css script section

async function loadFarmerProfile() {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      console.warn('No token found, redirecting to login');
      window.location.href = '../../auth/login/login.html';
      return;
    }
    
    const response = await fetch('http://localhost:8001/farmers/profile', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '../../auth/login/login.html';
      }
      throw new Error('Failed to load profile');
    }
    
    const profile = await response.json();
    
    // Display profile data in dashboard
    displayFarmerProfile(profile);
    
  } catch (error) {
    console.error('Error loading profile:', error);
    // Don't block dashboard, but show warning
    document.getElementById('profileWarning')?.style.display = 'block';
  }
}

function displayFarmerProfile(profile) {
  // Update dashboard elements with profile data
  // Adjust selectors based on your actual HTML structure
  
  if (document.getElementById('farmerName')) {
    document.getElementById('farmerName').textContent = profile.full_name || 'Farmer';
  }
  
  if (document.getElementById('farmName')) {
    document.getElementById('farmName').textContent = profile.farm_name || 'Your Farm';
  }
  
  if (document.getElementById('farmCounty')) {
    document.getElementById('farmCounty').textContent = profile.county || '—';
  }
  
  if (document.getElementById('farmSize')) {
    document.getElementById('farmSize').textContent = (profile.farm_size || 0) + ' acres';
  }
  
  if (document.getElementById('phoneNumber')) {
    document.getElementById('phoneNumber').textContent = profile.phone || '—';
  }
  
  // Display flocks if available
  if (profile.flocks && document.getElementById('flocksList')) {
    const flocksList = document.getElementById('flocksList');
    if (profile.flocks.length > 0) {
      flocksList.innerHTML = profile.flocks.map(flock => `
        <div style="padding:12px;background:var(--g50);border-radius:8px;margin-bottom:8px">
          <div style="font-weight:600;margin-bottom:4px">${flock.breed || 'Flock'}</div>
          <div style="font-size:13px;color:var(--text2)">
            🐔 ${flock.quantity} birds · ${flock.age_weeks || 0} weeks old
          </div>
        </div>
      `).join('');
    } else {
      flocksList.innerHTML = '<div style="color:var(--text2);font-size:13px">No flocks added yet. Add one from the Flock Management section.</div>';
    }
  }
}

// Call on page load
document.addEventListener('DOMContentLoaded', () => {
  loadFarmerProfile();
});
```

### For `supplier.html` Dashboard

**File**: `frontend/main/supplier-dashboard/supplier.html`

```javascript
// Add this to supplier.html

async function loadSupplierProfile() {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      window.location.href = '../../auth/login/login.html';
      return;
    }
    
    const response = await fetch('http://localhost:8001/suppliers/profile', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '../../auth/login/login.html';
      }
      throw new Error('Failed to load profile');
    }
    
    const profile = await response.json();
    displaySupplierProfile(profile);
    
  } catch (error) {
    console.error('Error loading profile:', error);
  }
}

function displaySupplierProfile(profile) {
  if (document.getElementById('businessName')) {
    document.getElementById('businessName').textContent = profile.business_name || 'Your Business';
  }
  
  if (document.getElementById('contactPerson')) {
    document.getElementById('contactPerson').textContent = profile.contact_person || '—';
  }
  
  if (document.getElementById('businessCounty')) {
    document.getElementById('businessCounty').textContent = profile.county || '—';
  }
  
  if (document.getElementById('businessPhone')) {
    document.getElementById('businessPhone').textContent = profile.phone || '—';
  }
  
  if (document.getElementById('businessEmail')) {
    document.getElementById('businessEmail').textContent = profile.email || '—';
  }
  
  // Display supply categories
  if (profile.categories && document.getElementById('supplyCats')) {
    document.getElementById('supplyCats').innerHTML = profile.categories
      .map(cat => `<span style="display:inline-block;background:var(--a50);color:var(--a700);padding:4px 10px;border-radius:4px;font-size:12px;margin-right:6px;margin-bottom:6px">${cat}</span>`)
      .join('');
  }
  
  // Display delivery counties
  if (profile.delivery_counties && document.getElementById('deliveryCounties')) {
    document.getElementById('deliveryCounties').innerHTML = profile.delivery_counties.join(', ') || '—';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadSupplierProfile();
});
```

### For `buyer.html` Dashboard

**File**: `frontend/main/buyer_dashboard/buyer.html`

```javascript
// Add this to buyer.html

async function loadBuyerProfile() {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      window.location.href = '../../auth/login/login.html';
      return;
    }
    
    const response = await fetch('http://localhost:8001/buyers/profile', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '../../auth/login/login.html';
      }
      throw new Error('Failed to load profile');
    }
    
    const profile = await response.json();
    displayBuyerProfile(profile);
    
  } catch (error) {
    console.error('Error loading profile:', error);
  }
}

function displayBuyerProfile(profile) {
  if (document.getElementById('buyerName')) {
    document.getElementById('buyerName').textContent = profile.full_name || 'Buyer';
  }
  
  if (document.getElementById('buyerBusiness')) {
    document.getElementById('buyerBusiness').textContent = profile.business_name || '—';
  }
  
  if (document.getElementById('buyerCounty')) {
    document.getElementById('buyerCounty').textContent = profile.county || '—';
  }
  
  if (document.getElementById('buyerPhone')) {
    document.getElementById('buyerPhone').textContent = profile.phone || '—';
  }
  
  if (document.getElementById('buyerEmail')) {
    document.getElementById('buyerEmail').textContent = profile.email || '—';
  }
  
  if (document.getElementById('buyerType')) {
    document.getElementById('buyerType').textContent = profile.buyer_type || '—';
  }
  
  // Display sourcing preferences
  if (profile.products_needed && document.getElementById('productsNeeded')) {
    document.getElementById('productsNeeded').textContent = profile.products_needed.join(', ') || '—';
  }
  
  if (document.getElementById('orderVolume')) {
    document.getElementById('orderVolume').textContent = profile.order_volume || '—';
  }
  
  if (document.getElementById('orderFrequency')) {
    document.getElementById('orderFrequency').textContent = profile.order_frequency || '—';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadBuyerProfile();
});
```

---

## 3. Ensure Backend Endpoints Exist

The onboarding wizard calls these POST endpoints for submission:
- `POST /farmers/register` 
- `POST /suppliers/register`
- `POST /buyers/register`

And the dashboards call these GET endpoints to fetch profiles:
- `GET /farmers/profile`
- `GET /suppliers/profile`
- `GET /buyers/profile`

**Verify these exist in your backend** ([backend/app/api/farmers.py](../../../backend/app/api/farmers.py), etc.). If they don't exist, add them based on your API design.

---

## 4. Optional: Add Edit Profile Feature

Users may want to return to onboarding to edit their information. Add an "Edit Profile" button in each dashboard that redirects to:

```javascript
// In dashboard, add button with onclick:
function editProfile() {
  window.location.href = '../../auth/onboarding/onboarding.html?mode=edit';
}
```

Then modify `onboarding.html` to detect `?mode=edit` and pre-populate forms with existing data.

---

## 5. Testing Checklist

- [ ] User registers → redirected to onboarding ✓
- [ ] Onboarding form submits → API receives correct payload
- [ ] Dashboard loads → fetches profile data successfully
- [ ] Dashboard displays → all form data shown correctly
- [ ] Re-registration not allowed (role locked after first setup) 
- [ ] Toast notifications show (errors, success)
- [ ] Mobile responsive (test on 640px and 500px widths)
- [ ] Back/change role buttons work correctly
- [ ] Token validation on all API calls

---

## 6. Common Issues

**Issue**: "Invalid token" errors from backend
**Solution**: Ensure `Authorization: Bearer <token>` header is sent correctly. Check `localStorage.getItem('token')`.

**Issue**: CORS errors when calling API
**Solution**: Verify backend `ALLOWED_ORIGINS` includes your frontend URL. See [config.py](../../../backend/config.py).

**Issue**: Profile data not populating in dashboard
**Solution**: Check API response structure matches the `displayXxxProfile()` function expectations. Log the response to console.

**Issue**: Redirect to onboarding doesn't work
**Solution**: Check relative path. From `register/register.html` to `onboarding/onboarding.html` should be `../onboarding/onboarding.html`.

---

## File Structure After Integration

```
frontend/
  auth/
    onboarding/
      onboarding.html          ✅ NEW
      onboarding.css           ✅ NEW
      onboarding.js            ✅ NEW
    register/
      register.html            ← MODIFIED
  main/
    farmer_dashboard/
      farmer.html              ← ADD loadFarmerProfile()
    supplier-dashboard/
      supplier.html            ← ADD loadSupplierProfile()
    buyer_dashboard/
      buyer.html               ← ADD loadBuyerProfile()
```

---

## Next Steps

1. ✅ Copy the three onboarding files to `frontend/auth/onboarding/`
2. ✅ Modify `register.html` redirect (see section 1)
3. ✅ Add profile fetch functions to each dashboard (see section 2)
4. ✅ Test the complete flow: Register → Onboarding → Dashboard
5. ✅ Verify backend endpoints exist and return correct data structure
6. ⏳ Optional: Add edit profile button and pre-population logic

---

**Questions?** Check [ARCHITECTURE.md](../../../ARCHITECTURE.md) for system overview or review the backend API routes in [main.py](../../../backend/app/main.py).
