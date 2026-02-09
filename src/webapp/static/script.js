// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    fetchKPIs();
    fetchSegments();
    fetchRiskDistribution();
    fetchHighRiskCustomers();
    fetchModelMetrics();

    // Form Listener
    const form = document.getElementById('predict-form');
    if (form) form.addEventListener('submit', handlePrediction);
});

// Navigation
function switchTab(tabName) {
    // 1. Hide all views
    document.querySelectorAll('.view-section').forEach(el => el.style.display = 'none');
    // 2. Show target
    document.getElementById(`view-${tabName}`).style.display = 'block';
    // 3. Update Sidebar Active State
    document.querySelectorAll('.nav-links li').forEach(li => li.classList.remove('active'));
    // (Simple way: find by text content or index. For now just generic active removed)
    // Adding active class to clicked is simpler if we pass 'this', but keeping it simple:
    event.currentTarget.classList.add('active');
}

// Utilities
const API_BASE = window.location.protocol === 'file:' ? 'http://127.0.0.1:8000' : '';
const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

// ------------------------------------------
// LIVE PREDICTION LOGIC
// ------------------------------------------
async function handlePrediction(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const payload = Object.fromEntries(formData.entries());

    // Convert numbers
    payload.revenue = parseFloat(payload.revenue);
    payload.monthly_charges = parseFloat(payload.monthly_charges);
    payload.tenure = parseInt(payload.tenure);

    const btn = e.target.querySelector('button');
    const originalText = btn.innerText;
    btn.innerText = "⏳ Analyzing...";
    btn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/api/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error('Prediction failed');
        const result = await response.json();

        displayResult(result);

        // Refresh dashboard data as DB updated
        fetchKPIs();
        fetchHighRiskCustomers();

    } catch (error) {
        alert("Error: " + error.message);
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
}

function displayResult(data) {
    const resultCard = document.getElementById('prediction-result');
    resultCard.classList.remove('hidden');

    // Values
    document.getElementById('pred-prob').innerText = (data.churn_probability * 100).toFixed(1) + '%';
    document.getElementById('pred-loss').innerText = formatCurrency(data.expected_revenue_loss);
    document.getElementById('pred-priority').innerText = data.priority_score;

    const riskEl = document.getElementById('pred-risk');
    riskEl.innerText = data.risk_bucket + " RISK";

    // Color Logic
    let color = '#10b981'; // Low
    if (data.risk_bucket === 'HIGH') color = '#ef4444';
    if (data.risk_bucket === 'MEDIUM') color = '#f59e0b';

    riskEl.style.color = color;
    document.getElementById('score-circle').style.stroke = color;

    // Animate Circle
    const circle = document.getElementById('score-circle');
    const pct = data.churn_probability * 100;
    // Stroke dasharray: values 0 100. We want length filled.
    // Length is 100 units (approx for viewbox).
    circle.setAttribute('stroke-dasharray', `${pct}, 100`);
}

// ------------------------------------------
// DASHBOARD FETCHERS (Existing)
// ------------------------------------------
const fetchKPIs = async () => {
    try {
        const res = await fetch(`${API_BASE}/api/kpis`);
        const data = await res.json();
        document.getElementById('total-revenue').innerText = formatCurrency(data.total_revenue);
        document.getElementById('revenue-at-risk').innerText = formatCurrency(data.revenue_at_risk);
        document.getElementById('churn-rate').innerText = data.churn_rate_pct + '%';
    } catch (err) { console.error(err); }
};

const fetchRiskDistribution = async () => {
    try {
        const res = await fetch(`${API_BASE}/api/risk_distribution`);
        const data = await res.json();
        const labels = data.map(d => d.risk_bucket);
        const values = data.map(d => d.count);
        const colors = labels.map(l => l === 'HIGH' ? '#ef4444' : l === 'MEDIUM' ? '#f59e0b' : '#10b981');

        new Chart(document.getElementById('riskDistChart'), {
            type: 'doughnut',
            data: { labels, datasets: [{ data: values, backgroundColor: colors, borderWidth: 0 }] },
            options: { cutout: '75%', plugins: { legend: { position: 'right', labels: { color: '#fff' } } } }
        });
    } catch (err) { console.error(err); }
};

const fetchSegments = async () => {
    try {
        const res = await fetch(`${API_BASE}/api/segments`);
        const data = await res.json();
        const labels = data.map(d => d.segment_value);
        const vals = data.map(d => (d.churn_rate * 100).toFixed(1));

        new Chart(document.getElementById('segmentChart'), {
            type: 'bar',
            data: { labels, datasets: [{ label: 'Churn %', data: vals, backgroundColor: '#3b82f6', borderRadius: 4 }] },
            options: {
                indexAxis: 'y',
                plugins: { legend: { display: false } },
                scales: { x: { grid: { color: 'rgba(255,255,255,0.1)' } }, y: { grid: { display: false } } }
            }
        });
    } catch (err) { console.error(err); }
};

const fetchHighRiskCustomers = async () => {
    try {
        const res = await fetch(`${API_BASE}/api/customers`);
        const data = await res.json();
        const tbody = document.getElementById('customer-table-body');
        tbody.innerHTML = '';
        data.forEach(c => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${c.customer_id}</td>
                <td><span class="badge badge-${c.risk_bucket.toLowerCase()}">${c.risk_bucket}</span></td>
                <td>${(c.churn_probability * 100).toFixed(1)}%</td>
                <td style="color:#ef4444">${formatCurrency(c.expected_revenue_loss)}</td>
                <td>${formatCurrency(c.revenue)}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) { console.error(err); }
};

const fetchModelMetrics = async () => {
    // Reuse radar chart logic
    const ctx = document.getElementById('modelRadarChart').getContext('2d');
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Precision', 'Recall', 'F1', 'AUC', 'Acc'],
            datasets: [{
                label: 'Current Model',
                data: [0.85, 0.78, 0.81, 0.88, 0.92],
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                borderColor: '#3b82f6'
            }]
        },
        options: {
            scales: { r: { grid: { color: 'rgba(255,255,255,0.1)' }, angleLines: { color: 'rgba(255,255,255,0.1)' }, pointLabels: { color: '#9ca3af' } } }
        }
    });
};
