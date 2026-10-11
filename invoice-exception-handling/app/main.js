// ==========================================================================
// InvoiceGuard AI — 3-Way Match Exception Dashboard
// Simulates the full pipeline: extraction → match → duplicate → classify → resolve
// ==========================================================================

// ── SYNTHETIC DATASET ────────────────────────────────────────────────────
// Represents the processed result of 30 sample invoices from the 900-batch
const invoiceExceptions = (() => {
  const SUPPLIERS = [
    'Acme Hardware Components Inc',
    'Global Semiconductor Corp',
    'Precision Fasteners Ltd',
    'Vortex Electronics Corp',
    'CloudHosting Infrastructure LLC'
  ];

  const DEFECT_TEMPLATES = [
    { defect: 'PERFECT_MATCH',            category: 'CLEARED_AUTO_MATCH',            action: 'AUTO_RELEASE_PAYMENT' },
    { defect: 'QUANTITY_MISMATCH',        category: 'QUANTITY_MISMATCH',             action: 'PARTIAL_PAYMENT_SHORT_SHIPMENT' },
    { defect: 'PRICE_DRIFT',              category: 'PRICE_DRIFT',                   action: 'REQUEST_CREDIT_MEMO' },
    { defect: 'TAX_DISCREPANCY',          category: 'TAX_DISCREPANCY',               action: 'ON_HOLD_TAX_REVIEW' },
    { defect: 'MISSING_GOODS_RECEIPT',    category: 'MISSING_GOODS_RECEIPT',         action: 'HOLD_PENDING_WAREHOUSE_GR' },
    { defect: 'TRUE_DUPLICATE',           category: 'TRUE_DUPLICATE_RISK',           action: 'REJECT_INVOICE_DUPLICATE' },
    { defect: 'SUBSCRIPTION_TRAP',        category: 'VALID_SUBSCRIPTION_RECURRING',  action: 'AUTO_RELEASE_PAYMENT' },
    { defect: 'EXTRACTION_NOISE_UNSURE',  category: 'UNSURE_NEEDS_HUMAN_CHECK',      action: 'ESCALATE_TO_SENIOR_AP_ANALYST' }
  ];

  const invoices = [];
  const seed = [0,1,2,3,4,5,6,7,1,0,2,3,4,5,6,7,0,1,2,3,4,5,1,0,3,6,7,4,5,2];

  for (let i = 0; i < 30; i++) {
    const tmpl = DEFECT_TEMPLATES[seed[i]];
    const supplier = SUPPLIERS[i % SUPPLIERS.length];
    const poId = `PO-2026-${String(i + 1).padStart(4, '0')}`;
    const poQty = 100 + i * 5;
    const poPrice = parseFloat((25 + i * 3.5).toFixed(2));
    const poTax = 0.08;
    const grPosted = tmpl.defect !== 'MISSING_GOODS_RECEIPT';
    const grQty   = tmpl.defect === 'QUANTITY_MISMATCH' ? poQty - 20 : poQty;
    const invQty  = tmpl.defect === 'QUANTITY_MISMATCH' ? poQty + 20 : poQty;
    const invPrice = tmpl.defect === 'PRICE_DRIFT' ? parseFloat((poPrice * 1.12).toFixed(2)) : poPrice;
    const expectedTax = parseFloat(((invQty * invPrice) * poTax).toFixed(2));
    const invTax = tmpl.defect === 'TAX_DISCREPANCY' ? parseFloat(((invQty * invPrice) * 0.15).toFixed(2)) : expectedTax;
    const invTotal = parseFloat(((invQty * invPrice) + invTax).toFixed(2));
    const poTotal  = parseFloat(((poQty * poPrice) + (poQty * poPrice * poTax)).toFixed(2));
    const conf = tmpl.defect === 'EXTRACTION_NOISE_UNSURE'
      ? parseFloat((0.42 + ((i * 7) % 15) / 100).toFixed(2))
      : parseFloat((0.92 + ((i * 5) % 7) / 100).toFixed(2));
    const isDuplicate = tmpl.defect === 'TRUE_DUPLICATE';
    const isSubscription = tmpl.defect === 'SUBSCRIPTION_TRAP';

    const qtyDelta = invQty - grQty;
    const priceDelta = parseFloat((invPrice - poPrice).toFixed(2));
    const taxDelta = parseFloat((invTax - expectedTax).toFixed(2));

    invoices.push({
      invoice_id:    `INV-OBJ-${String(i + 1).padStart(4, '0')}`,
      invoice_number: isDuplicate ? `INV-990${String(Math.max(1, i-8)).padStart(4,'0')}` : `INV-990${String(i + 1).padStart(4, '0')}`,
      po_id: poId,
      supplier_name: supplier,
      invoice_date: `2026-09-${String((i % 28) + 1).padStart(2, '0')}`,
      inv_qty, inv_price: invPrice, inv_tax: invTax, inv_total: invTotal,
      po_qty: poQty, po_price: poPrice, po_tax_rate: '8%', po_total: poTotal,
      gr_posted: grPosted, gr_qty: grQty,
      extraction_confidence: conf,
      extraction_status: conf < 0.70 ? 'LOW_CONFIDENCE_OCR_NOISE' : 'HIGH_CONFIDENCE_CLEAN',
      ground_truth_defect: tmpl.defect,
      category: tmpl.category,
      action: tmpl.action,
      confidence: isDuplicate || tmpl.defect === 'PERFECT_MATCH' ? 1.0 : (conf < 0.70 ? conf : 0.95),
      is_abstention: tmpl.defect === 'EXTRACTION_NOISE_UNSURE',
      deltas: { qty_delta: qtyDelta, price_delta: priceDelta, price_drift_pct: parseFloat(((priceDelta / poPrice) * 100).toFixed(2)), tax_delta: taxDelta },
      dup_result: {
        is_risk: isDuplicate,
        type: isDuplicate ? 'EXACT_INVOICE_NUMBER_MATCH' : isSubscription ? 'VALID_SUBSCRIPTION_RECURRING' : 'NO_DUPLICATE_FOUND',
        explanation: isDuplicate
          ? `Exact duplicate invoice number detected. Previously paid on 2026-09-${String(Math.max(1, i - 8)).padStart(2,'0')} for $${invTotal.toFixed(2)}.`
          : isSubscription
          ? `Monthly subscription billing for ${supplier} ($${invTotal.toFixed(2)}). 30-day recurring cycle confirmed.`
          : 'No duplicate pattern detected in payment history.'
      },
      resolution_email: buildEmail(tmpl.defect, supplier, `INV-990${String(i + 1).padStart(4, '0')}`, invTotal, invQty, poQty, invPrice, poPrice, taxDelta),
      checklist: buildChecklist(tmpl.defect)
    });
  }
  return invoices;
})();

