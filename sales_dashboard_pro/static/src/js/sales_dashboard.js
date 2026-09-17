/** @odoo-module **/
/**
 * Sales 360 Dashboard Pro — OWL Component
 * =========================================
 * Premium Analytics: KPIs · Funnel · Trend · Donut ·
 * Top 3 Products · List View (sale.order) · Customer Map
 */
import { Component, useState, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { jsonrpc } from "@web/core/network/rpc_service";
import { useService } from "@web/core/utils/hooks";

// ─── Palette (Premium Indigo / Violet / Blue) ──────────────────────────────────
const PALETTE = [
    '#6366f1', '#818cf8', '#a5b4fc', '#4f46e5',
    '#3730a3', '#312e81', '#c7d2fe', '#e0e7ff',
    '#3b82f6', '#60a5fa', '#a855f7', '#ec4899',
];

// ─── Chart defaults ───────────────────────────────────────────────────────────
const CD = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 800, easing: 'easeInOutQuart' },
    plugins: {
        legend: {
            labels: {
                color: '#64748b',
                font: { family: 'Inter', size: 11, weight: '600' },
                boxWidth: 10, padding: 14,
            },
        },
        tooltip: {
            backgroundColor: 'rgba(255, 255, 255, 0.98)',
            borderColor: 'rgba(99, 102, 241, 0.12)',
            borderWidth: 1,
            titleColor: '#0f172a',
            bodyColor: '#475569',
            padding: 12,
            cornerRadius: 12,
            titleFont: { family: 'Inter', size: 12, weight: '700' },
            bodyFont: { family: 'Inter', size: 11 },
        },
    },
};

const SCALE_X = { grid: { display: false }, border: { display: false }, ticks: { color: '#64748b', font: { family: 'Inter', size: 10 } } };
const SCALE_Y = { grid: { color: 'rgba(0,0,0,0.03)', borderDash: [4, 4] }, border: { display: false }, ticks: { color: '#64748b', font: { family: 'Inter', size: 10 } } };

// ─── Helpers ──────────────────────────────────────────────────────────────────
function makeGradient(ctx, hex, a1 = 0.22, a2 = 0.01) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    const gr = ctx.createLinearGradient(0, 0, 0, 300);
    gr.addColorStop(0, `rgba(${r},${g},${b},${a1})`);
    gr.addColorStop(1, `rgba(${r},${g},${b},${a2})`);
    return gr;
}

function fmtNum(n) {
    if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
    if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K';
    return String(Math.round(n));
}

function defaultDates() {
    const today = new Date();
    const first = new Date(today.getFullYear(), 0, 1);
    return {
        from: first.toISOString().slice(0, 10),
        to: today.toISOString().slice(0, 10),
    };
}

// ─── Component ────────────────────────────────────────────────────────────────
export class SalesDashboard extends Component {
    static template = 'sales_dashboard_pro.SalesDashboard';

    setup() {
        const { from, to } = defaultDates();
        this.action = useService('action');

        this.state = useState({
            loading: true,
            data: null,
            dateFrom: from,
            dateTo: to,
            users: [],
            teams: [],
            states: [],
            products: [],
            partners: [],
            showShareModal: false,
        });

        // Currency info (set after data loads)
        this._currencySymbol = '$';
        this._currencyPosition = 'before';

        // Canvas refs
        this.revenueTrendChart = useRef('revenueTrendChart');
        this.stageDonutChart = useRef('stageDonutChart');
        this.salespersonChart = useRef('salespersonChart');
        this.topProductsChart = useRef('topProductsChart');
        this.categoryPieChart = useRef('categoryPieChart');

        // Container refs
        this.funnelWrap = useRef('funnelWrap');
        this.customerMapWrap = useRef('customerMapWrap');
        this.recentLeadsContainer = useRef('recentLeadsContainer');

        // Leaflet map instance
        this._leafletMap = null;

        // Filter refs
        this.dateFrom = useRef('dateFrom');
        this.dateTo = useRef('dateTo');
        this.userId = useRef('userId');
        this.teamId = useRef('teamId');
        this.stateSelect = useRef('stateSelect');
        this.partnerId = useRef('partnerId');

        this._charts = {};

        onMounted(async () => {
            await this._loadFilters();
            await this._loadData();
        });

        onWillUnmount(() => this._destroyCharts());
    }

