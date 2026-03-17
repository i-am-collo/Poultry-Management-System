/* ════════════════════════════════════════
   POULTRY HUB - ONBOARDING JS
════════════════════════════════════════ */

/* API CONFIGURATION */
const API_BASE_URL = 'http://127.0.0.1:8001';

/* GLOBAL STATE */
let activeRole = null;
let flockEntries = [], flockCount = 0;
let prodEntries = [], prodCount = 0;

const roleThemes = {
    farmer: { 50: 'var(--g50)', 100: 'var(--g100)', 200: 'var(--g200)', 300: 'var(--g300)', 400: 'var(--g400)', 500: 'var(--g500)', 600: 'var(--g600)', 700: 'var(--g700)', 800: 'var(--g800)', 900: 'var(--g900)', label: 'Farmer 🌱' },
    supplier: { 50: 'var(--a50)', 100: 'var(--a100)', 200: 'var(--a200)', 300: '#fcd34d', 400: 'var(--a400)', 500: '#f59e0b', 600: 'var(--a600)', 700: 'var(--a700)', 800: 'var(--a800)', 900: '#78350f', label: 'Supplier 🏪' },
    buyer: { 50: 'var(--b50)', 100: 'var(--b100)', 200: 'var(--b200)', 300: '#93c5fd', 400: 'var(--b400)', 500: '#3b82f6', 600: 'var(--b600)', 700: 'var(--b700)', 800: 'var(--b800)', 900: '#1e3a8a', label: 'Buyer 🛒' },
};

const birdIcons = { broiler: '🍗', layer: '🥚', chick: '🐣', kienyeji: '🐓', turkey: '🦃' };
const catIcons = { feed: '🌾', medicines: '💊', vaccines: '💉', equipment: '🔧', lighting: '💡', housing: '🏠', packaging: '📦', other: '📦' };

/* ROLE SELECTION */
function selectRole(role) {
    activeRole = role;
    document.querySelectorAll('.role-card').forEach(c => c.classList.remove('selected'));
    document.getElementById('rc-' + role).classList.add('selected');

    const t = roleThemes[role];
    const root = document.documentElement;
    Object.entries(t).forEach(([k, v]) => {
        if (k !== 'label') root.style.setProperty('--role-' + k, v);
    });

    document.getElementById('startBtn').classList.add('ready');
    document.getElementById('topRoleLbl').textContent = t.label;
    document.getElementById('topAv').textContent = role[0].toUpperCase();
}