function buildEmail(defect, supplier, invNum, total, invQty, poQty, invPrice, poPrice, taxDelta) {
  switch(defect) {
    case 'TRUE_DUPLICATE':
      return `Dear AP Team at ${supplier},\n\nWe received invoice ${invNum} for $${total.toFixed(2)}. Our automated 3-way match audit detected this as a duplicate of a previously processed payment.\n\nThis invoice has been cancelled in our ERP system. Please review your records.\n\nRegards,\nAccounts Payable Operations`;
    case 'PRICE_DRIFT':
      return `Dear ${supplier} Billing,\n\nInvoice ${invNum}: Unit price billed ($${invPrice.toFixed(2)}) exceeds Purchase Order rate ($${poPrice.toFixed(2)}) by ${(((invPrice - poPrice) / poPrice) * 100).toFixed(1)}%.\n\nPlease issue a Credit Memo or resubmit at the agreed PO rate to release payment.\n\nRegards,\nAccounts Payable Team`;
    case 'QUANTITY_MISMATCH':
      return `Dear ${supplier} Billing,\n\nInvoice ${invNum}: We received ${poQty} units but were billed for ${invQty} units.\n\nPayment has been issued for ${poQty} units. Please verify shipment records for the balance of ${invQty - poQty} units.\n\nRegards,\nAccounts Payable Team`;
    case 'MISSING_GOODS_RECEIPT':
      return `Internal Note: Invoice ${invNum} on hold pending Goods Receipt (GR) posting by warehouse team. Vendor notification deferred.`;
    case 'TAX_DISCREPANCY':
      return `Dear ${supplier},\n\nInvoice ${invNum} contains a tax discrepancy of $${Math.abs(taxDelta).toFixed(2)}. Please resubmit with corrected applicable tax rate.\n\nRegards,\nAccounts Payable Team`;
    case 'EXTRACTION_NOISE_UNSURE':
      return `Internal Audit Note: Invoice ${invNum} routed to Senior AP Analyst queue due to low PDF OCR confidence. Manual review required.`;
    default:
      return `Invoice ${invNum} approved for payment. No discrepancies found.`;
  }
}

