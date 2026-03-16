/**
 * CryptoScope -- Client-side charts and interactions.
 *
 * Uses Chart.js for portfolio donut, price line charts, correlation
 * heatmap, gas gauge, and sparkline mini-charts.
 */

/* ---------------------------------------------------------------
   Colour palette
   --------------------------------------------------------------- */
const CS_COLORS = [
    '#8b5cf6', '#3b82f6', '#06b6d4', '#10b981', '#f59e0b',
    '#ef4444', '#ec4899', '#14b8a6', '#f97316', '#6366f1',
    '#84cc16', '#a855f7',
];

/* ---------------------------------------------------------------
   Portfolio Allocation Donut
   --------------------------------------------------------------- */
function renderAllocationChart() {
    const data = window.allocationData;
    if (!data) return;

    const labels = Object.keys(data);
    const values = Object.values(data);
    if (labels.length === 0) return;

    const ctx = document.getElementById('allocationChart');
    if (!ctx) return;

    new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: CS_COLORS.slice(0, labels.length),
                borderColor: '#0a0e17',
                borderWidth: 2,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: { color: '#e2e8f0', padding: 12, font: { size: 11 } },
                },
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            return ctx.label + ': ' + ctx.parsed.toFixed(2) + '%';
                        },
                    },
                },
            },
        },
    });
}

/* ---------------------------------------------------------------
   Price Line Chart (Market page)
   --------------------------------------------------------------- */
let priceChartInstance = null;

function loadPriceChart(symbol) {
    fetch('/api/market/history/' + symbol + '?days=90')
        .then(r => r.json())
        .then(data => {
            if (!data.history) return;
            const labels = data.history.map(h => h.date);
            const prices = data.history.map(h => h.price);
            renderPriceChart(symbol, labels, prices);
        });
}

function renderPriceChart(symbol, labels, prices) {
    const ctx = document.getElementById('priceChart');
    if (!ctx) return;

    if (priceChartInstance) priceChartInstance.destroy();

    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 350);
    gradient.addColorStop(0, 'rgba(139, 92, 246, 0.3)');
    gradient.addColorStop(1, 'rgba(139, 92, 246, 0.0)');

    priceChartInstance = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: symbol + ' Price (USD)',
                data: prices,
                borderColor: '#8b5cf6',
                backgroundColor: gradient,
                fill: true,
                tension: 0.3,
                pointRadius: 0,
                pointHoverRadius: 4,
                borderWidth: 2,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            scales: {
                x: {
                    ticks: { color: '#94a3b8', maxTicksLimit: 10 },
                    grid: { color: 'rgba(30,41,59,0.5)' },
                },
                y: {
                    ticks: {
                        color: '#94a3b8',
                        callback: v => '$' + v.toLocaleString(),
                    },
                    grid: { color: 'rgba(30,41,59,0.5)' },
                },
            },
            plugins: {
                legend: { labels: { color: '#e2e8f0' } },
                tooltip: {
                    callbacks: {
                        label: ctx => '$' + ctx.parsed.y.toLocaleString(undefined, {
                            minimumFractionDigits: 2, maximumFractionDigits: 2
                        }),
                    },
                },
            },
        },
    });
}

/* ---------------------------------------------------------------
   Correlation Heatmap
   --------------------------------------------------------------- */
function renderCorrelationChart() {
    const corrData = window.correlationData;
    if (!corrData) return;

    const ctx = document.getElementById('correlationChart');
    if (!ctx) return;

    const symbols = corrData.symbols;
    const matrix = corrData.matrix;
    const n = symbols.length;

    const canvas = ctx;
    const context = canvas.getContext('2d');
    const cellSize = 40;
    const margin = 50;
    canvas.width = margin + n * cellSize;
    canvas.height = margin + n * cellSize;

    /* Draw cells */
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
            const val = matrix[symbols[i]][symbols[j]];
            const x = margin + j * cellSize;
            const y = margin + i * cellSize;

            /* Map correlation [-1, 1] to colour */
            let r, g, b;
            if (val >= 0) {
                r = Math.round(16 + (139 - 16) * val);
                g = Math.round(185 + (92 - 185) * val);
                b = Math.round(129 + (246 - 129) * val);
            } else {
                const absVal = Math.abs(val);
                r = Math.round(16 + (239 - 16) * absVal);
                g = Math.round(185 + (68 - 185) * absVal);
                b = Math.round(129 + (68 - 129) * absVal);
            }
            context.fillStyle = 'rgb(' + r + ',' + g + ',' + b + ')';
            context.fillRect(x, y, cellSize - 1, cellSize - 1);

            /* Value text */
            context.fillStyle = '#fff';
            context.font = '10px sans-serif';
            context.textAlign = 'center';
            context.textBaseline = 'middle';
            context.fillText(val.toFixed(2), x + cellSize / 2, y + cellSize / 2);
        }
    }

    /* Row / column labels */
    context.fillStyle = '#94a3b8';
    context.font = '10px sans-serif';
    for (let i = 0; i < n; i++) {
        context.textAlign = 'right';
        context.textBaseline = 'middle';
        context.fillText(symbols[i], margin - 5, margin + i * cellSize + cellSize / 2);

        context.save();
        context.translate(margin + i * cellSize + cellSize / 2, margin - 5);
        context.rotate(-Math.PI / 4);
        context.textAlign = 'left';
        context.textBaseline = 'middle';
        context.fillText(symbols[i], 0, 0);
        context.restore();
    }
}