function launchForm() {
    if (!activeRole) return;
    document.getElementById('rolePicker').style.display = 'none';
    const shell = document.getElementById('shell-' + activeRole);
    shell.classList.add('active');
    if (activeRole === 'farmer' && flockEntries.length === 0) addFlock();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function changeRole() {
    document.querySelectorAll('.form-shell').forEach(s => s.classList.remove('active'));
    document.getElementById('rolePicker').style.display = 'block';
    selectRole('farmer');
    document.getElementById('rc-farmer').classList.remove('selected');
    document.getElementById('startBtn').classList.remove('ready');
    document.getElementById('topRoleLbl').textContent = '—';
    document.getElementById('topAv').textContent = '?';
    activeRole = null;
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/* PROGRESS HELPERS */
function setProgress(prefix, n, total) {
    for (let i = 1; i <= total; i++) {
        const el = document.getElementById(prefix + '-si-' + i);
        el.classList.remove('active', 'done');
        if (i < n) el.classList.add('done');
        if (i === n) el.classList.add('active');
        const c = el.querySelector('.si-circle');
        c.innerHTML = i < n
            ? `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>`
            : String(i);
    }
}

let fStep = 1;
function fGoStep(n) {
    document.getElementById('f-step-' + fStep).classList.remove('active');
    fStep = n; document.getElementById('f-step-' + n).classList.add('active');
    setProgress('f', n, 3); scrollTop();
}

let sStep = 1;
function sGoStep(n) {
    document.getElementById('s-step-' + sStep).classList.remove('active');
    sStep = n; document.getElementById('s-step-' + n).classList.add('active');
    setProgress('s', n, 2); scrollTop();
}

let bStep = 1;
function bGoStep(n) {
    document.getElementById('b-step-' + bStep).classList.remove('active');
    bStep = n; document.getElementById('b-step-' + n).classList.add('active');
    setProgress('b', n, 2); scrollTop();
}

function scrollTop() { window.scrollTo({ top: 0, behavior: 'smooth' }); }

/* FLOCK MANAGEMENT */
function addFlock() {
    flockCount++;
    flockEntries.push({ id: flockCount, type: 'broiler', breed: '', qty: '', age: '', status: 'healthy', feed: '' });
    renderFlocks();
}

function removeFlock(id) {
    flockEntries = flockEntries.filter(f => f.id !== id);
    renderFlocks();
}

function updateFlockField(id, field, val) {
    const f = flockEntries.find(e => e.id === id);
    if (f) f[field] = val;
}

function renderFlocks() {
    const list = document.getElementById('f-flock-list');
    if (!flockEntries.length) {
        list.innerHTML = '<div style="text-align:center;padding:24px;color:var(--text2);font-size:13px">No batches yet. Click below to add one.</div>';
        return;
    }
    list.innerHTML = flockEntries.map((f, i) => `
    <div class="fe">
      <div class="fe-head">
        <div class="fe-icon" id="fi-${f.id}">${birdIcons[f.type] || '🐔'}</div>
        <div><div class="fe-num">Batch #${i + 1}</div><div class="fe-sub">Fill in details below</div></div>
        ${flockEntries.length > 1 ? `<button class="rm-btn" onclick="removeFlock(${f.id})">✕ Remove</button>` : ''}
      </div>
      <div class="g3">
        <div class="fg"><label class="fl req">Bird Type</label>
          <select class="fs" onchange="updateFlockField(${f.id},'type',this.value);document.getElementById('fi-${f.id}').textContent=({'broiler':'🍗',layer:'🥚',chick:'🐣',kienyeji:'🐓',turkey:'🦃'})[this.value]||'🐔'">
            <option value="broiler" ${f.type === 'broiler' ? 'selected' : ''}>Broiler</option>
            <option value="layer" ${f.type === 'layer' ? 'selected' : ''}>Layer</option>
            <option value="chick" ${f.type === 'chick' ? 'selected' : ''}>Chick</option>
            <option value="kienyeji" ${f.type === 'kienyeji' ? 'selected' : ''}>Kienyeji</option>
            <option value="turkey" ${f.type === 'turkey' ? 'selected' : ''}>Turkey</option>
          </select>
        </div>
        <div class="fg"><label class="fl req">Breed</label><input class="fi" placeholder="e.g. Ross 308" value="${f.breed}" oninput="updateFlockField(${f.id},'breed',this.value)"></div>
        <div class="fg"><label class="fl req">Qty</label><input class="fi" type="number" placeholder="Birds" value="${f.qty}" oninput="updateFlockField(${f.id},'qty',this.value)"></div>
        <div class="fg"><label class="fl req">Age (wks)</label><input class="fi" type="number" placeholder="Age" value="${f.age}" oninput="updateFlockField(${f.id},'age',this.value)"></div>
        <div class="fg"><label class="fl">Health Status</label>
          <select class="fs" onchange="updateFlockField(${f.id},'status',this.value)">
            <option value="healthy" ${f.status === 'healthy' ? 'selected' : ''}>✅ Healthy</option>
            <option value="monitor" ${f.status === 'monitor' ? 'selected' : ''}>👀 Monitor</option>
            <option value="sick" ${f.status === 'sick' ? 'selected' : ''}>🤒 Sick</option>
            <option value="quarantine" ${f.status === 'quarantine' ? 'selected' : ''}>🚧 Quarantine</option>
          </select>
        </div>
        <div class="fg"><label class="fl">Feed/day (kg)</label><input class="fi" type="number" placeholder="kg" value="${f.feed}" oninput="updateFlockField(${f.id},'feed',this.value)"></div>
      </div>
    </div>`).join('');
}

/* PRODUCT MANAGEMENT */
function addProduct() {
    prodCount++;
    prodEntries.push({ id: prodCount, name: '', category: 'feed', unit: 'kg', price: '', stock: '', desc: '' });
    renderProducts();
}

function removeProduct(id) {
    prodEntries = prodEntries.filter(p => p.id !== id);
    renderProducts();
}

function updateProdField(id, field, val) {
    const p = prodEntries.find(e => e.id === id);
    if (p) p[field] = val;
}

function renderProducts() {
    const list = document.getElementById('s-prod-list');
    if (!prodEntries.length) {
        list.innerHTML = '<div style="text-align:center;padding:24px;color:var(--text2);font-size:13px">No products yet. Add your first listing below.</div>';
        return;
    }
    list.innerHTML = prodEntries.map((p, i) => `
    <div class="pe">
      <div class="pe-head">
        <div class="pe-icon">${catIcons[p.category] || '📦'}</div>
        <div><div class="fe-num">Product #${i + 1}</div><div class="fe-sub">${p.name || 'New product'}</div></div>
        ${prodEntries.length > 1 ? `<button class="rm-btn" onclick="removeProduct(${p.id})">✕ Remove</button>` : ''}
      </div>
      <div class="g2">
        <div class="fg"><label class="fl req">Product Name</label><input class="fi" placeholder="e.g. Broiler Starter 25kg" value="${p.name}" oninput="updateProdField(${p.id},'name',this.value)"></div>
        <div class="fg"><label class="fl req">Category</label>
          <select class="fs" onchange="updateProdField(${p.id},'category',this.value)">
            <option value="feed" ${p.category === 'feed' ? 'selected' : ''}>🌾 Feed</option>
            <option value="medicines" ${p.category === 'medicines' ? 'selected' : ''}>💊 Medicines</option>
            <option value="vaccines" ${p.category === 'vaccines' ? 'selected' : ''}>💉 Vaccines</option>
            <option value="equipment" ${p.category === 'equipment' ? 'selected' : ''}>🔧 Equipment</option>
            <option value="lighting" ${p.category === 'lighting' ? 'selected' : ''}>💡 Lighting</option>
            <option value="housing" ${p.category === 'housing' ? 'selected' : ''}>🏠 Housing</option>
            <option value="other" ${p.category === 'other' ? 'selected' : ''}>📦 Other</option>
          </select>
        </div>
        <div class="fg"><label class="fl req">Unit Price (KES)</label><input class="fi" type="number" placeholder="e.g. 1500" value="${p.price}" oninput="updateProdField(${p.id},'price',this.value)"></div>
        <div class="fg"><label class="fl req">Stock Quantity</label><input class="fi" type="number" placeholder="Available units" value="${p.stock}" oninput="updateProdField(${p.id},'stock',this.value)"></div>
        <div class="fg"><label class="fl">Unit of Measure</label>
          <select class="fs" onchange="updateProdField(${p.id},'unit',this.value)">
            <option value="kg" ${p.unit === 'kg' ? 'selected' : ''}>kg</option>
            <option value="bag" ${p.unit === 'bag' ? 'selected' : ''}>bag</option>
            <option value="piece" ${p.unit === 'piece' ? 'selected' : ''}>piece</option>
            <option value="litre" ${p.unit === 'litre' ? 'selected' : ''}>litre</option>
            <option value="box" ${p.unit === 'box' ? 'selected' : ''}>box</option>
            <option value="unit" ${p.unit === 'unit' ? 'selected' : ''}>unit</option>
          </select>
        </div>
        <div class="fg"><label class="fl">Short Description</label><input class="fi" placeholder="Brief product note…" value="${p.desc}" oninput="updateProdField(${p.id},'desc',this.value)"></div>
      </div>
    </div>`).join('');
}

/* REVIEW BUILDERS */
function buildFarmerReview() {
    const name = v('f-name'), farm = v('f-farm'), county = v('f-county');
    const phone = v('f-phone');
    const flockTags = flockEntries.map(f => `<span class="rev-tag">${birdIcons[f.type] || '🐔'} ${f.qty || '?'} ${f.type} · ${f.age || '?'} wks</span>`).join('') || noneTag();
    document.getElementById('f-rev-body').innerHTML = `
    <div class="rev-sec"><div class="rev-lbl">Farm Information</div>
      <div class="rev-grid">
        <div><div class="rev-k">Full Name</div><div class="rev-v">${name || '—'}</div></div>
        <div><div class="rev-k">Farm Name</div><div class="rev-v">${farm || '—'}</div></div>
        <div><div class="rev-k">County</div><div class="rev-v">${county || '—'}</div></div>
        <div><div class="rev-k">Phone</div><div class="rev-v">${phone || '—'}</div></div>
      </div>
    </div>
    <div class="rev-sec"><div class="rev-lbl">Flock Batches (${flockEntries.length})</div><div>${flockTags}</div></div>`;
}

function buildSupplierReview() {
    const bname = v('s-bname'), cname = v('s-cname'), county = v('s-county'), phone = v('s-phone'), email = v('s-email');
    const cats = chips('chips-scat');
    const till = v('s-till');
    document.getElementById('s-rev-body').innerHTML = `
    <div class="rev-sec"><div class="rev-lbl">Business Information</div>
      <div class="rev-grid">
        <div><div class="rev-k">Business Name</div><div class="rev-v">${bname || '—'}</div></div>
        <div><div class="rev-k">Contact Person</div><div class="rev-v">${cname || '—'}</div></div>
        <div><div class="rev-k">County</div><div class="rev-v">${county || '—'}</div></div>
        <div><div class="rev-k">Phone</div><div class="rev-v">${phone || '—'}</div></div>
        <div><div class="rev-k">Email</div><div class="rev-v">${email || '—'}</div></div>
        <div><div class="rev-k">Supply Categories</div><div class="rev-v">${cats || '—'}</div></div>
      </div>
    </div>
    <div class="rev-sec"><div class="rev-lbl">Payment Details</div>
      <div class="rev-grid">
        <div><div class="rev-k">M-Pesa Till / Paybill</div><div class="rev-v">${till || '—'}</div></div>
      </div>
    </div>
    <div class="rev-sec" style="border:none;padding:0;margin:0">
      <div class="ibox" style="margin:0"><span class="ibox-ico">📦</span><div class="ibox-txt">You can add and manage your product listings from the <strong>Supplier Dashboard</strong> after setup.</div></div>
    </div>`;
}

function buildBuyerReview() {
    const name = v('b-name'), biz = v('b-biz'), county = v('b-county'), phone = v('b-phone'), email = v('b-email');
    const btype = chips('chips-btype'), pay = v('b-pay');
    document.getElementById('b-rev-body').innerHTML = `
    <div class="rev-sec"><div class="rev-lbl">Buyer Profile</div>
      <div class="rev-grid">
        <div><div class="rev-k">Full Name</div><div class="rev-v">${name || '—'}</div></div>
        <div><div class="rev-k">Business/Org</div><div class="rev-v">${biz || '—'}</div></div>
        <div><div class="rev-k">County</div><div class="rev-v">${county || '—'}</div></div>
        <div><div class="rev-k">Phone</div><div class="rev-v">${phone || '—'}</div></div>
        <div><div class="rev-k">Email</div><div class="rev-v">${email || '—'}</div></div>
        <div><div class="rev-k">Buyer Type</div><div class="rev-v">${btype || '—'}</div></div>
        <div><div class="rev-k">Preferred Payment</div><div class="rev-v">${pay || '—'}</div></div>
      </div>
    </div>
    <div class="rev-sec" style="border:none;padding:0;margin:0">
      <div class="ibox" style="margin:0"><span class="ibox-ico">🛍️</span><div class="ibox-txt">Explore our <strong>Product Marketplace</strong> to search for and order poultry products from thousands of suppliers across Kenya!</div></div>
    </div>`;
}

/* SUBMIT */
async function submitForm(prefix) {
    const btn = document.getElementById(prefix + '-submit');
    btn.disabled = true;
    btn.textContent = '⏳ Saving…';

    try {
        let endpoint, payload;

        if (prefix === 'f') {
            endpoint = '/farmers/register';
            payload = {
                full_name: v('f-name'),
                farm_name: v('f-farm'),
                county: v('f-county'),
                phone: v('f-phone'),
                flocks: flockEntries.map(f => ({
                    breed: f.breed,
                    quantity: parseInt(f.qty) || 0,
                    age_weeks: parseInt(f.age) || 0,
                    health_status: f.status,
                    feed_per_day_kg: parseFloat(f.feed) || 0
                }))
            };
        } else if (prefix === 's') {
            endpoint = '/suppliers/register';
            payload = {
                business_name: v('s-bname'),
                contact_person: v('s-cname'),
                county: v('s-county'),
                phone: v('s-phone'),
                email: v('s-email'),
                kra_pin: v('s-kra'),
                categories: chips('chips-scat').split(', ').filter(x => x),
                payment_mpesa_till: v('s-till')
            };
        } else if (prefix === 'b') {
            endpoint = '/buyers/register';
            payload = {
                full_name: v('b-name'),
                business_name: v('b-biz'),
                county: v('b-county'),
                phone: v('b-phone'),
                email: v('b-email'),
                buyer_type: chips('chips-btype'),
                preferred_payment: v('b-pay')
            };
        }

        const response = await fetch(API_BASE_URL + endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error('Registration failed: ' + response.status);

        setTimeout(() => {
            document.getElementById(prefix + '-rev-card').style.display = 'none';
            document.getElementById(prefix + '-rev-nf').style.display = 'none';
            document.getElementById(prefix + '-success').classList.add('active');

            const totalSteps = prefix === 's' ? 2 : (prefix === 'b' ? 2 : 3);
            for (let i = 1; i <= totalSteps; i++) {
                const si = document.getElementById(prefix + '-si-' + i);
                si.classList.remove('active');
                si.classList.add('done');
                si.querySelector('.si-circle').innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>`;
            }

            setTimeout(() => {
                const dashboards = {
                    f: '../../../main/farmer_dashboard/farmer.html',
                    s: '../../../main/supplier-dashboard/supplier.html',
                    b: '../../../main/buyer_dashboard/buyer.html'
                };
                window.location.href = dashboards[prefix];
            }, 3000);
        }, 1700);

    } catch (error) {
        btn.disabled = false;
        btn.textContent = '🚀 Complete Setup';
        toast('❌ Error: ' + (error.message || 'Failed to save. Try again.'));
    }
}

/* UTILITIES */
function v(id) { return (document.getElementById(id)?.value || '').trim(); }
function chips(groupId) { return [...document.querySelectorAll('#' + groupId + ' .chip.on')].map(c => c.textContent.trim()).join(', '); }
function noneTag() { return '<span style="font-size:13px;color:var(--text2)">None added</span>'; }
function toggleChip(el) { el.classList.toggle('on'); }

function previewPhoto(input, imgId) {
    if (input.files && input.files[0]) {
        const r = new FileReader();
        r.onload = e => {
            const img = document.getElementById(imgId);
            img.src = e.target.result;
            img.classList.add('show');
        };
        r.readAsDataURL(input.files[0]);
    }
}

function toast(msg) {
    const wrap = document.getElementById('toastWrap');
    const t = document.createElement('div');
    t.className = 'toast';
    t.textContent = msg;
    wrap.appendChild(t);
    setTimeout(() => {
        t.style.opacity = '0';
        t.style.transition = 'opacity .3s';
        setTimeout(() => t.remove(), 300);
    }, 2800);
}

document.addEventListener('keydown', e => {
    if (e.key === 'Escape') changeRole();
});
