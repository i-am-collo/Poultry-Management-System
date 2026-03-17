# **POULTRY MANAGEMENT SYSTEM — COMPREHENSIVE PROJECT ANALYSIS**

## **1. PROJECT STRUCTURE**

```
Poultry Management System/
├── backend/                          # FastAPI REST API server
│   ├── app/
│   │   ├── main.py                  # FastAPI app initialization, route registration, lifespan
│   │   ├── api/                     # REST API route files (separated by domain)
│   │   │   ├── auth.py              # Authentication routes (login, register, password reset, refresh)
│   │   │   ├── farmers.py           # Farmer-specific endpoints (flocks, products, orders, invitations)
│   │   │   ├── suppliers.py         # Supplier-specific endpoints (product catalog, orders, farm management)
│   │   │   ├── buyers.py            # Buyer-specific endpoints (product search, order creation)
│   │   │   └── notifications.py     # Notification management (list, mark read, delete)
│   │   ├── core/
│   │   │   ├── security.py          # Password hashing (bcrypt), JWT token creation/validation
│   │   │   └── deps.py              # FastAPI dependency injection (get_current_user, require_role)
│   │   ├── crud/                    # Database operations (Create, Read, Update, Delete)
│   │   │   ├── user.py              # User CRUD operations
│   │   │   ├── product.py           # Product search, creation, updates
│   │   │   ├── buyer.py             # Buyer profile creation
│   │   │   ├── farm.py              # Farm management
│   │   │   ├── flock.py             # Flock creation & management
│   │   │   ├── supplier.py          # Supplier profile management
│   │   │   ├── farm_invitation.py   # Supplier-farmer invitation management
│   │   │   ├── notification.py      # Notification CRUD
│   │   │   └── order.py             # Order status & item management
│   │   ├── db/
│   │   │   ├── database.py          # SQLAlchemy engine, sessionmaker, declarative base (Base)
│   │   │   └── __init__.py
│   │   ├── models/                  # SQLAlchemy ORM models (database schema)
│   │   │   ├── user.py              # User entity
│   │   │   ├── farms.py             # Farm entity
│   │   │   ├── flock.py             # Flock entity
│   │   │   ├── product.py           # Product entity
│   │   │   ├── order.py             # Order & OrderItem entities
│   │   │   ├── notification.py      # Notification entity
│   │   │   ├── buyer.py             # BuyerProfile entity
│   │   │   ├── supplier.py          # SupplierProfile entity
│   │   │   ├── farm_invitation.py   # FarmInvitation entity
│   │   │   ├── message.py           # Message entity
│   │   │   ├── health_records.py    # HealthRecord entity (vaccine/medication tracking)
│   │   │   ├── payments.py          # Payment entity
│   │   │   └── reviews.py           # Review entity
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   │   ├── auth.py              # LoginRequest, RegisterRequest schemas
│   │   │   ├── product.py           # BuyerProductSearchResponse, ProductCreate
│   │   │   ├── order.py             # OrderCreate, OrderResponse, OrderItemResponse
│   │   │   ├── farm.py              # FarmCreate, FarmResponse
│   │   │   ├── flock.py             # FlockCreate, FlockResponse
│   │   │   ├── farm_invitation.py   # FarmInvitationCreate, FarmInvitationResponse
│   │   │   └── ... (more schemas)
│   │   └── services/
│   │       └── email_services.py    # Email sending (stub, not fully configured)
│   ├── requirements.txt             # Python dependencies (FastAPI, SQLAlchemy, passlib, etc.)
│   ├── Dockerfile                   # Container image definition
│   ├── main.py (in root)            # Entry point (runs app/main.py)
│   └── tests/                       # Unit & integration tests
│
├── frontend/                        # Vanilla JavaScript + HTML frontend
│   ├── api-client.js               # Centralized API wrapper (handles all REST calls + token refresh)
│   ├── index.html                  # Landing page (public)
│   ├── auth/                       # Authentication pages & logic
│   │   ├── auth.js                 # Form handlers for login, register, password reset
│   │   ├── login/login.html        # Login form
│   │   ├── register/register.html  # Registration form
│   │   └── forgot_password/
│   │       ├── forgot_password.html
│   │       └── reset_password.html
│   └── main/                       # Role-specific dashboards
│       ├── farmer_dashboard/
│       │   ├── farmer.html         # Farmer dashboard UI (flocks, products, orders, messages)
│       │   └── farmer.css          # Farmer dashboard styles
│       ├── buyer_dashboard/
│       │   ├── buyer.html          # Buyer dashboard UI (product search, orders, farms, messages)
│       │   └── buyer.css           # Buyer dashboard styles
│       └── supplier-dashboard/
│           ├── supplier.html       # Supplier dashboard UI (catalog, orders, inventory)
│           └── supplier.css        # Supplier dashboard styles
│
├── README.md                        # Project overview
├── ARCHITECTURE.md                  # System architecture diagram
├── QUICK_START.md                  # Setup instructions
└── docker-compose.yml              # Container orchestration (FastAPI + PostgreSQL + nginx)
```