/* ---------------------------------------------------------------
   Gas Gauge
   --------------------------------------------------------------- */
function renderGasGauge() {
    const gasVal = window.currentGas;
    if (gasVal === undefined) return;

    const ctx = document.getElementById('gasGauge');
    if (!ctx) return;

    const canvas = ctx;
    const context = canvas.getContext('2d');
    const cx = canvas.width / 2;
    const cy = canvas.height - 20;
    const radius = 90;

    /* Background arc */
    context.beginPath();
    context.arc(cx, cy, radius, Math.PI, 2 * Math.PI, false);
    context.lineWidth = 18;
    context.strokeStyle = '#1e293b';
    context.stroke();

    /* Gradient segments: green -> yellow -> red */
    const maxGas = 100;
    const pct = Math.min(gasVal / maxGas, 1.0);
    const endAngle = Math.PI + pct * Math.PI;

    const grad = context.createLinearGradient(cx - radius, cy, cx + radius, cy);
    grad.addColorStop(0, '#10b981');
    grad.addColorStop(0.4, '#f59e0b');
    grad.addColorStop(0.7, '#ef4444');
    grad.addColorStop(1, '#dc2626');

    context.beginPath();
    context.arc(cx, cy, radius, Math.PI, endAngle, false);
    context.lineWidth = 18;
    context.lineCap = 'round';
    context.strokeStyle = grad;
    context.stroke();

    /* Needle */
    const needleAngle = Math.PI + pct * Math.PI;
    const needleLen = radius - 25;
    const nx = cx + needleLen * Math.cos(needleAngle);
    const ny = cy + needleLen * Math.sin(needleAngle);
    context.beginPath();
    context.moveTo(cx, cy);
    context.lineTo(nx, ny);
    context.lineWidth = 3;
    context.strokeStyle = '#e2e8f0';
    context.stroke();

    /* Center dot */
    context.beginPath();
    context.arc(cx, cy, 5, 0, 2 * Math.PI);
    context.fillStyle = '#8b5cf6';
    context.fill();
}

/* ---------------------------------------------------------------
   Gas History Chart
   --------------------------------------------------------------- */
function renderGasHistoryChart() {
    const history = window.gasHistory;
    if (!history || !history.length) return;

    const ctx = document.getElementById('gasHistoryChart');
    if (!ctx) return;

    const labels = history.map(h => h.date);
    const avg = history.map(h => h.avg_gas_gwei);
    const min = history.map(h => h.min_gas_gwei);
    const max = history.map(h => h.max_gas_gwei);

    new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Max Gas (Gwei)',
                    data: max,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239,68,68,0.1)',
                    fill: false,
                    tension: 0.3,
                    pointRadius: 0,
                    borderWidth: 1.5,
                },
                {
                    label: 'Avg Gas (Gwei)',
                    data: avg,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245,158,11,0.15)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    borderWidth: 2,
                },
                {
                    label: 'Min Gas (Gwei)',
                    data: min,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16,185,129,0.1)',
                    fill: false,
                    tension: 0.3,
                    pointRadius: 0,
                    borderWidth: 1.5,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            scales: {
                x: {
                    ticks: { color: '#94a3b8', maxTicksLimit: 10 },
                    grid: { color: 'rgba(30,41,59,0.5)' },
                },
                y: {
                    ticks: { color: '#94a3b8', callback: v => v.toFixed(0) + ' Gwei' },
                    grid: { color: 'rgba(30,41,59,0.5)' },
                },
            },
            plugins: {
                legend: { labels: { color: '#e2e8f0' } },
            },
        },
    });
}

/* ---------------------------------------------------------------
   Sparkline mini-charts for market page
   --------------------------------------------------------------- */
function renderSparklines() {
    const canvases = document.querySelectorAll('.cs-sparkline');
    canvases.forEach(canvas => {
        const symbol = canvas.dataset.symbol;
        if (!symbol) return;

        fetch('/api/market/history/' + symbol + '?days=7')
            .then(r => r.json())
            .then(data => {
                if (!data.history || data.history.length < 2) return;
                const prices = data.history.map(h => h.price);
                const ctx = canvas.getContext('2d');
                const w = canvas.width;
                const h = canvas.height;
                const mn = Math.min(...prices);
                const mx = Math.max(...prices);
                const range = mx - mn || 1;

                const isUp = prices[prices.length - 1] >= prices[0];
                ctx.strokeStyle = isUp ? '#10b981' : '#ef4444';
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                prices.forEach((p, i) => {
                    const x = (i / (prices.length - 1)) * w;
                    const y = h - ((p - mn) / range) * (h - 4) - 2;
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                });
                ctx.stroke();
            });
    });
}

/* ---------------------------------------------------------------
   Wallet creation
   --------------------------------------------------------------- */
function createWallet() {
    const name = document.getElementById('walletName').value || 'My Wallet';
    const network = document.getElementById('walletNetwork').value || 'ethereum';

    fetch('/api/wallets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name, network: network }),
    })
    .then(r => r.json())
    .then(() => { window.location.reload(); });
}

/* ---------------------------------------------------------------
   Initialisation
   --------------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', function() {
    renderAllocationChart();
    renderCorrelationChart();
    renderGasGauge();
    renderGasHistoryChart();
    renderSparklines();

    /* Auto-load first token price chart */
    const chartSelect = document.getElementById('chartSymbol');
    if (chartSelect && chartSelect.value) {
        loadPriceChart(chartSelect.value);
    }
});
