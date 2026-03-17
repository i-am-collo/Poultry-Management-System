# Onboarding Wizard - Quick Reference

## Files Created

| File | Size | Purpose |
|------|------|---------|
| `onboarding.html` | ~18 KB | Main markup with role picker and 3 form shells |
| `onboarding.css` | ~13 KB | Complete styling (separated from HTML) |
| `onboarding.js` | ~15 KB | Form logic, API integration, state management |
| `INTEGRATION_GUIDE.md` | — | Step-by-step integration instructions |

**Location**: `frontend/auth/onboarding/`

---

## Quick Integration Steps

### 1. **Register Flow** 
After successful registration, add redirect:
```javascript
setTimeout(() => {
  window.location.href = '../onboarding/onboarding.html';
}, 1500);
```

### 2. **Farmer Dashboard** 
Add to `farmer.html` page load:
```javascript
document.addEventListener('DOMContentLoaded', loadFarmerProfile);
```

### 3. **Supplier Dashboard** 
Add to `supplier.html` page load:
```javascript
document.addEventListener('DOMContentLoaded', loadSupplierProfile);
```

### 4. **Buyer Dashboard** 
Add to `buyer.html` page load:
```javascript
document.addEventListener('DOMContentLoaded', loadBuyerProfile);
```

---

## Key Features

✅ **Role-Based Setup**
- Farmer: 3 steps (farm info → flocks → review)
- Supplier: 2 steps (business info → review)
- Buyer: 3 steps (profile → preferences → review)

✅ **Dynamic Forms**
- Add/remove flocks (farmer) or products (supplier)
- Chip toggles for multi-select options
- Real-time form validation

✅ **Data Persistence**
- Forms submit to backend endpoints
- Data displays in role-specific dashboards
- Success screen before redirect

✅ **Code Organization**
- Separated CSS (styling only)
- Separated JS (logic only)
- HTML markup (structure only)
- No inline styles or scripts

✅ **Theming**
- Dynamic role-based colors via CSS variables
- Responsive design (640px & 500px breakpoints)
- Smooth animations and transitions

---

## Database Fields Submitted

### Farmer → `/farmers/register`
```javascript
{
  full_name: string,
  farm_name: string,
  county: string,
  phone: string,
  farm_size: number,
  description: string,
  flocks: [
    {
      breed: string,
      quantity: number,
      age_weeks: number,
      health_status: string,
      feed_per_day_kg: number
    }
  ]
}
```

### Supplier → `/suppliers/register`
```javascript
{
  business_name: string,
  contact_person: string,
  county: string,
  phone: string,
  email: string,
  kra_pin: string,
  business_reg_no: string,
  description: string,
  categories: string[],
  delivery_counties: string[],
  payment_mpesa_till: string,
  payment_bank_account: string
}
```

### Buyer → `/buyers/register`
```javascript
{
  full_name: string,
  business_name: string,
  county: string,
  phone: string,
  email: string,
  buyer_type: string,
  products_needed: string[],
  order_volume: string,
  order_frequency: string,
  max_price_per_unit: number,
  max_distance_km: number,
  quality_preferences: string[],
  delivery_address: string,
  preferred_payment: string,
  mpesa_number: string
}
```

---

## API Endpoints Required

**Registration (POST)**
- `POST /farmers/register`
- `POST /suppliers/register`
- `POST /buyers/register`

**Profile Fetch (GET)**
- `GET /farmers/profile`
- `GET /suppliers/profile`
- `GET /buyers/profile`

All requests use `Authorization: Bearer <token>` header.

---

## CSS Variables Used

### Colors (Farmer - Green)
`--g50` through `--g900`

### Colors (Supplier - Amber)
`--a50` through `--a900`

### Colors (Buyer - Blue)
`--b50` through `--b900`

### Semantic
`--role-50` through `--role-900` (dynamically set by `selectRole()`)

### Typography
`--text1` (dark), `--text2` (muted), `--text3` (very muted)

### Surfaces
`--surface`, `--surface-alt`, `--border`

---

## Form Field Types

**Text Inputs**: `.fi` class
- Full name, business name, addresses, etc.

**Select Dropdowns**: `.fs` class
- Counties, bird types, categories, etc.

**Textareas**: `.ft` class
- Descriptions, notes

**Chip Toggles**: `.chip` class
- Multi-select (farmer type, categories, quality preferences)

**File Uploads**: `:file` input type
- Photo previews via FileReader API

---

## JavaScript Functions Reference

| Function | Purpose |
|----------|---------|
| `selectRole(role)` | Switch active role and update theming |
| `launchForm()` | Show form, hide role picker |
| `changeRole()` | Return to role picker |
| `fGoStep(n)`, etc. | Navigate between steps |
| `addFlock()` | Add flock entry (farmer) |
| `addProduct()` | Add product entry (supplier) |
| `buildXxxReview()` | Generate review card HTML |
| `submitForm(prefix)` | Post data to API and redirect |
| `v(id)` | Get input value by ID |
| `chips(groupId)` | Get selected chip values |
| `toast(msg)` | Show notification |

---

## Customization Tips

**Change Colors**:
Edit CSS variables in `onboarding.css` `:root` section (lines 5-35).

**Add Form Fields**:
1. Add `<input>` to HTML
2. Map field name in `submitForm()` payload
3. Update backend schema

**Modify Steps**:
1. Adjust progress indicator (`.progress-bar`)
2. Add/remove `.step` divs
3. Update step navigation functions

**Pre-populate (Edit Mode)**:
Detect `?mode=edit` in URL, fetch existing data, populate inputs.

---

## Browser Compatibility

- ✅ Chrome/Edge (88+)
- ✅ Firefox (85+)
- ✅ Safari (14+)
- ✅ Mobile browsers

Uses:
- ES6+ JavaScript (arrow functions, template literals)
- Fetch API + Async/await
- FileReader API
- CSS Custom Properties (CSS Variables)

---

## File Size Summary

```
Total: ~46 KB (uncompressed)
  - HTML: ~18 KB
  - CSS: ~13 KB
  - JS: ~15 KB
```

Minified: ~20-25 KB (typical)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Forms not submitting | Check token in localStorage, verify API endpoint exists |
| Styling not applying | Verify `onboarding.css` is linked in HTML head |
| Step navigation broken | Check that form IDs match function IDs (e.g., `f-step-1`) |
| Images not previewing | Ensure FileReader API supported (all modern browsers) |
| Dashboard data not showing | Verify `/profile` endpoint returns correct field names |

---

## Next: Dashboard Integration

See **INTEGRATION_GUIDE.md** for detailed setup steps.