---

## **2. SUBSYSTEMS IDENTIFIED**

### **A. SUPPLIER SUBSYSTEM**
**Purpose:** B2B supplier catalog management and order fulfillment

**Files:**
- Backend: `backend/app/api/suppliers.py`, `backend/app/models/supplier.py`, `backend/app/crud/supplier.py`
- Frontend: `frontend/main/supplier-dashboard/supplier.html`, supplier.css

**Key Features:**
- Product catalog management (add, edit, delete, price/stock updates)
- Order tracking & approval workflow
- Farm network & customer management
- Farm invitations (suppliers invite farmers to their products)

---

### **B. FARM/FARMER SUBSYSTEM**
**Purpose:** Farmer-owned farm and flock management

**Files:**
- Backend: `backend/app/api/farmers.py`, `backend/app/models/farms.py`, `backend/app/models/flock.py`, `backend/app/crud/farm.py`, `backend/app/crud/flock.py`
- Frontend: `frontend/main/farmer_dashboard/farmer.html`, farmer.css

**Key Features:**
- Farm profile creation & management (location, size, description)
- Flock registration (breed, age, purpose, quantity, health status, feed tracking)
- Own product listings (farmers can sell to buyers)
- Order management (view orders on farmer's products)
- Supplier invitations & messaging (connect with suppliers)
- Health record tracking (vaccinations, medications per flock)

---

### **C. BUYER SUBSYSTEM**
**Purpose:** Product discovery, ordering, and purchase management

**Files:**
- Backend: `backend/app/api/buyers.py`, `backend/app/models/buyer.py`, `backend/app/crud/buyer.py`
- Frontend: `frontend/main/buyer_dashboard/buyer.html`, buyer.css

**Key Features:**
- Product search across suppliers & farmers
- Shopping cart & checkout (create orders)
- Order history & status tracking
- Saved farms (bookmarking suppliers)
- Messaging with sellers
- Product reviews & ratings
- Delivery address management

---

## **3. DATABASE MODELS & RELATIONSHIPS**

| Model | File | Primary Fields | Relationships | Purpose |
|-------|------|---|---|---|
| **User** | `user.py` | `id`, `name`, `email`, `phone`, `hashed_password`, `role` (farmer/supplier/buyer/admin), `created_at` | ← orders, farms, notifications | Core identity & auth |
| **Farm** | `farms.py` | `id`, `farmer_id`, `farm_name`, `location`, `size`, `phone`, `description`, `created_at` | farmer_id → User<br>→ flocks | Farmer-owned farm entity |
| **Flock** | `flock.py` | `id`, `farmer_id`, `breed`, `bird_type`, `age_weeks`, `purpose`, `quantity`, `health_status`, `daily_feed_kg`, `start_date`, `created_at` | farmer_id → User<br>→ health_records | Batch of birds on a farm |
| **Product** | `product.py` | `id`, `supplier_id` OR `farmer_id`, `name`, `category`, `description`, `product_image`, `unit_price`, `unit_of_measure`, `stock_quantity`, `is_active`, `visible_to_farmers_only`, `product_source` (supplier/farmer), `created_at` | supplier_id → User<br>farmer_id → User<br>← order_items | Sellable inventory item |
| **Order** | `order.py` | `id`, `user_id` (buyer), `total_amount`, `order_status` (pending/approved/shipped/delivered/cancelled), `payment_status` (pending/completed/failed), `note`, `created_at`, `updated_at` | user_id → User<br>→ items | Purchase transaction |
| **OrderItem** | `order.py` | `id`, `order_id`, `product_id`, `quantity`, `unit_price`, `total_price`, `created_at` | order_id → Order<br>product_id → Product | Line item in order |
| **Notification** | `notification.py` | `id`, `user_id`, `title`, `message`, `type`, `is_read`, `created_at` | user_id → User | System alerts for users |
| **FarmInvitation** | `farm_invitation.py` | `id`, `farmer_id`, `supplier_id`, `farm_name`, `status` (pending/accepted/declined), `created_at` | farmer_id → User<br>supplier_id → User | Supplier → Farmer connection request |
| **Message** | `message.py` | `id`, `sender_id`, `receiver_id`, `content`, `is_read`, `created_at` | sender_id → User<br>receiver_id → User | Direct user-to-user messages |
| **SupplierProfile** | `supplier.py` | `id`, `supplier_id`, `business_name`, `county`, `phone`, `kra_pin`, `categories` (JSON), `payment_mpesa_till`, `created_at` | supplier_id → User | Supplier business details |
| **BuyerProfile** | `buyer.py` | `id`, `buyer_id`, `full_name`, `business_name`, `county`, `buyer_type`, `preferred_payment`, `created_at` | buyer_id → User | Buyer business details |
| **Payment** | `payments.py` | `id`, `order_id`, `amount`, `transaction_reference`, `payment_method`, `payment_status`, `created_at` | order_id → Order | Payment record per order |
| **HealthRecord** | `health_records.py` | `id`, `flock_id`, `vaccination_type`, `medication`, `date_administered`, `next_due_date`, `notes`, `created_at` | flock_id → Flock | Vaccine/health tracking |
| **Review** | `reviews.py` | `id`, `reviewer_id`, `reviewee_id`, `rating` (1-5), `comment`, `created_at` | reviewer_id → User<br>reviewee_id → User | User ratings & feedback |

**Key Relationship Rules:**
- **Products**: Every product has EITHER `supplier_id` OR `farmer_id` (not both; indicated by `product_source` field)
- **Orders**: Users (buyers) create orders; each order contains 1+ OrderItems pointing to Products
- **Flocks**: Owned by farmers; health records and production data linked to flocks
- **Invitations**: Suppliers invite specific farms; can be accepted/declined to establish connection

---

## **4. API ENDPOINTS**

### **A. AUTHENTICATION** (`/auth/*`)
**Router:** `backend/app/api/auth.py`

| Method | Endpoint | Purpose | Auth | Returns |
|--------|----------|---------|------|---------|
| POST | `/auth/register` | Register new user (farmer/supplier/buyer) | None | `{token, user, role}` |
| POST | `/auth/login` | Login with email/password | None | `{access_token, refresh_token, user}` |
| POST | `/auth/forgot-password` | Request password reset email | None | `{message: "Reset link sent"}` |
| POST | `/auth/reset-password` | Validate reset token & update password | Token (reset type) | `{message: "Password reset"}` |
| POST | `/auth/refresh` | Refresh expired access token | Refresh token | `{access_token, refresh_token, user}` |

---

### **B. FARMERS** (`/farmers/*`)
**Router:** `backend/app/api/farmers.py`
**Auth Required:** Yes (role: `farmer`)

**Flock Management:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/farmers/flocks` | List all flocks for current farmer |
| GET | `/farmers/flocks/{flock_id}` | Get single flock details |
| POST | `/farmers/register-flock` | Create new flock |
| PUT | `/farmers/flocks/{flock_id}` | Update flock (breed, age, quantity, health status, feed) |
| DELETE | `/farmers/flocks/{flock_id}` | Delete flock |

**Farm Profile:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/farmers/farm-profile` | Get farmer's farm details |
| POST | `/farmers/farm-profile` | Create farm profile |
| PUT | `/farmers/farm-profile` | Update farm profile |

**Products (Farmer-Sourced):**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/farmers/products` | Add product for sale |
| GET | `/farmers/products` | List farmer's products |
| PUT | `/farmers/products/{product_id}` | Update product (price, stock, etc.) |
| DELETE | `/farmers/products/{product_id}` | Remove product |

**Orders:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/farmers/orders` | Get all orders with farmer's products |
| PUT | `/farmers/orders/{order_id}/dispatch` | Mark order as shipped |

**Relationships & Invitations:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/farmers/all-suppliers` | List all registered suppliers |
| POST | `/farmers/suppliers/{supplier_id}/request-connection` | Request to work with supplier |
| GET | `/farmers/invitations/pending` | Get pending supplier invitations |
| PUT | `/farmers/invitations/{id}/accept` | Accept supplier invitation |
| PUT | `/farmers/invitations/{id}/decline` | Decline supplier invitation |
| GET | `/farmers/suppliers/connected` | List connected (accepted) suppliers |

**Messaging:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/farmers/messages/{supplier_id}` | Get message history with supplier |
| POST | `/farmers/messages/{supplier_id}` | Send message to supplier |

---

### **C. SUPPLIERS** (`/suppliers/*`)
**Router:** `backend/app/api/suppliers.py`
**Auth Required:** Yes (role: `supplier`)

**Product Management:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/suppliers/products` | Add product to catalog |
| GET | `/suppliers/products` | List supplier's products |
| PUT | `/suppliers/products/{product_id}` | Update product (stock, price, etc.) |
| DELETE | `/suppliers/products/{product_id}` | Remove product |

**Order Management:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/suppliers/orders` | Get orders containing supplier's products |
| PUT | `/suppliers/orders/{order_id}/approve` | Approve order |
| PATCH | `/suppliers/orders/{order_id}` | Update order status |

**Farm & Customer Network:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/suppliers/invite-farm` | Send invitation to farm |
| GET | `/suppliers/all-farms` | List all farms |
| GET | `/suppliers/customers` | List farmers who ordered from supplier |

**Profile:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/suppliers/register` | Complete supplier onboarding |
| GET | `/suppliers/profile` | Get supplier business profile |

---

### **D. BUYERS** (`/buyers/*`)
**Router:** `backend/app/api/buyers.py`
**Auth Required:** Yes (role: `buyer` or `farmer`)

**Product Search:**

| Method | Endpoint | Purpose | Query Params |
|--------|----------|---------|---|
| GET | `/buyers/search` | Search products across suppliers & farmers | `q` (search term, min 1 char) |

**Order Management:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/buyers/orders` | Create new order with items |
| GET | `/buyers/orders` | List buyer's orders (ordered by creation desc) |
| GET | `/buyers/orders/{order_id}` | Get single order details |

**Profile:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/buyers/register` | Complete buyer onboarding |
| GET | `/buyers/profile` | Get buyer profile & order history |

---

### **E. NOTIFICATIONS** (`/notifications/*`)
**Router:** `backend/app/api/notifications.py`
**Auth Required:** Yes

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/notifications/` | List all notifications for current user |
| GET | `/notifications/{notification_id}` | Get single notification |
| PUT | `/notifications/{notification_id}` | Mark notification as read/unread |
| PUT | `/notifications/mark-all-read` | Mark all notifications as read |
| DELETE | `/notifications/{notification_id}` | Delete single notification |
| DELETE | `/notifications/` | Delete all notifications |

---

### **F. HEALTH CHECK**
| Method | Endpoint | Returns |
|--------|----------|---------|
| GET | `/health` | `{status: "ok", message: "API is running"}` |

---

## **5. BUYER SUBSYSTEM (DETAILED)**

### **A. Buyer Dashboard Files**

**Frontend:**
- **HTML:** `frontend/main/buyer_dashboard/buyer.html` (490+ lines)
- **CSS:** `frontend/main/buyer_dashboard/buyer.css`
- **API Client:** `frontend/api-client.js` (buyer methods only)

**Backend:**
- **Routes:** `backend/app/api/buyers.py`
- **CRUD:** `backend/app/crud/buyer.py`
- **Model:** `backend/app/models/buyer.py`
- **Schemas:** `backend/app/schemas/order.py`, `backend/app/schemas/product.py`

---

### **B. Current Buyer Dashboard Functionality**

**Navigation Sections:**
1. **Main**
   - Dashboard — Overview metrics, active orders, saved farms, purchase history
   - Poultry Products — Search & browse products from suppliers/farmers with filters
   - My Orders — View order tracking table with status
   - Farms — View/manage saved farms

2. **Communication**
   - Messages — Chat with sellers (placeholder/stub; no endpoints currently wired)
   - Reviews — Rate suppliers/farmers (placeholder/stub)

3. **Account**
   - Settings — Profile, delivery address, notification preferences (toggles), password reset, 2FA
   - Logout

**Dashboard Sections:**
1. **Overview Metrics** (loads dynamically)
   - Total orders, total spent, order status summary

2. **Active Orders** (loads via API)
   - Quick view of pending/approved orders with link to full orders page

3. **My Farms** (loads via API)
   - Cards for saved farms (suppliers bookmarked)
   - Quick links to browse their products

4. **Purchase History** (loads via API)
   - Table of recent orders with export CSV option

5. **Products** (Live API Search)
   - Search bar for product queries
   - Filter chips: All, Eggs, Chicks, Broilers, Feed, Vaccines
   - Filter dropdowns: Farm, Price Range, Availability
   - Live table display with columns: ID, Product, Source, Category, Price, Stock, Qty, Action
   - Add to cart button per product

6. **Orders** (Live API)
   - Table view: Order ID, Product, Qty, Unit, Total, Status, Created Date
   - Refresh capability

7. **Shopping Cart** (Modal)
   - List cart items
   - Delivery method selection (Delivery +KES 850 vs. Pickup Free)
   - Cost breakdown: Subtotal, Transport, VAT (16%), Total
   - Checkout button

---

### **C. Current API Endpoints Called by Buyer Dashboard**

```javascript
// Search products
GET /buyers/search?q={searchTerm}
Response: [{ id, supplier_id, supplier_name, farmer_id, farmer_name, 
            product_source, name, category, description, product_image, 
            unit_price, unit_of_measure, stock_quantity, visible_to_farmers_only }]

// Create order
POST /buyers/orders
Body: { items: [{ product_id, quantity }], note }
Response: { id, user_id, buyer_email, buyer_farm_name, total_amount, 
            order_status, payment_status, items: [...], note, created_at, updated_at }

// List orders
GET /buyers/orders
Response: [{ ...OrderResponse }]

// Get single order
GET /buyers/orders/{order_id}
Response: { ...OrderResponse }

// Get buyer profile
GET /buyers/profile
Response: { buyer_id, email, phone, orders_count, total_spent, recent_orders: [...] }
```

---

### **D. Frontend API Methods (api-client.js)**

```javascript
const api = new APIClient();

// Buyer-specific methods
api.buyer = {
    getAllProducts: () => this.get('/buyers/search'),
    searchProducts: (query) => this.get(`/buyers/search?q=${query}`),
    createOrder: (data) => this.post('/buyers/orders', data),
    getOrders: () => this.get('/buyers/orders'),
    getOrder: (id) => this.get(`/buyers/orders/${id}`),
};

// Called from buyer.html as:
await api.buyer.searchProducts('eggs');
await api.buyer.createOrder({ items: [{product_id: 5, quantity: 10}], note: "..." });
await api.buyer.getOrders();
```

---

### **E. Data Currently Displayed in Buyer Dashboard**

**From API:**
- Product list (name, price, stock, source, category, supplier/farmer name)
- Order history (order ID, items, status, total, dates)
- Buyer profile (name, email, phone, order count, total spent)

**Hardcoded/Placeholder:**
- Overview metrics (KPIs calculated but may be static values)
- Farm list (Kiambu Fresh Farms, Valley Poultry Farm, Agro-Feeds Ltd, Sunrise Hatchery are shown in dropdowns)
- Settings (profile, delivery address, notification toggles are form fields but not fully wired)
- Messages & Reviews (UI exists but endpoints not fully integrated)

---

## **6. AUTHENTICATION IMPLEMENTATION**

### **A. JWT Token Strategy**

**Library:** `python-jose` with `HS256` algorithm
**Secret Key:** Environment variable `SECRET_KEY` (dev fallback: `"dev-insecure-secret-change-me"`)

**Token Types:**

| Token Type | Payload | Expiry | Purpose |
|------------|---------|--------|---------|
| **Access Token** | `{sub: email, role: role, type: "access"}` | 15 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` env) | Authorization header for API calls |
| **Refresh Token** | `{sub: email, type: "refresh"}` | 7 days (configurable via `REFRESH_TOKEN_EXPIRE_DAYS` env) | Obtain new access token without re-login |
| **Reset Token** | `{sub: email, type: "reset"}` | 60 minutes (configurable via `RESET_TOKEN_EXPIRE_MINUTES` env) | Password reset validation |