    // ── Currency formatting ───────────────────────────────────────────────────
    _fmtCurrency(n) {
        const sym = this._currencySymbol || '$';
        const pos = this._currencyPosition || 'before';
        const val = (() => {
            if (n >= 1_000_000) return (n / 1_000_000).toFixed(2) + 'M';
            if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K';
            return Math.round(n).toLocaleString();
        })();
        return pos === 'before' ? `${sym}${val}` : `${val} ${sym}`;
    }

    _fmtCurrencyFull(n) {
        const sym = this._currencySymbol || '$';
        const pos = this._currencyPosition || 'before';
        const val = Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        return pos === 'before' ? `${sym}${val}` : `${val} ${sym}`;
    }

    // OWL template helpers
    formatCur(val) { return this._fmtCurrency(Number(val) || 0); }
    formatNum(val) {
        const n = Number(val) || 0;
        if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
        if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K';
        return String(Math.round(n));
    }

    // ── Filter helpers ────────────────────────────────────────────────────────
    get _filters() {
        return {
            date_from: this.dateFrom.el?.value || this.state.dateFrom,
            date_to: this.dateTo.el?.value || this.state.dateTo,
            user_id: this.userId.el?.value || '',
            team_id: this.teamId.el?.value || '',
            state: this.stateSelect.el?.value || '',
            product_ids: null,
            partner_id: this.partnerId.el?.value || '',
        };
    }

    // ── Data loading ─────────────────────────────────────────────────────────
    async _loadFilters() {
        try {
            const res = await jsonrpc('/sales_dashboard/filters', {});
            this.state.users = res.users || [];
            this.state.teams = res.teams || [];
            this.state.products = res.products || [];
            this.state.partners = res.partners || [];
            this.state.states = res.states || [];
        } catch (e) { console.warn('Sales: filter load failed', e); }
    }

    async _loadData() {
        this.state.loading = true;
        this._destroyCharts();
        try {
            const f = this._filters;
            const data = await jsonrpc('/sales_dashboard/data', {
                date_from: f.date_from,
                date_to: f.date_to,
                user_id: f.user_id || null,
                team_id: f.team_id || null,
                state: f.state || null,
                product_ids: null,
                partner_id: f.partner_id || null,
            });
            // Store currency info from data
            if (data.currency) {
                this._currencySymbol = data.currency.symbol || '$';
                this._currencyPosition = data.currency.position || 'before';
            }
            this.state.data = data;
            this.state.loading = false;
            setTimeout(() => this._renderAll(), 60);
        } catch (e) {
            console.error('Sales: data load failed', e);
            this.state.loading = false;
        }
    }

    // ── Filters ──────────────────────────────────────────────────────────────
    async applyFilters() { await this._loadData(); }

    async resetFilters() {
        const { from, to } = defaultDates();
        if (this.dateFrom.el) this.dateFrom.el.value = from;
        if (this.dateTo.el) this.dateTo.el.value = to;
        if (this.userId.el) this.userId.el.value = '';
        if (this.teamId.el) this.teamId.el.value = '';
        if (this.stateSelect.el) this.stateSelect.el.value = '';
        if (this.partnerId.el) this.partnerId.el.value = '';
        await this._loadData();
    }

    exportExcel() {
        const f = this._filters;
        let url = `/sales_dashboard/export_excel?`;
        if (f.date_from) url += `date_from=${f.date_from}&`;
        if (f.date_to) url += `date_to=${f.date_to}&`;
        if (f.user_id) url += `user_id=${f.user_id}&`;
        if (f.state) url += `state=${f.state}&`;
        if (f.partner_id) url += `partner_id=${f.partner_id}&`;
        window.open(url, '_blank');
    }

    exportPDF() {
        const f = this._filters;
        let url = `/sales-dashboard/print-pdf?`;
        if (f.date_from) url += `date_from=${f.date_from}&`;
        if (f.date_to) url += `date_to=${f.date_to}&`;
        if (f.user_id) url += `user_id=${f.user_id}&`;
        if (f.state) url += `state=${f.state}&`;
        if (f.partner_id) url += `partner_id=${f.partner_id}&`;
        window.open(url, '_blank');
    }

    shareDashboard() { this.state.showShareModal = true; }
    closeShareModal() { this.state.showShareModal = false; }