function buildChecklist(defect) {
  const map = {
    TRUE_DUPLICATE: ['Verify previous payment remittance in bank ledger', 'Check ERP for duplicate transaction ID', 'Contact vendor AP team to confirm cancellation'],
    QUANTITY_MISMATCH: ['Check warehouse short-shipment log', 'Request partial billing adjustment from vendor', 'Confirm receiving dock sign-off'],
    PRICE_DRIFT: ['Verify contracted pricing tier in procurement system', 'Request credit memo from vendor', 'Cross-check blanket PO terms'],
    MISSING_GOODS_RECEIPT: ['Ping warehouse manager for GR posting confirmation', 'Verify physical delivery with courier tracking'],
    TAX_DISCREPANCY: ['Verify applicable state vs local tax rate', 'Request corrected invoice from vendor'],
    EXTRACTION_NOISE_UNSURE: ['Manually inspect raw invoice PDF scan', 'Verify total dollar amount against line items', 'Confirm PO number visibility'],
    SUBSCRIPTION_TRAP: [],
    PERFECT_MATCH: []
  };
  return map[defect] || [];
}

// ── APP STATE ─────────────────────────────────────────────────────────────
let activeFilter = 'ALL';
let selectedId   = null;
let page         = 0;
const PAGE_SIZE  = 12;
let dupCost = 94000, escCost = 15, wrngCost = 50;

// ── INIT ──────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  renderStats();
  renderTable();
  updateCostMatrix();
  setupListeners();
});

// ── STATS ─────────────────────────────────────────────────────────────────
function renderStats() {
  const cleared = invoiceExceptions.filter(i => i.category === 'CLEARED_AUTO_MATCH').length;
  const dups    = invoiceExceptions.filter(i => i.category === 'TRUE_DUPLICATE_RISK').length;
  const humans  = invoiceExceptions.filter(i => i.is_abstention).length;
  const dupLoss = dups * 94000;

  document.getElementById('stat-total').textContent = invoiceExceptions.length;
  document.getElementById('stat-cleared').textContent = cleared;
  document.getElementById('stat-dup').textContent = dups;
  document.getElementById('stat-dup-loss').textContent = `$${(dups * 94000).toLocaleString()} at risk`;
  document.getElementById('stat-human').textContent = humans;
  document.getElementById('hdr-risk-amount').textContent = `$${dupLoss.toLocaleString()}`;
  document.getElementById('hdr-proc-count').textContent = invoiceExceptions.length;
  // Total financial loss placeholder
  document.getElementById('stat-loss').textContent = '$' + (dups * 94000 + humans * 15).toLocaleString();
}

// ── TABLE ─────────────────────────────────────────────────────────────────
function filteredData() {
  if (activeFilter === 'ALL') return invoiceExceptions;
  return invoiceExceptions.filter(i => i.category === activeFilter);
}

function renderTable() {
  const data = filteredData();
  const totalPages = Math.ceil(data.length / PAGE_SIZE);
  const pageData = data.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
  const tbody = document.getElementById('invoice-tbody');
  tbody.innerHTML = '';

  pageData.forEach(inv => {
    const tr = document.createElement('tr');
    if (inv.invoice_id === selectedId) tr.classList.add('selected');

    const amountStyle = inv.category === 'TRUE_DUPLICATE_RISK' ? 'color:var(--danger);font-weight:700;' : '';
    tr.innerHTML = `
      <td style="font-family:var(--mono);font-size:11px;">${inv.invoice_number}</td>
      <td style="max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${inv.supplier_name}">${inv.supplier_name}</td>
      <td style="font-family:var(--mono);font-size:11px;">${inv.po_id}</td>
      <td style="${amountStyle}font-family:var(--mono);">$${inv.inv_total.toLocaleString(undefined, {minimumFractionDigits:2})}</td>
      <td><span class="cat-pill ${inv.category}">${inv.category.replace(/_/g,' ')}</span></td>
      <td style="font-size:11px;color:var(--text-muted);">${inv.action.replace(/_/g,' ')}</td>
      <td><button class="inspect-btn" data-id="${inv.invoice_id}">Inspect</button></td>
    `;
    tr.addEventListener('click', () => selectInvoice(inv.invoice_id));
    tbody.appendChild(tr);
  });

  document.getElementById('page-info').textContent = `Page ${page + 1} / ${Math.max(1, totalPages)}`;
  document.getElementById('page-prev').disabled = page === 0;
  document.getElementById('page-next').disabled = page >= totalPages - 1;
}