**Functions:** (`backend/app/core/security.py`)
```python
create_access_token(email, role) → JWT string
create_refresh_token(email) → JWT string
create_reset_token(email) → JWT string
decode_token(token) → dict with payload
verify_password(plain, hashed) → bool
hash_password(password) → bcrypt hash
```

---

### **B. FastAPI Dependency Injection** (`backend/app/core/deps.py`)

**`get_current_user(token: str = Depends(HTTPBearer())) → User`**
- Extracts Bearer token from `Authorization` header
- Decodes JWT; validates expiry & type ("access")
- Queries database for User by email in token
- Raises `401 HTTPException` if missing/invalid/expired
- **Used in:** All protected routes

**`require_role(*allowed_roles) → Callable`**
- Returns a dependency that wraps `get_current_user()`
- Checks if `user.role` is in `allowed_roles`
- Raises `403 HTTPException` if role mismatch
- **Used in:** Role-specific routes (e.g., `@router.post("/register-flock", ..., require_role("farmer"))`)

**Decorator Pattern:**
```python
@router.post("/register-flock")
def register_flock(
    payload: FlockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("farmer")),  # ← Role check
):
    # Only accessible to farmers
    ...
```

---

### **C. Protected Routes by Role**

| Role | Protected Endpoints |
|------|---|
| **farmer** | `/farmers/*` (flocks, farm profile, products, orders, invitations) |
| **supplier** | `/suppliers/*` (products, orders, farms, invitations) |
| **buyer** | `/buyers/*` (search, orders, profile) |
| **farmer or buyer** | `/buyers/search`, `/buyers/orders` (farmers can also buy) |
| **any (authenticated)** | `/notifications/*` (all authenticated users) |

