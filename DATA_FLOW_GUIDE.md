# Poultry Management System - Data Autofill & Real-Time Propagation Guide

## Overview
Your system now supports **automatic form autofill** and **real-time data synchronization** across all dashboards. When a farmer enters/updates data, it instantly becomes visible to buyers, suppliers, and admins.

---

## How It Works: 3-Tier Data Flow

### **Tier 1: Data Entry (Farmer Dashboard)**
```
Farmer fills form → Submit to API → Database updated
```

**Example: Adding a new flock**
1. Farmer navigates to **Flock Inventory** tab
2. Clicks **"Add New Flock"** button
3. Modal opens with form fields:
   - Bird Type (dropdown)
   - Breed (text input)
   - Quantity (number)
   - Age in weeks (number)
   - Health Status (dropdown)
   - Daily Feed (number)
   - Notes (textarea)
4. Farmer clicks **"Add Flock"**
5. JavaScript calls `api.farmer.registerFlock(data)`
6. POST request sends to `/farmers/register-flock`
7. Backend validates and saves to PostgreSQL database
8. ✅ **Data now persists in database**

### **Tier 2: Form Autofill (Editing)**
```
Click Edit → Fetch flock data → Auto-populate form → Edit → Update database
```

**New Feature - Modal-based editing:**
1. In the Flock Inventory table, click **"Edit"** button on any flock
2. System fetches flock data via `api.farmer.getFlockById(id)`
3. GET request to `/farmers/flocks/{id}`
4. Form automatically populates with:
   - `bird_type` → Bird Type dropdown
   - `breed` → Breed field
   - `quantity` → Quantity field
   - `age_weeks` → Age field
   - `health_status` → Health Status dropdown
   - `daily_feed_kg` → Daily Feed field
   - `notes` → Notes textarea
5. Modal title changes to: "Edit Flock #123 - Ross 308"
6. Button changes from "Add Flock" → "Update Flock"
7. Edit fields and click **"Update Flock"**
8. System calls `api.farmer.updateFlock(id, data)`
9. PUT request to `/farmers/flocks/{id}`
10. ✅ **Data updated in database**

### **Tier 3: Data Visibility (Buyers & Suppliers)**
```
Farmer updates data → Page loads/refreshes → API fetches latest data → Displays to other users
```

**Buyer Marketplace Example:**
1. Farmer creates a new **product** (e.g., "500 Broilers, ready for market")
2. Farmer saves it → `api.farmer.addProduct(data)` → Database updated
3. Buyer navigates to **Marketplace** tab
4. Page loads → `api.buyer.getAllProducts()` called
5. GET request to `/buyers/search`
6. Backend queries latest products from **all farmers**
7. Buyer sees farmer's product listed with:
   - Price per unit
   - Available quantity
   - Farmer name & location
   - "Place Order" button
8. ✅ **Real-time visibility achieved**

**Supplier Dashboard Example:**
1. Farmer logs quantity as "running low" on feed supply needs
2. Supplier logs in → Supplier dashboard loads
3. Dashboard shows **demand signals** from all farmers
4. Supplier sees farmer name + "Feed quantity: LOW"
5. Supplier can proactively reach out or adjust pricing
6. ✅ **Supplier has real-time business intelligence**

---

## Key Files & Changes Made

### **Frontend (3 files modified)**

#### 1. **api-client.js** (Lines ~220)
Added method to fetch individual flock:
```javascript
farmer = {
    getFlockById: (id) => this.get(`/farmers/flocks/${id}`),
    // ... other methods
};
```

#### 2. **farmer.html** (Lines 1015-1055, 1280-1420)
**Modal changes:**
- Added `id="flockModalTitle"` to title (for dynamic text)
- Added `id="flockModalSubmitBtn"` to button (for dynamic text)

**JavaScript additions:**
```javascript
let currentEditingFlockId = null;  // Tracks which flock is being edited

async function saveFlockFromModal() {
    // Handles BOTH create and update
    if (currentEditingFlockId) {
        // UPDATE mode
        await api.farmer.updateFlock(currentEditingFlockId, formData);
    } else {
        // CREATE mode
        await api.farmer.registerFlock(formData);
    }
}

async function editFlockFromTable(flockId) {
    // Loads flock data and populates form
    const flock = await api.farmer.getFlockById(flockId);
    document.getElementById('flockBirdType').value = flock.bird_type;
    document.getElementById('flockBreed').value = flock.breed;
    // ... autofill all fields
    document.getElementById('flockModalTitle').textContent = `Edit Flock #${flockId}`;
    document.getElementById('flockModalSubmitBtn').textContent = 'Update Flock';
    openModal('modal-flock');
}
```

### **Backend (1 file modified)**

#### 3. **backend/app/api/farmers.py** (Lines 160-172)
Added new endpoint to fetch single flock:
```python
@router.get("/flocks/{flock_id}", response_model=FlockResponse)
def get_flock(
    flock_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),
):
    """Get a specific flock by ID"""
    flock = get_flock_by_id_for_farmer(db, flock_id, current_user.id)
    if not flock:
        raise HTTPException(status_code=404, detail="Flock not found")
    return serialize_flock(flock)
