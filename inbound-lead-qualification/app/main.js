// Sample leads embedded dataset for browser demo
const sampleLeads = [
  {
    "lead_id": "LEAD-001",
    "timestamp": "2026-09-29T10:05:00Z",
    "form_input": {
      "name": "Sarah Jenkins",
      "work_email": "sjenkins@cloudscale.io",
      "job_title": "VP of Infrastructure",
      "company_domain": "cloudscale.io",
      "message": "We are looking to automate our K8s cluster deployments across 400+ nodes."
    },
    "enrichment": {
      "found": true,
      "company_name": "CloudScale Systems",
      "engineering_headcount": 450,
      "tech_stack": ["Kubernetes", "AWS EKS", "Terraform"],
      "geography": "US",
      "company_type": "Product Company",
      "snippets": [
        {"snippet_id": "SNIP-001", "fact": "CloudScale Systems has 450 engineers across US offices.", "source": "LinkedIn Talent Insights 2026"},
        {"snippet_id": "SNIP-002", "fact": "CloudScale operates 400+ Kubernetes nodes on AWS EKS.", "source": "KubeCon 2025 Case Study"}
      ]
    },
    "score": 85,
    "tier": "QUALIFIED",
    "disqualified": false,
    "latency_ms": 1.4,
    "route": "HIGH_PRIORITY_SDR_QUEUE",
    "claims": [
      {"sentence": "I noticed CloudScale Systems is running production Kubernetes infrastructure (400+ nodes on AWS EKS).", "snippet_id": "SNIP-002", "source": "KubeCon 2025 Case Study"},
      {"sentence": "Given your team of 450+ engineers, maintaining deployment velocity is critical.", "snippet_id": "SNIP-001", "source": "LinkedIn Talent Insights 2026"}
    ]
  },
  {
    "lead_id": "LEAD-002",
    "timestamp": "2026-09-29T10:12:00Z",
    "form_input": {
      "name": "David Chen",
      "work_email": "dchen@devtools-rival.com",
      "job_title": "Product Manager",
      "company_domain": "devtools-rival.com",
      "message": "Interested in a demo for our internal research."
    },
    "enrichment": {"found": false, "company_name": "DevTools Rival", "engineering_headcount": 0, "tech_stack": [], "geography": "Unknown", "snippets": []},
    "score": 0,
    "tier": "DISQUALIFIED",
    "disqualified": true,
    "disq_reason": "Competitor domain identified (devtools-rival.com). Lead flagged for security audit.",
    "latency_ms": 0.3,
    "route": "DISQUALIFIED_LOG",
    "claims": []
  },
  {
    "lead_id": "LEAD-003",
    "timestamp": "2026-09-29T10:18:00Z",
    "form_input": {
      "name": "Alex Smith",
      "work_email": "alex.student2026@gmail.com",
      "job_title": "CS Student",
      "company_domain": "gmail.com",
      "message": "Need free access for university project."
    },
    "enrichment": {"found": false, "company_name": "Gmail Provider", "engineering_headcount": 0, "tech_stack": [], "geography": "Unknown", "snippets": []},
    "score": 0,
    "tier": "DISQUALIFIED",
    "disqualified": true,
    "disq_reason": "Freemail provider detected (gmail.com). B2B corporate domain required.",
    "latency_ms": 0.2,
    "route": "DISQUALIFIED_LOG",
    "claims": []
  },
  {
    "lead_id": "LEAD-004",
    "timestamp": "2026-09-29T10:25:00Z",
    "form_input": {
      "name": "Marcus Vance",
      "work_email": "m.vance@fintechglobal.com",
      "job_title": "Head of Platform Engineering",
      "company_domain": "fintechglobal.com",
      "message": "We have 350+ software engineers running microservices on EKS in the US and Germany."
    },
    "enrichment": {
      "found": true,
      "company_name": "FinTech Global",
      "engineering_headcount": 350,
      "tech_stack": ["Kubernetes", "Azure AKS"],
      "geography": "US & EU",
      "company_type": "Product Company",
      "snippets": [
        {"snippet_id": "SNIP-003", "fact": "FinTech Global employs 350+ software engineers across NY and Frankfurt.", "source": "Engineering Blog 2026"},
        {"snippet_id": "SNIP-004", "fact": "FinTech Global processes 10M transactions daily on Azure AKS Kubernetes clusters.", "source": "Cloud Summit Report"}
      ]
    },
    "score": 85,
    "tier": "QUALIFIED",
    "disqualified": false,
    "latency_ms": 1.6,
    "route": "HIGH_PRIORITY_SDR_QUEUE",
    "claims": [
      {"sentence": "I noticed FinTech Global is running production Kubernetes infrastructure (10M transactions daily on Azure AKS).", "snippet_id": "SNIP-004", "source": "Cloud Summit Report"},
      {"sentence": "Given your team of 350+ engineers, maintaining deployment velocity is critical.", "snippet_id": "SNIP-003", "source": "Engineering Blog 2026"}
    ]
  },
  {
    "lead_id": "LEAD-005",
    "timestamp": "2026-09-29T10:30:00Z",
    "form_input": {
      "name": "Elena Rostova",
      "work_email": "elena@agencydesign.co",
      "job_title": "Marketing Director",
      "company_domain": "agencydesign.co",
      "message": "We offer dev agency services."
    },
    "enrichment": {
      "found": true,
      "company_name": "Agency Design Studio",
      "engineering_headcount": 12,
      "tech_stack": ["Webflow", "React"],
      "geography": "US",
      "company_type": "Agency",
      "snippets": [{"snippet_id": "SNIP-010", "fact": "Agency Design Studio is a 30-person web design agency.", "source": "Clutch.co"}]
    },
    "score": 0,
    "tier": "DISQUALIFIED",
    "disqualified": true,
    "disq_reason": "Company type 'Agency' does not match product target ICP.",
    "latency_ms": 0.5,
    "route": "DISQUALIFIED_LOG",
    "claims": []
  }
];