---

### **D. Frontend Storage & Auto-Refresh** (`frontend/api-client.js`)

**Token Storage:**
```javascript
localStorage.setItem('accessToken', token);
localStorage.setItem('refreshToken', refreshToken);
localStorage.setItem('user', JSON.stringify(user));
localStorage.setItem('userRole', user.role);
```

**Auto-Refresh Logic:**
- Before each request, client injects: `Authorization: Bearer ${accessToken}`
- On `401` response (token expired), calls `GET /auth/refresh` with refresh token
- Backend returns new tokens; frontend updates localStorage
- Retries original request with new token
- On refresh failure (no valid refresh token), clears auth & redirects to login

**Flow:**
```
User API Call
  ↓ (Has access token? Yes)
Add Authorization header
  ↓ (Send request)
Server responds 401?
  ↓ (Yes)
Call /auth/refresh with refresh token
  ↓ (Refresh successful?)
Update localStorage with new tokens
  ↓ (Yes)
Retry original request
  ↓
Success or fail
 ↓
Return response
    ↓ (Refresh failed)
    Clear auth, redirect to login
```

---

## **7. FRONTEND CONVENTIONS**

### **A. CSS Organization**

**Approach:** **Per-page CSS files** (not global; each dashboard has its own stylesheet)

**Files:**
- `frontend/main/farmer_dashboard/farmer.css`
- `frontend/main/buyer_dashboard/buyer.css`
- `frontend/main/supplier-dashboard/supplier.css`

