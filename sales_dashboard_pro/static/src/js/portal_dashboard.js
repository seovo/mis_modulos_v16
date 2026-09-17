/* =============================================
   CRM Portal Share Dashboard JS logic
   ============================================= */

document.addEventListener("DOMContentLoaded", function () {
    const dataEl = document.getElementById('crm_dashboard_data');
    if (!dataEl) return;

    const dashboardData = JSON.parse(dataEl.getAttribute('data-dashboard') || '{}');
    const currencySymbol = dataEl.getAttribute('data-currency-symbol') || '$';
    const currencyPosition = dataEl.getAttribute('data-currency-position') || 'before';

    function formatCurrency(val) {
        const num = Number(val || 0);
        const formattedNum = num.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        return currencyPosition === 'before' ? (currencySymbol + formattedNum) : (formattedNum + ' ' + currencySymbol);
    }

    // 1. Won vs Lost Donut values
    const kpiWon = dashboardData.kpi_won || 0;
    const kpiLost = dashboardData.kpi_lost || 0;

    document.getElementById('kpi-total-val').innerText = dashboardData.kpi_total || 0;
    document.getElementById('kpi-won-val').innerText = kpiWon;
    document.getElementById('kpi-lost-val').innerText = kpiLost;
    document.getElementById('kpi-active-val').innerText = dashboardData.kpi_active || 0;

    document.getElementById('crm-donut-won-val').innerText = kpiWon;
    document.getElementById('crm-donut-lost-val').innerText = kpiLost;

    // 2. Performance Metrics list rendering
    const metricsList = document.getElementById('crm-performance-metrics-list');
    if (metricsList) {
        metricsList.innerHTML = '';
        const perfKpis = dashboardData.perf_kpis || [];
        perfKpis.forEach(function (kpi) {
            const row = document.createElement('div');
            row.className = 'crm-sidebar-metric-row';

            let valStr = kpi.value;
            if (kpi.format === 'currency') {
                valStr = formatCurrency(kpi.value);
            } else if (kpi.suffix) {
                valStr = kpi.value + kpi.suffix;
            }

            row.innerHTML = `
                <div class="crm-sidebar-metric-left">
                    <span class="crm-sidebar-metric-icon" style="color: ${kpi.color || '#0ea5e9'};">
                        <i class="fa ${kpi.icon || 'fa-usd'}"></i>
                    </span>
                    <span class="crm-sidebar-metric-label">${kpi.label}</span>
                </div>
                <span class="crm-sidebar-metric-value">${valStr}</span>
            `;
            metricsList.appendChild(row);
        });
    }

    // 3. Won/Lost Donut Chart
    new Chart(document.getElementById('crmWonLostDonut'), {
        type: 'doughnut',
        data: {
            labels: ['Won', 'Lost'],
            datasets: [{
                data: [kpiWon, kpiLost],
                backgroundColor: ['#10b981', '#f43f5e'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            cutout: '75%'
        }
    });

    // 4. Win vs Loss Trend
    const trendData = dashboardData.win_loss || { labels: [], won: [], lost: [] };
    new Chart(document.getElementById('crmWinLossTrend'), {
        type: 'line',
        data: {
            labels: trendData.labels,
            datasets: [
                {
                    label: 'Won Deals',
                    data: trendData.won,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.04)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Lost Deals',
                    data: trendData.lost,
                    borderColor: '#f43f5e',
                    backgroundColor: 'rgba(244, 63, 94, 0.04)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false } },
                y: { ticks: { precision: 0 } }
            }
        }
    });

    // 5. Stage Distribution
    const stageData = dashboardData.stage_donut || { labels: [], values: [], colors: [] };
    new Chart(document.getElementById('crmStageBar'), {
        type: 'bar',
        data: {
            labels: stageData.labels,
            datasets: [{
                data: stageData.values,
                backgroundColor: stageData.colors || '#0ea5e9',
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false } },
                y: { ticks: { precision: 0 } }
            }
        }
    });

    // 6. Sales Funnel
    const funnelData = dashboardData.funnel || { labels: [], values: [], colors: [] };
    new Chart(document.getElementById('crmSalesFunnel'), {
        type: 'bar',
        data: {
            labels: funnelData.labels,
            datasets: [{
                data: funnelData.values,
                backgroundColor: funnelData.colors || '#3b82f6',
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { precision: 0 } },
                y: { grid: { display: false } }
            }
        }
    });

    // 7. Calendar Days Builder
    const heatmap = dashboardData.heatmap || {};
    document.getElementById('crm-cal-title-month').innerText = heatmap.month_name || 'Active Month';

    let totalDeals = 0;
    const days = heatmap.days || [];
    days.forEach(function (d) {
        if (d.in_month) {
            totalDeals += (d.deal_count || 0);
        }
    });
    document.getElementById('crm-cal-stats').innerText = totalDeals + ' Deals This Month';

    const grid = document.getElementById('crm-calendar-days-grid');
    grid.innerHTML = '';
    days.forEach(function (d) {
        const cell = document.createElement('div');
        cell.className = 'crm-calendar-cell' + (d.in_month ? '' : ' other-month') + (d.is_today ? ' today' : '') + (d.deal_count > 0 ? ' has-deals' : '');

        let badgesHtml = '';
        if (d.deal_count > 0) {
            const revFormatted = d.expected_revenue >= 1000
                ? (currencySymbol + (d.expected_revenue / 1000).toFixed(0) + 'k')
                : (currencySymbol + d.expected_revenue);
            badgesHtml = `
                <div class="crm-calendar-badge-group">
                    <span class="crm-calendar-deal-badge">${d.deal_count}</span>
                    <span class="crm-calendar-rev-badge">${revFormatted}</span>
                </div>
            `;
        }

        cell.innerHTML = `
            <span class="crm-calendar-day-num">${d.day_num}</span>
            ${badgesHtml}
        `;
        grid.appendChild(cell);
    });
});