let activeFilter = 'ALL';
let selectedLeadId = null;

document.addEventListener('DOMContentLoaded', () => {
  renderStats();
  renderLeadsTable();
  setupEventListeners();
});

function renderStats() {
  document.getElementById('stat-total').textContent = sampleLeads.length;
  document.getElementById('stat-qualified').textContent = sampleLeads.filter(l => l.tier === 'QUALIFIED').length;
  document.getElementById('stat-nurture').textContent = sampleLeads.filter(l => l.tier === 'NURTURE').length;
  document.getElementById('stat-disqualified').textContent = sampleLeads.filter(l => l.disqualified).length;

  const avgLat = (sampleLeads.reduce((acc, l) => acc + l.latency_ms, 0) / sampleLeads.length).toFixed(2);
  document.getElementById('hdr-avg-latency').textContent = `Avg Latency: ${avgLat}ms (Target <1800s)`;
}

function renderLeadsTable() {
  const tbody = document.getElementById('leads-tbody');
  tbody.innerHTML = '';

  const filtered = sampleLeads.filter(lead => {
    if (activeFilter === 'QUALIFIED') return lead.tier === 'QUALIFIED';
    if (activeFilter === 'DISQUALIFIED') return lead.disqualified;
    return true;
  });

  filtered.forEach(lead => {
    const tr = document.createElement('tr');
    if (lead.lead_id === selectedLeadId) tr.classList.add('selected');
    
    tr.innerHTML = `
      <td><span style="font-family: var(--font-mono); color: var(--primary-accent);">${lead.lead_id}</span></td>
      <td><strong>${lead.form_input.name}</strong><br><span style="font-size: 11px; color: var(--text-muted);">${lead.form_input.job_title}</span></td>
      <td>${lead.form_input.company_domain}</td>
      <td><strong>${lead.score}/100</strong></td>
      <td><span class="status-tag ${lead.tier}">${lead.tier}</span></td>
      <td><button class="filter-btn" style="padding: 4px 8px; font-size: 11px;">Inspect Trace</button></td>
    `;

    tr.addEventListener('click', () => selectLead(lead.lead_id));
    tbody.appendChild(tr);
  });
}