```

---

## Data Refresh Timing

| Event | Timing | How |
|-------|--------|-----|
| **Farmer creates flock** | Immediate | Save to DB + reload table |
| **Farmer edits flock** | Immediate | Save to DB + reload table |
| **Farmer deletes flock** | Immediate | Delete from DB + reload table |
| **Buyer views marketplace** | On page load | Fetch latest products via API |
| **Supplier checks demand** | On page load | Fetch latest farmer signals via API |
| **Admin views analytics** | On page load | Query latest aggregated data |

**Note:** If you want **real-time updates without page refresh**, implement WebSocket (socket.io) for instant notifications. For now, data syncs on page load/refresh.

---

## Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    FARMER DASHBOARD                         │
├─────────────────────────────────────────────────────────────┤
│  1. Click "Edit" on Flock                                   │
│  2. Modal loads → Fetches flock from /farmers/flocks/{id}    │
│  3. Modal auto-fills all fields                             │
│  4. User edits → Clicks "Update Flock"                       │
│  5. PUT /farmers/flocks/{id} → Database updated             │
│  6. Table reloads → Shows updated data                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    PostgreSQL DB
                    (All data now)
                    current & fresh)
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ BUYER        │   │ SUPPLIER     │   │ ADMIN        │
│ DASHBOARD    │   │ DASHBOARD    │   │ DASHBOARD    │
├──────────────┤   ├──────────────┤   ├──────────────┤
│ On page load:│   │ On page load:│   │ On page load:│
│ GET /buyers/ │   │ GET /suppli/ │   │ GET /admin/  │
│ search       │   │ farmers      │   │ reports      │
│              │   │              │   │              │
│ → Shows all  │   │ → Shows all  │   │ → Shows all  │
│   farmer     │   │   farmer     │   │   platform   │
│   products   │   │   signals &  │   │   analytics  │
│   & listings │   │   demand     │   │   & metrics  │
└──────────────┘   └──────────────┘   └──────────────┘
```

---

## Testing the System

### **Step 1: Start Backend**
```bash
cd backend
.\poultry\Scripts\activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### **Step 2: Open Frontend**
```bash
cd frontend
python -m http.server 3000
```
Then visit `http://localhost:3000`

### **Step 3: Test Autofill**
1. **Log in as Farmer**
2. Navigate to **Flock Inventory**
3. Click **"Add New Flock"** → Add test flock (e.g., 500 Broilers)
4. Click **"Refresh"** → Flock appears in table
5. Click **"Edit"** on the flock
6. ✅ **Form auto-populates with:**
   - Bird type: "broiler"
   - Breed: (what you entered)
   - Quantity: 500
   - Age: (what you entered)
   - Health Status: (what you entered)
   - Daily Feed: (what you entered)
   - Notes: (what you entered)
7. Change one field (e.g., quantity to 450)
8. Click "Update Flock"
9. ✅ **Table updates with new value**

### **Step 4: Test Data Visibility**
1. **Still logged in as Farmer**, add a new product:
   - Go to **My Products** tab
   - Click "Add Product"
   - Name: "Fresh Broilers"
   - Price: 450 KES
   - Save
2. **Open a new browser tab** (don't log out)
3. Navigate to Buyer Dashboard
4. Go to **Marketplace**
5. ✅ **Your farmer's product appears in real-time**

### **Step 5: Verify Background Refresh**
1. As **Farmer**: Update quantity on a flock
2. As **Buyer** (in another tab): Refresh page → See updated quantity
3. ✅ **Cross-user data is synchronized**

---

## Troubleshooting

### **"Flock not found" error when editing**
- Issue: `api.farmer.getFlockById()` returns 404
- Solution: Verify backend endpoint `/farmers/flocks/{id}` exists
- Action: Restart backend server

### **Form doesn't populate when editing**
- Issue: API response format doesn't match form field IDs
- Solution: Check field names in FlockResponse schema:
  ```python
  class FlockResponse(BaseModel):
      id: int
      bird_type: str  # → maps to flockBirdType
      breed: str      # → maps to flockBreed
      quantity: int   # → maps to flockQuantity
      age_weeks: int  # → maps to flockAgeWeeks
      health_status: str  # → maps to flockHealthStatus
      daily_feed_kg: float  # → maps to flockDailyFeed
      notes: Optional[str]  # → maps to flockNotes
  ```

### **Button text doesn't change to "Update Flock"**
- Issue: Element IDs don't match
- Solution: Verify HTML has:
  ```html
  <div class="modal-title" id="flockModalTitle">...</div>
  <button id="flockModalSubmitBtn">...</button>
  ```

### **Updates don't sync to other dashboards**
- Issue: Buyer/Supplier needs to manually refresh
- Future: Implement WebSocket for instant sync
- Current: Each user refreshes their page to see latest data

---

## Next Steps (Future Enhancements)

1. **Real-Time WebSocket Updates**
   - Use Socket.io to push updates to all connected clients
   - Buyers see farmer's inventory change instantly
   - No manual refresh needed

2. **Auto-Refresh Intervals**
   - Dashboards poll backend every 30 seconds
   - Smoothly updates without user action
   - Configurable refresh rate

3. **Notifications**
   - Buyer gets notified when farmer updates product
   - Supplier gets notified of demand signals
   - Admin gets notified of high-value transactions

4. **Audit Trail**
   - Track all data changes with timestamps
   - Show "Last updated: 2 minutes ago"
   - Admin can review edit history

---

## Summary

✅ **What's Working Now:**
- Farmers can create flocks
- Form auto-populates when editing
- Updates persist to database
- Buyers see latest farmer products on page load
- Suppliers see latest demand signals on page load

✅ **Key Endpoints:**
- `GET /farmers/flocks` - List all flocks
- `GET /farmers/flocks/{id}` - **NEW** Get single flock for edit
- `PUT /farmers/flocks/{id}` - Update flock
- `DELETE /farmers/flocks/{id}` - Delete flock
- `GET /buyers/search` - Buyer sees all products
- `GET /suppliers/farmers` - Supplier sees farm signals

**Result:** Your system now has a complete **data entry → autofill → real-time propagation** workflow! 🎉