**CSS Variable System:** (`buyer.css` example)
```css
:root {
    /* Color palette */
    --green-deep: #1a3a2a;       /* Primary dark */
    --green-mid: #2d6a4f;
    --green-bright: #40916c;
    --green-light: #74c69d;       /* Highlights */
    --green-pale: #d8f3dc;        /* Light accents */
    --green-ghost: #f0faf3;       /* Very light bg */
    
    --amber: #e9a224;             /* Secondary/warnings */
    --amber-pale: #fef3d0;
    --red-soft: #e05c5c;          /* Errors/dangers */
    --red-pale: #fde8e8;
    
    /* Typography */
    --text-dark: #1c2b22;
    --text-mid: #3d5247;
    --text-light: #6b8a77;
    --text-muted: #a0b4a8;
    
    /* Spacing & shadows */
    --radius: 12px;
    --radius-sm: 8px;
    --shadow-md: 0 4px 16px rgba(26, 58, 42, 0.10);
    --shadow-lg: 0 8px 32px rgba(26, 58, 42, 0.14);
    
    /* Layout */
    --sidebar-width: 220px;
    --card: 166px;  /* Card width */
}
```

**Typography:**
- **Font:** DM Sans (400, 500, 600 weights) + DM Serif Display (serif accents)
- **Loaded via:** Google Fonts CDN in HTML head