    getDashboardUrl() {
        const f = this._filters;
        let url = window.location.origin + '/sales-dashboard?';
        if (f.date_from) url += `date_from=${f.date_from}&`;
        if (f.date_to) url += `date_to=${f.date_to}&`;
        if (f.user_id) url += `user_id=${f.user_id}&`;
        if (f.state) url += `state=${f.state}&`;
        if (f.partner_id) url += `partner_id=${f.partner_id}&`;
        return url.endsWith('&') || url.endsWith('?') ? url.slice(0, -1) : url;
    }

    getQrCodeUrl() {
        return `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(this.getDashboardUrl())}`;
    }

    copyDashboardUrl() {
        const input = document.getElementById('sales-share-url-input');
        if (input) {
            input.select();
            navigator.clipboard.writeText(input.value).catch(() => { });
            this.env.services.notification.add('Dashboard URL copied!', { type: 'success' });
        }
    }

    getWhatsAppUrl() {
        return `https://api.whatsapp.com/send?text=${encodeURIComponent('Check out the Sales Dashboard: ' + this.getDashboardUrl())}`;
    }
    getTwitterUrl() {
        return `https://twitter.com/intent/tweet?url=${encodeURIComponent(this.getDashboardUrl())}&text=${encodeURIComponent('Sales 360 Dashboard!')}`;
    }
    getLinkedInUrl() {
        return `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(this.getDashboardUrl())}`;
    }
    getEmailShareHref() {
        return `mailto:?subject=${encodeURIComponent('Sales Dashboard Report')}&body=${encodeURIComponent('Check out the Sales Dashboard: ' + this.getDashboardUrl())}`;
    }

    // ── Order Drilldown ───────────────────────────────────────────────────────
    async openOrdersFiltered(stateFilter) {
        let domain = [];
        const f = this._filters;
        if (f.date_from) domain.push(['date_order', '>=', f.date_from + ' 00:00:00']);
        if (f.date_to) domain.push(['date_order', '<=', f.date_to + ' 23:59:59']);
        if (f.user_id) domain.push(['user_id', '=', parseInt(f.user_id)]);
        if (stateFilter && stateFilter !== 'all') domain.push(['state', '=', stateFilter]);

        const names = {
            sale: 'Confirmed Sales Orders', draft: 'Quotations',
            done: 'Locked Orders', cancel: 'Cancelled Orders', all: 'All Sales Orders',
        };
        await this.action.doAction({
            name: names[stateFilter] || 'Sales Orders',
            type: 'ir.actions.act_window',
            res_model: 'sale.order',
            view_mode: 'list,kanban,form',
            views: [[false, 'list'], [false, 'kanban'], [false, 'form']],
            domain,
            target: 'current',
        });
    }

    // ── Destroy charts ────────────────────────────────────────────────────────
    _destroyCharts() {
        Object.values(this._charts).forEach(c => { try { c.destroy(); } catch { } });
        this._charts = {};
        if (this._leafletMap) {
            try { this._leafletMap.remove(); } catch { }
            this._leafletMap = null;
        }
    }

    hasAnalyticalData() {
        const d = this.state.data;
        if (!d) return false;
        return (d.total_revenue > 0 || d.quotation_value > 0 || d.products_sold_qty > 0);
    }

    // ── Render all ────────────────────────────────────────────────────────────
    _renderAll() {
        const d = this.state.data;
        if (!d) return;
        if (this.hasAnalyticalData()) {
            this._renderRevenueTrend(d.revenue_trend);
            this._renderSalesperson(d.salesperson);
            this._renderCustomerMap(d.customer_map);
            this._renderStageDonut(d.stage_donut);
            this._renderTopProducts(d.top_products);
            this._renderCategoryPie(d.category_pie);
            this._renderFunnel(d.funnel);
        }
        this._renderRecentOrders(d.recent_orders);
    }