// ── INSPECTOR ─────────────────────────────────────────────────────────────
function selectInvoice(id) {
  selectedId = id;
  renderTable();
  const inv = invoiceExceptions.find(i => i.invoice_id === id);
  if (!inv) return;

  document.getElementById('inspector-placeholder').classList.add('hidden');
  document.getElementById('inspector-content').classList.remove('hidden');
  document.getElementById('inspect-inv-id').textContent = `${inv.invoice_id} · ${inv.invoice_date}`;

  // Invoice doc
  document.getElementById('inv-num').textContent   = inv.invoice_number;
  document.getElementById('inv-sup').textContent   = inv.supplier_name;
  document.getElementById('inv-qty').textContent   = inv.inv_qty;
  document.getElementById('inv-price').textContent = `$${inv.inv_price.toFixed(2)}`;
  document.getElementById('inv-tax').textContent   = `$${inv.inv_tax.toFixed(2)}`;
  document.getElementById('inv-total').textContent = `$${inv.inv_total.toFixed(2)}`;

  const confEl = document.getElementById('inv-conf');
  const confPct = (inv.extraction_confidence * 100).toFixed(0) + '%';
  confEl.textContent = confPct;
  confEl.style.color = inv.extraction_confidence < 0.70 ? 'var(--danger)' : 'var(--success)';

  // PO doc
  document.getElementById('po-id-val').textContent    = inv.po_id;
  document.getElementById('po-qty').textContent       = inv.po_qty;
  document.getElementById('po-price').textContent     = `$${inv.po_price.toFixed(2)}`;
  document.getElementById('po-tax-rate').textContent  = inv.po_tax_rate;
  document.getElementById('po-total').textContent     = `$${inv.po_total.toFixed(2)}`;

  // GR doc
  const grStatusEl = document.getElementById('gr-status');
  grStatusEl.textContent  = inv.gr_posted ? 'GR Posted' : 'NOT POSTED';
  grStatusEl.style.background = inv.gr_posted ? 'var(--success-dim)' : 'var(--danger-dim)';
  grStatusEl.style.color      = inv.gr_posted ? 'var(--success)' : 'var(--danger)';
  document.getElementById('gr-qty').textContent = inv.gr_qty;

  // Deltas
  const dg = document.getElementById('delta-grid');
  dg.innerHTML = '';
  const deltas = [
    ['Qty Billed vs Received', inv.deltas.qty_delta, ''],
    ['Unit Price Delta',       inv.deltas.price_delta, '$'],
    ['Price Drift %',          inv.deltas.price_drift_pct, '%'],
    ['Tax Delta',              inv.deltas.tax_delta, '$']
  ];
  deltas.forEach(([label, val, unit]) => {
    const cls = val > 0 ? 'delta-positive' : val < 0 ? 'delta-negative' : 'delta-zero';
    const prefix = val > 0 ? '+' : '';
    const display = unit === '$' ? `${prefix}$${Math.abs(val).toFixed(2)}${val < 0 ? ' Cr' : ''}` :
                    unit === '%' ? `${prefix}${val}%` : `${prefix}${val}`;
    dg.innerHTML += `<div class="delta-item">
      <span class="delta-label">${label}</span>
      <span class="delta-val ${cls}">${display}</span>
    </div>`;
  });

  // Duplicate detection
  const dupEl = document.getElementById('dup-result-content');
  const dr = inv.dup_result;
  const dupColor = dr.is_risk ? 'var(--danger)' : 'var(--success)';
  const dupBg = dr.is_risk ? 'var(--danger-dim)' : 'var(--success-dim)';
  dupEl.innerHTML = `
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
      <span style="background:${dupBg};color:${dupColor};border:1px solid ${dupColor};padding:3px 10px;border-radius:10px;font-size:11px;font-weight:700;">
        ${dr.type.replace(/_/g,' ')}
      </span>
    </div>
    <p style="font-size:12px;color:var(--text-muted);">${dr.explanation}</p>
  `;

  // Classification
  document.getElementById('class-cat').textContent    = inv.category.replace(/_/g, ' ');
  document.getElementById('class-conf').textContent   = (inv.confidence * 100).toFixed(0) + '%';
  document.getElementById('class-action').textContent = inv.action.replace(/_/g, ' ');

  // Email
  document.getElementById('res-email-body').textContent = inv.resolution_email;

  // Checklist
  const checklistSec = document.getElementById('checklist-section');
  const checklistUl  = document.getElementById('res-checklist');
  if (inv.checklist && inv.checklist.length > 0) {
    checklistUl.innerHTML = inv.checklist.map(item => `<li>${item}</li>`).join('');
    checklistSec.classList.remove('hidden');
  } else {
    checklistSec.classList.add('hidden');
  }
}