**Layout System:**
- **Sidebar Navigation:** Fixed left (220px width), dark green background
- **Main Content:** Flex layout with header + scrollable content area
- **Grid System:** CSS Grid for card layouts (`.card-grid`, `.sq` = card)
- **Tables:** Standard HTML with inline styles for marketplace listings

**Component Classes:**
- `.sidebar` — Left navigation
- `.nav-item`, `.nav-item.active` — Navigation items
- `.topbar` — Header bar with search & user menu
- `.sq`, `.card-grid` — Card containers
- `.modal-overlay`, `.modal` — Modal dialogs (cart)
- `.btn-sm`, `.btn-primary` — Button styles
- `.toggle`, `.toggle.on/.off` — Toggle switches

---

### **B. JavaScript Communication with Backend**

**HTTP Client:** `frontend/api-client.js`

**Pattern: Fetch via APIClient**
```javascript
// Global instance created automatically
const api = new APIClient();

// Usage examples:
try {
    const products = await api.buyer.searchProducts('eggs');
    console.log(products);
} catch (error) {
    console.error(error.message);
    // Error handling (includes network, 4xx, 5xx)
}

// All HTTP verbs supported:
api.get(endpoint, options)
api.post(endpoint, body, options)
api.put(endpoint, body, options)
api.delete(endpoint, options)
api.patch(endpoint, body, options)
```