function selectLead(leadId) {
  selectedLeadId = leadId;
  renderLeadsTable();

  const lead = sampleLeads.find(l => l.lead_id === leadId);
  if (!lead) return;

  document.getElementById('inspector-placeholder').classList.add('hidden');
  document.getElementById('inspector-content').classList.remove('hidden');

  document.getElementById('inspect-lead-id').textContent = lead.lead_id + ' | SLA: ' + lead.latency_ms + 'ms';

  // Form Input vs Enriched Data
  document.getElementById('p-name').textContent = lead.form_input.name;
  document.getElementById('p-email').textContent = lead.form_input.work_email;
  document.getElementById('p-title').textContent = lead.form_input.job_title;
  document.getElementById('p-domain').textContent = lead.form_input.company_domain;
  document.getElementById('p-msg').textContent = `"${lead.form_input.message}"`;

  document.getElementById('e-company').textContent = lead.enrichment.company_name;
  document.getElementById('e-eng').textContent = lead.enrichment.engineering_headcount + ' engineers';
  document.getElementById('e-stack').textContent = lead.enrichment.tech_stack.join(', ') || 'N/A';
  document.getElementById('e-geo').textContent = lead.enrichment.geography;
  document.getElementById('e-status').textContent = lead.enrichment.found ? 'ENRICHED_200_OK' : 'NOT_FOUND_FALLBACK';

  // Score
  document.getElementById('score-circle-val').textContent = lead.score;
  document.getElementById('score-tier-lbl').textContent = lead.tier;
  document.getElementById('score-route-lbl').textContent = lead.disqualified ? lead.disq_reason : `Route: ${lead.route}`;

  // Email & Claim Trace
  const emailSubjEl = document.getElementById('email-subject-val');
  const emailBodyEl = document.getElementById('email-body-val');
  const traceListEl = document.getElementById('trace-claims-list');
  traceListEl.innerHTML = '';

  if (lead.disqualified) {
    emailSubjEl.textContent = '[Outbound Email Suppressed - Lead Disqualified]';
    emailBodyEl.textContent = `Pre-filter disqualified lead: ${lead.disq_reason}\nNo email sent to prospect. Zero cost incurred.`;
  } else if (lead.claims && lead.claims.length > 0) {
    emailSubjEl.textContent = `Scaling K8s workflows for ${lead.enrichment.company_name}`;
    
    let bodyText = `Hi ${lead.form_input.name.split(' ')[0]},\n\nThanks for reaching out!\n\n`;
    lead.claims.forEach(c => {
      bodyText += `${c.sentence} [Trace: ${c.snippet_id}]\n\n`;

      const tItem = document.createElement('div');
      tItem.className = 'trace-item';
      tItem.innerHTML = `<span class="snip-id">[${c.snippet_id}] Verified</span>: ${c.sentence} <br><i style="color: var(--text-muted);">Source: ${c.source}</i>`;
      traceListEl.appendChild(tItem);
    });
    bodyText += `Would you have 15 minutes this Thursday for a quick demo?\n\nBest regards,\nAlex Vance\nLead Solutions Engineer`;
    emailBodyEl.textContent = bodyText;
  } else {
    emailSubjEl.textContent = `DevTools Platform Overview for ${lead.enrichment.company_name}`;
    emailBodyEl.textContent = `Hi ${lead.form_input.name.split(' ')[0]},\n\nThanks for reaching out! We offer developer productivity tools to streamline infrastructure management.\n\nWould you be open to a 15-minute introductory call?\n\nBest regards,\nAlex Vance`;
    traceListEl.innerHTML = `<div class="trace-item" style="border-color: var(--warning-color);"><span style="color: var(--warning-color);">Generic Fallback</span>: Research found no verified snippets. Zero unverified claims injected.</div>`;
  }
}

function setupEventListeners() {
  document.querySelectorAll('.filter-btn[data-filter]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.filter-btn[data-filter]').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      activeFilter = e.target.getAttribute('data-filter');
      renderLeadsTable();
    });
  });
}
