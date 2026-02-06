document.addEventListener('DOMContentLoaded', () => {
    fetchKPIs();
    fetchSegments();
    fetchHighRiskCustomers();
    fetchModelMetrics();
});

const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
};

const fetchKPIs = async () => {
    try {
        const response = await fetch('/api/kpis');
        const data = await response.json();

        document.getElementById('total-revenue').innerText = formatCurrency(data.total_revenue);
        document.getElementById('revenue-at-risk').innerText = formatCurrency(data.revenue_at_risk);
        document.getElementById('churn-rate').innerText = data.churn_rate_pct + '%';
        document.getElementById('high-risk-pct').innerText = data.high_risk_pct + '%';
    } catch (error) {
        console.error('Error fetching KPIs:', error);
    }
};

const fetchSegments = async () => {
    try {
        const response = await fetch('/api/segments');
        const data = await response.json();

        const labels = data.map(d => d.segment_value);
        const churnRates = data.map(d => (d.churn_rate * 100).toFixed(1));

        const ctx = document.getElementById('segmentChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Churn Rate (%)',
                    data: churnRates,
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(245, 158, 11, 0.8)'
                    ],
                    borderWidth: 0,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error fetching segments:', error);
    }
};

const fetchHighRiskCustomers = async () => {
    try {
        const response = await fetch('/api/customers');
        const data = await response.json();

        const tbody = document.getElementById('customer-table-body');
        tbody.innerHTML = '';

        data.forEach(customer => {
            const row = document.createElement('tr');

            // Risk Badge Logic
            let badgeClass = 'badge-low';
            if (customer.risk_bucket === 'HIGH') badgeClass = 'badge-high';
            else if (customer.risk_bucket === 'MEDIUM') badgeClass = 'badge-medium';

            row.innerHTML = `
                <td><code>${customer.customer_id}</code></td>
                <td><span class="badge ${badgeClass}">${customer.risk_bucket}</span></td>
                <td>${(customer.churn_probability * 100).toFixed(1)}%</td>
                <td class="danger">${formatCurrency(customer.expected_revenue_loss)}</td>
                <td>${formatCurrency(customer.revenue)}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching customers:', error);
    }
};

const fetchModelMetrics = async () => {
    try {
        const response = await fetch('/api/metrics');
        const data = await response.json();

        document.getElementById('model-version').innerText = `v${data.model_version}`;

        const metricsContainer = document.getElementById('metrics-list');
        metricsContainer.innerHTML = `
            <div class="metric-item">
                <div class="metric-label">AUC - ROC</div>
                <div class="metric-val text-accent">${data.roc_auc.toFixed(3)}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Precision</div>
                <div class="metric-val text-success">${data.precision_score.toFixed(3)}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Recall</div>
                <div class="metric-val text-warning">${data.recall_score.toFixed(3)}</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">Training Size</div>
                <div class="metric-val">${data.training_rows.toLocaleString()}</div>
            </div>
        `;
    } catch (error) {
        console.error('Error fetching metrics:', error);
    }
};