**Request Flow:**
1. `api.buyer.searchProducts(query)` → calls `api.get('/buyers/search?q=' + query)`
2. APIClient adds `Authorization: Bearer ${token}` header
3. Sends request to `http://127.0.0.1:8001/buyers/search?q=...`
4. Handles `401` with token refresh (auto-retry)
5. Returns parsed JSON or throws error

**Error Handling:**
```javascript
catch (error) {
    if (error.status === 400) { /* Form validation error */ }
    else if (error.status === 401) { /* Auth failure */ }
    else if (error.status === 403) { /* Permission denied */ }
    else if (error.status === 404) { /* Not found */ }
    else if (error.status === 500) { /* Server error */ }
    error.message // User-friendly error text
}
```

---

### **C. Shared Components & Layouts**

**Shared across all dashboards:**
- **Sidebar navigation** (different nav items per role, same structure)
- **Topbar header** (search, notifications, cart/user menu positioned consistently)
- **Modal system** (overlays & dialogs for forms, carts, details)
- **Toast notifications** (`showToast()` function for alerts)
- **Authentication** (all rely on `frontend/auth/auth.js` for login/register)

**Role-Specific:**
- **Farmer:** Flock (bird batch) management UI, farm profile form
- **Supplier:** Product catalog form, farm invite list
- **Buyer:** Product search filters, shopping cart, order tracking tables

**No Shared CSS File:**
Each dashboard redefines colors, spacing, and components (DRY violation but allows role-specific styling)

---

## **8. GAPS & OBSERVATIONS**

### **A. Missing from Buyer Marketplace**

| Feature | Current State | Gap |
|---------|---|---|
| **Product Filters** | UI present (chips, dropdowns) | Not wired to API; filters don't actually refine results |
| **Cart Management** | UI present (modal, cost breakdown) | No backend endpoints for saving carts; checkout flow not implemented |
| **Checkout & Payment** | Modal with delivery options, "Proceed to Checkout" button | No payment processing endpoint; payment status always "pending" |
| **Farm/Supplier Details** | "Saved Farms" page exists | No endpoint to view farm details or supplier profiles; just placeholders |
| **Product Reviews** | Reviews page exists | No backend endpoints; no ability to submit/view reviews |
| **Messaging** | Messages page exists | No wired endpoints; message UI is stub |
| **Order Status Updates** | Orders table shows status | No real-time updates; no webhook/polling for order changes |
| **Wishlist/Favorites** | Not implemented | No UI to save favorite products |
| **Bulk Ordering** | UI supports qty field per product | No bulk discount logic or estimate functionality |
| **Delivery Tracking** | Not implemented | No tracking endpoints or GPS integration |
| **Invoice Generation** | Not implemented | No PDF/print order invoices |

---

### **B. Existing Product Listing & Order Endpoints**

**Product Endpoints:**
- ✅ `GET /buyers/search?q={term}` — Search products (all active products across suppliers & farmers)
- ✅ `POST /buyers/orders` — Create order with items
- ✅ `GET /buyers/orders` — List buyer's orders
- ✅ `GET /buyers/orders/{order_id}` — Get order details

