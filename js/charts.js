/**
 * Moduł wykresów (Chart.js)
 */

class ChartManager {
    constructor() {
        this.charts = {};
    }

    /**
     * Wykres krzywej dochodowości (yields)
     */
    createYieldsChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        // Zniszcz poprzedni wykres jeśli istnieje
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const indicators = data.indicators || {};
        const yields = indicators.yields || {};

        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['2Y', '10Y', 'Spread 2s10s'],
                datasets: [{
                    label: 'Rentowność (%)',
                    data: [
                        yields.US2Y || 0,
                        yields.US10Y || 0,
                        yields.spread_2s10s || 0
                    ],
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.7)',
                        'rgba(16, 185, 129, 0.7)',
                        yields.spread_2s10s < 0 ? 'rgba(239, 68, 68, 0.7)' : 'rgba(16, 185, 129, 0.7)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    /**
     * Wykres zmienności i walut
     */
    createVolatilityChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const indicators = data.indicators || {};
        const volatility = indicators.volatility || {};
        const currencies = indicators.currencies || {};

        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['VIX', 'DXY'],
                datasets: [{
                    label: 'Wartość',
                    data: [
                        volatility.VIX || 0,
                        currencies.DXY || 0
                    ],
                    backgroundColor: [
                        'rgba(239, 68, 68, 0.7)',
                        'rgba(59, 130, 246, 0.7)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    /**
     * Wykres surowców
     */
    createCommoditiesChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const indicators = data.indicators || {};
        const commodities = indicators.commodities || {};

        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Złoto', 'Ropa', 'Miedź'],
                datasets: [{
                    label: 'Cena ($)',
                    data: [
                        commodities.gold || 0,
                        commodities.oil || 0,
                        commodities.copper || 0
                    ],
                    backgroundColor: [
                        'rgba(251, 191, 36, 0.7)',
                        'rgba(34, 34, 34, 0.7)',
                        'rgba(180, 83, 9, 0.7)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    /**
     * Wykres historyczny spreadu 2s10s
     */
    createSpreadHistoryChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        // Obliczanie historycznego spreadu z historii US2Y i US10Y
        const history = data.history || {};
        const us2yHistory = history.US2Y || [];
        const us10yHistory = history.US10Y || [];

        // Łączenie danych
        const spreadData = us2yHistory.map((item, index) => {
            const us10y = us10yHistory[index]?.value || 0;
            const us2y = item.value || 0;
            return {
                date: item.date,
                spread: us10y - us2y
            };
        }).slice(-90); // Ostatnie 90 dni

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: spreadData.map(d => d.date),
                datasets: [{
                    label: 'Spread 2s10s',
                    data: spreadData.map(d => d.spread),
                    borderColor: 'rgba(59, 130, 246, 1)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        display: false
                    }
                }
            }
        });
    }

    /**
     * Wykres AAII Sentiment
     */
    createAAIIChart(canvasId, data) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const aaii = data.aaii || {};

        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Bullish', 'Neutral', 'Bearish'],
                datasets: [{
                    data: [
                        aaii.bullish || 0,
                        aaii.neutral || 0,
                        aaii.bearish || 0
                    ],
                    backgroundColor: [
                        'rgba(16, 185, 129, 0.7)',
                        'rgba(107, 114, 128, 0.7)',
                        'rgba(239, 68, 68, 0.7)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    /**
     * Niszczy wszystkie wykresy
     */
    destroyAll() {
        Object.values(this.charts).forEach(chart => chart.destroy());
        this.charts = {};
    }
}

// Globalna instancja
window.chartManager = new ChartManager();