    // ── Revenue Trend Line ────────────────────────────────────────────────────
    _renderRevenueTrend(data) {
        const canvas = this.revenueTrendChart.el;
        if (!canvas || !data?.labels?.length) return;
        const ctx = canvas.getContext('2d');
        const grad = makeGradient(ctx, '#6366f1', 0.2, 0.001);
        const sym = this._currencySymbol;
        const pos = this._currencyPosition;
        const fmtTick = v => pos === 'before' ? `${sym}${fmtNum(v)}` : `${fmtNum(v)}${sym}`;
        const fmtTip = v => pos === 'before' ? ` ${sym}${Number(v).toLocaleString()}` : ` ${Number(v).toLocaleString()} ${sym}`;
        this._charts.rev = new Chart(canvas, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Sales Revenue',
                    data: data.values,
                    borderColor: '#6366f1',
                    backgroundColor: grad,
                    borderWidth: 2,
                    pointBackgroundColor: '#6366f1',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 1.5,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    fill: true,
                    tension: 0.4,
                }],
            },
            options: {
                ...CD,
                scales: {
                    x: {
                        grid: { display: false },
                        border: { display: false },
                        ticks: { color: '#64748b', font: { family: 'Inter', size: 10 } }
                    },
                    y: {
                        grid: { color: 'rgba(99, 102, 241, 0.04)', borderDash: [4, 4] },
                        border: { display: false },
                        ticks: { color: '#64748b', font: { family: 'Inter', size: 10 }, callback: fmtTick }
                    },
                },
                plugins: {
                    ...CD.plugins, legend: { display: false },
                    tooltip: { ...CD.plugins.tooltip, callbacks: { label: c => fmtTip(c.raw) } }
                },
            },
        });
    }

    // ── Stage Donut (Order Status) ────────────────────────────────────────────
    _renderStageDonut(data) {
        const canvas = this.stageDonutChart.el;
        if (!canvas || !data?.labels?.length) return;
        this._charts.stageDnt = new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{ data: data.values, backgroundColor: data.colors || PALETTE, borderWidth: 0, hoverOffset: 8 }],
            },
            options: {
                ...CD, cutout: '65%',
                plugins: {
                    ...CD.plugins, legend: { ...CD.plugins.legend, position: 'bottom' },
                    tooltip: { ...CD.plugins.tooltip, callbacks: { label: c => ` ${c.label}: ${c.raw}` } }
                },
            },
        });
    }

    // ── Funnel (Pipeline) ─────────────────────────────────────────────────────
    _renderFunnel(data) {
        const wrap = this.funnelWrap.el;
        if (!wrap || !data?.labels?.length) return;
        wrap.innerHTML = '';

        const max = Math.max(...data.values, 1);
        const totalOrders = data.values[0] || max;
        const container = Object.assign(document.createElement('div'), { className: 'sales-funnel-container' });

        const N = data.labels.length;
        const slopeStep = N > 1 ? 25 / (N - 1) : 0;

        data.labels.forEach((label, i) => {
            const val = data.values[i] || 0;
            const pctOfMax = Math.round((val / max) * 100);
            const pctOfTotal = Math.round((val / totalOrders) * 100);
            const color = data.colors?.[i] || PALETTE[i % PALETTE.length];

            const topSlope = i * slopeStep;
            const bottomSlope = (i + 1) * slopeStep;
            const clipPath = `polygon(${topSlope}% 0%, ${100 - topSlope}% 0%, ${100 - bottomSlope}% 100%, ${bottomSlope}% 100%)`;

            const row = Object.assign(document.createElement('div'), { className: 'sales-funnel-row' });
            const lbl = Object.assign(document.createElement('div'), { className: 'sales-funnel-label-col', title: label, textContent: label });

            const shapeCol = Object.assign(document.createElement('div'), { className: 'sales-funnel-shape-col' });
            const block = Object.assign(document.createElement('div'), { className: 'sales-funnel-stage-block' });
            block.style.cssText = `
                clip-path: ${clipPath};
                -webkit-clip-path: ${clipPath};
                background: linear-gradient(180deg, ${color}dd, ${color}99);
            `;
            block.title = `${label}: ${val} (${pctOfTotal}%)`;

            const blockTxt = Object.assign(document.createElement('span'), {
                className: 'sales-funnel-block-txt',
                textContent: val > 0 ? `${pctOfMax}%` : ''
            });
            block.appendChild(blockTxt);
            shapeCol.appendChild(block);

            const valCol = Object.assign(document.createElement('div'), { className: 'sales-funnel-value-col' });
            valCol.innerHTML = `${val.toLocaleString()} <span>(${pctOfTotal}%)</span>`;

            row.append(lbl, shapeCol, valCol);
            container.appendChild(row);

            if (i < N - 1) {
                const nextVal = data.values[i + 1] || 0;
                const convRate = val > 0 ? Math.round((nextVal / val) * 100) : 0;
                const conn = Object.assign(document.createElement('div'), { className: 'sales-funnel-connector' });
                conn.innerHTML = `<i class="fa fa-chevron-down"></i> <span>${convRate}% Conversion</span>`;
                container.appendChild(conn);
            }
        });

        wrap.appendChild(container);
    }

    // ── Salesperson Bar ───────────────────────────────────────────────────────
    _renderSalesperson(data) {
        const canvas = this.salespersonChart.el;
        if (!canvas || !data?.labels?.length) return;
        const cols = data.labels.map((_, i) => PALETTE[i % PALETTE.length]);
        const sym = this._currencySymbol;
        const pos = this._currencyPosition;
        const fmtTick = v => pos === 'before' ? `${sym}${fmtNum(v)}` : `${fmtNum(v)}${sym}`;
        const fmtTip = v => pos === 'before' ? ` ${sym}${Number(v).toLocaleString()}` : ` ${Number(v).toLocaleString()} ${sym}`;
        this._charts.sales = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{ label: 'Sales Amount', data: data.values, backgroundColor: cols.map(c => c + 'bb'), borderColor: cols, borderWidth: 1.5, borderRadius: 6, borderSkipped: false }],
            },
            options: {
                ...CD,
                indexAxis: 'y',
                scales: {
                    x: { ...SCALE_X, beginAtZero: true, ticks: { ...SCALE_X.ticks, callback: fmtTick } },
                    y: { grid: { display: false }, ticks: { color: '#64748b', font: { family: 'Inter', size: 10, weight: '600' } } },
                },
                plugins: {
                    ...CD.plugins,
                    legend: { display: false },
                    tooltip: { ...CD.plugins.tooltip, callbacks: { label: c => fmtTip(c.raw) } }
                },
            },
        });
    }

    // ── Recent Orders List View (HTML) ────────────────────────────────────────
    _renderRecentOrders(data) {
        const container = this.recentLeadsContainer.el;
        if (!container) return;
        if (!data?.length) {
            container.innerHTML = '<div class="crm-empty-state"><i class="fa fa-list"></i><p>No recent orders</p></div>';
            return;
        }
        const sym = this._currencySymbol;
        const pos = this._currencyPosition;
        const fmtAmt = v => {
            if (!v || v === 0) return '—';
            const val = Number(v).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 });
            return pos === 'before' ? `${sym}${val}` : `${val} ${sym}`;
        };
        let html = `<div class="crm-list-scroll"><table class="crm-list-table">
            <thead><tr>
                <th>#</th><th>Order</th><th>Customer</th>
                <th>Salesperson</th><th>Amount</th><th>Date</th><th>Status</th>
            </tr></thead><tbody>`;
        data.forEach((order, i) => {
            const sClass = order.state === 'sale' ? 'crm-badge-won' : order.state === 'cancel' ? 'crm-badge-lost' : 'crm-badge-open';
            const sLabel = order.state === 'sale' ? '✓ Confirmed' : order.state === 'cancel' ? '✗ Cancelled' : '● Quotation';
            const amt = fmtAmt(order.amount_total);
            html += `<tr class="crm-list-row" data-id="${order.id}">
                <td class="crm-list-num">${i + 1}</td>
                <td class="crm-lead-name" title="${order.name}">${order.name}</td>
                <td class="crm-lead-partner">${order.partner || '—'}</td>
                <td class="crm-lead-user">${order.user || '—'}</td>
                <td class="crm-lead-revenue">${amt}</td>
                <td class="crm-lead-date">${order.date}</td>
                <td><span class="${sClass}">${sLabel}</span></td>
            </tr>`;
        });
        html += '</tbody></table></div>';
        container.innerHTML = html;
        container.querySelectorAll('.crm-list-row').forEach(row => {
            row.addEventListener('click', () => this._openOrderForm(parseInt(row.dataset.id)));
        });
    }

    async _openOrderForm(id) {
        if (!id) return;
        await this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'sale.order',
            res_id: id,
            views: [[false, 'form']],
            target: 'current',
        });
    }

    // ── Customer World Map (Leaflet.js) ───────────────────────────────────────
    async _renderCustomerMap(data) {
        const wrap = this.customerMapWrap.el;
        if (!wrap) return;

        if (!window.L) {
            await new Promise((resolve, reject) => {
                if (!document.getElementById('leaflet-css')) {
                    const link = document.createElement('link');
                    link.id = 'leaflet-css';
                    link.rel = 'stylesheet';
                    link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
                    document.head.appendChild(link);
                }
                if (!document.getElementById('leaflet-js')) {
                    const script = document.createElement('script');
                    script.id = 'leaflet-js';
                    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
                    script.onload = resolve;
                    script.onerror = reject;
                    document.head.appendChild(script);
                } else {
                    resolve();
                }
            });
        }

        const L = window.L;
        if (!L) return;

        if (this._leafletMap) {
            try { this._leafletMap.remove(); } catch { }
            this._leafletMap = null;
        }
        wrap.innerHTML = '';

        const map = L.map(wrap, {
            center: [20, 10],
            zoom: 2,
            zoomControl: true,
            attributionControl: false,
            scrollWheelZoom: false,
        });
        this._leafletMap = map;

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
            opacity: 0.55,
        }).addTo(map);

        if (!data || !data.length) return;

        const sym = this._currencySymbol;
        const pos = this._currencyPosition;
        const fmtRev = v => pos === 'before' ? `${sym}${Number(v).toLocaleString()}` : `${Number(v).toLocaleString()} ${sym}`;
        const maxOrders = Math.max(...data.map(d => d.orders), 1);

        data.forEach(item => {
            if (!item.lat && !item.lng) return;
            const radius = 8 + (item.orders / maxOrders) * 28;
            const color = item.revenue > 100000 ? '#a855f7' :
                item.revenue > 10000 ? '#6366f1' :
                    item.revenue > 1000 ? '#3b82f6' : '#ec4899';

            const circle = L.circleMarker([item.lat, item.lng], {
                radius, fillColor: color, color: '#fff',
                weight: 1.5, opacity: 1, fillOpacity: 0.75,
            }).addTo(map);

            circle.bindPopup(`
                <div style="font-family:Inter,sans-serif;font-size:11px;min-width:130px;">
                    <strong style="font-size:13px;color:#4f46e5;display:block;margin-bottom:4px;">${item.country}</strong>
                    <div>📦 <b>${item.orders}</b> Orders</div>
                    <div>💰 <b>${fmtRev(item.revenue)}</b> Revenue</div>
                </div>
            `, { maxWidth: 200 });
        });
    }

    // ── Top Products Bar ───────────────────────────────────────────────────────
    _renderTopProducts(data) {
        const canvas = this.topProductsChart.el;
        if (!canvas || !data?.labels?.length) return;
        const cols = data.labels.map((_, i) => PALETTE[i % PALETTE.length]);
        const sym = this._currencySymbol;
        const pos = this._currencyPosition;
        const fmtTick = v => pos === 'before' ? `${sym}${fmtNum(v)}` : `${fmtNum(v)}${sym}`;
        const fmtTip = v => pos === 'before' ? ` ${sym}${Number(v).toLocaleString()}` : ` ${Number(v).toLocaleString()} ${sym}`;
        this._charts.topProd = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Revenue',
                    data: data.values,
                    backgroundColor: cols.map(c => c + 'cc'),
                    borderColor: cols,
                    borderWidth: 1.5,
                    borderRadius: 6,
                    borderSkipped: false,
                }],
            },
            options: {
                ...CD,
                indexAxis: 'y',
                scales: {
                    x: { ...SCALE_X, beginAtZero: true, ticks: { ...SCALE_X.ticks, callback: fmtTick } },
                    y: { grid: { display: false }, ticks: { color: '#64748b', font: { family: 'Inter', size: 9, weight: '600' } } },
                },
                plugins: {
                    ...CD.plugins,
                    legend: { display: false },
                    tooltip: { ...CD.plugins.tooltip, callbacks: { label: c => fmtTip(c.raw) } }
                },
            },
        });
    }

    // ── Category Pie Chart ─────────────────────────────────────────────────────
    _renderCategoryPie(data) {
        const canvas = this.categoryPieChart.el;
        if (!canvas || !data?.labels?.length) return;
        this._charts.catPie = new Chart(canvas, {
            type: 'pie',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: PALETTE,
                    borderWidth: 1,
                    borderColor: '#fff',
                }],
            },
            options: {
                ...CD,
                plugins: {
                    ...CD.plugins,
                    legend: { ...CD.plugins.legend, position: 'bottom' },
                    tooltip: {
                        ...CD.plugins.tooltip,
                        callbacks: {
                            label: c => ` ${c.label}: ${this.formatCur(c.raw)}`
                        }
                    }
                },
            },
        });
    }
}

// ── Register ─────────────────────────────────────────────────────────────────
registry.category('actions').add('sales_dashboard_pro', SalesDashboard);