// ── COST MATRIX SIMULATOR ─────────────────────────────────────────────────
function updateCostMatrix() {
  const expectedCategories = {
    PERFECT_MATCH: 'CLEARED_AUTO_MATCH',
    QUANTITY_MISMATCH: 'QUANTITY_MISMATCH',
    PRICE_DRIFT: 'PRICE_DRIFT',
    TAX_DISCREPANCY: 'TAX_DISCREPANCY',
    MISSING_GOODS_RECEIPT: 'MISSING_GOODS_RECEIPT',
    TRUE_DUPLICATE: 'TRUE_DUPLICATE_RISK',
    SUBSCRIPTION_TRAP: 'VALID_SUBSCRIPTION_RECURRING',
    EXTRACTION_NOISE_UNSURE: 'UNSURE_NEEDS_HUMAN_CHECK'
  };
  const missedDuplicates = invoiceExceptions.filter(i => i.ground_truth_defect === 'TRUE_DUPLICATE' && i.category !== 'TRUE_DUPLICATE_RISK').length;
  const escl = invoiceExceptions.filter(i => i.ground_truth_defect === 'PERFECT_MATCH' && i.is_abstention).length;
  const wrong = invoiceExceptions.filter(i => !i.is_abstention && i.category !== expectedCategories[i.ground_truth_defect]).length;

  const totalLoss = (missedDuplicates * dupCost) + (escl * escCost) + (wrong * wrngCost);

  // Baseline F1 assumes naive approach misses 80% of duplicates
  const duplicateCount = invoiceExceptions.filter(i => i.ground_truth_defect === 'TRUE_DUPLICATE').length;
  const baselineLoss = Math.floor(duplicateCount * 0.8) * dupCost + escl * 100 + wrong * 200;

  document.getElementById('cost-result-dynamic').textContent = `$${totalLoss.toLocaleString()}`;
  document.getElementById('baseline-f1-loss').textContent    = `$${baselineLoss.toLocaleString()}`;
  document.getElementById('stat-loss').textContent           = `$${totalLoss.toLocaleString()}`;
  document.getElementById('hdr-risk-amount').textContent     = `$${(dups * dupCost).toLocaleString()}`;
}

// ── EVENT LISTENERS ───────────────────────────────────────────────────────
function setupListeners() {
  // Filter buttons
  document.querySelectorAll('.filter-btn[data-filter]').forEach(btn => {
    btn.addEventListener('click', e => {
      document.querySelectorAll('.filter-btn[data-filter]').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      activeFilter = e.target.dataset.filter;
      page = 0;
      renderTable();
    });
  });

  // Pagination
  document.getElementById('page-prev').addEventListener('click', () => { if (page > 0) { page--; renderTable(); } });
  document.getElementById('page-next').addEventListener('click', () => {
    if ((page + 1) * PAGE_SIZE < filteredData().length) { page++; renderTable(); }
  });

  // Cost matrix sliders
  document.getElementById('dup-cost-slider').addEventListener('input', e => {
    dupCost = +e.target.value;
    document.getElementById('dup-cost-val').textContent = `$${dupCost.toLocaleString()}`;
    updateCostMatrix();
  });
  document.getElementById('esc-cost-slider').addEventListener('input', e => {
    escCost = +e.target.value;
    document.getElementById('esc-cost-val').textContent = `$${escCost}`;
    updateCostMatrix();
  });
  document.getElementById('wrng-cost-slider').addEventListener('input', e => {
    wrngCost = +e.target.value;
    document.getElementById('wrng-cost-val').textContent = `$${wrngCost}`;
    updateCostMatrix();
  });

  // Delegate inspect button clicks
  document.getElementById('invoice-table').addEventListener('click', e => {
    const btn = e.target.closest('[data-id]');
    if (btn) { e.stopPropagation(); selectInvoice(btn.dataset.id); }
  });
}