**Missing Endpoints:**
- ❌ `GET /buyers/products/{product_id}` — Get single product details (description, images, reviews)
- ❌ `GET /buyers/farms/{farm_id}` — Get farm profile & details
- ❌ `GET /buyers/suppliers/{supplier_id}` — Get supplier profile & contact info
- ❌ `POST /buyers/orders/{order_id}/cancel` — Cancel order
- ❌ `PUT /buyers/orders/{order_id}` — Modify order (change qty, add/remove items)
- ❌ `GET /buyers/cart` — Retrieve saved cart
- ❌ `POST /buyers/cart/items` — Add item to cart
- ❌ `DELETE /buyers/cart/items/{item_id}` — Remove from cart
- ❌ `POST /buyers/reviews` — Submit product review
- ❌ `GET /reviews?product_id={id}` — Get product reviews

---

### **C. Backend Implementation Status**

**Core Functionality (✅ Implemented):**
- Authentication (register, login, token refresh, password reset)
- Flock management (CRUD operations)
- Product catalog (suppliers & farmers can add/edit/delete)
- Order creation & tracking
- Notifications system
- Farm invitations (supplier ↔ farmer connections)

**Partially Implemented (`⚠️ Stub/Incomplete`):**
- Email notifications (`backend/app/services/email_services.py` — no SMTP configured)
- Role-based ordering (farmers can be buyers, logic in place)
- Order approval workflow (suppliers can approve, but no status propagation logic)

**Not Yet Implemented (`❌`):**
- Payment processing (Payment model exists, no integration)
- Reviews & ratings (Review model exists, no CRUD endpoints)
- Messaging (Message model exists, routes/CRUD incomplete)
- Cart save/retrieve (frontend only, no backend)
- Wishlist/favorites
- Advanced search filters (category, price range, availability)
- Real-time notifications (WebSocket or polling)
- Health records reporting
- Delivery tracking

---

### **D. Database Observations**

**Schema Strengths:**
- Normalized relationships (no data duplication)
- Flexible product model (supplier OR farmer can list products)
- Enum-based status tracking (order_status, payment_status)
- Timestamps on all entities (audit trail)
- Cascade deletes configured (clean removal)

**Potential Issues:**
- No soft deletes (deleted records lost; consider audit log)
- Limited indexing (id, foreign keys indexed; consider adding compound indexes on (user_id, created_at) for queries)
- JSON fields (Product.visible_to_farmers_only, SupplierProfile.categories stored as JSON — could be separate tables for scalability)

---

### **E. Frontend State Management**

**Current Approach:** Vanilla JS with localStorage
- No framework (React, Vue, etc.)
- State stored in browser localStorage (tokens, user, role)
- No centralized state container
- Page navigation via `showPage()` function (DOM manipulation)
- No form validation framework (custom regex in auth.js)

**Gaps:**
- No error boundary/fallback UI
- Limited form validation (email, phone regex only)
- No loading skeletons (placeholder text "Loading..." used)
- No offline support
- Page data refreshed on every navigation (no caching)

---

## **SUMMARY TABLE**

| Aspect | Implementation | Quality |
|--------|---|---|
| **Architecture** | FastAPI backend + vanilla JS frontend | Clean separation; RESTful |
| **Authentication** | JWT (15-min access, 7-day refresh) | Secure (bcrypt + HS256) |
| **Database** | SQLAlchemy ORM + 13 models | Well-designed, normalized |
| **API Coverage** | 40+ endpoints (auth, farmers, suppliers, buyers, notifications) | Good for MVP |
| **Buyer Dashboard** | Search, orders, farms, messaging (UI scaffolding) | 60% functional (core search/order wired; filters/messaging stubs) |
| **Frontend Patterns** | Centralized API client, per-page CSS, localStorage state | Simple but scalable |
| **Testing** | Unit tests in `/tests/` | Limited coverage; no E2E |
| **Documentation** | README, ARCHITECTURE.md, QUICK_START.md | Good foundation; API docs via Swagger `/docs` |
| **Deployment** | Docker + docker-compose (FastAPI, PostgreSQL, nginx) | Production-ready |

---

## **FILES TO FOCUS ON FIRST**

1. `backend/app/main.py` — Route setup
2. `backend/app/models/` — Data schema (start with user.py, order.py, product.py)
3. `backend/app/api/buyers.py` — Buyer endpoints
4. `frontend/api-client.js` — Frontend-backend bridge
5. `frontend/main/buyer_dashboard/buyer.html` — UI structure

---

This report provides a complete blueprint of the system. Ready to plan your feature! 🚀
