/**
 * Główny plik aplikacji - orkiestruje wszystkie moduły
 */

class MarketRadarApp {
    constructor() {
        this.currentSection = 'dashboard';
        this.allData = null;
        this.watchlist = Utils.storage.get('watchlist', []);
    }

    /**
     * Inicjalizacja aplikacji
     */
    async init() {
        console.log('=== Market Radar 360° Initializing ===');
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load all data
        await this.loadAllData();
        
        // Render initial view
        this.renderDashboard();
        
        console.log('=== Market Radar 360° Ready ===');
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.dataset.section;
                this.navigateToSection(section);
            });
        });

        // Widget links
        document.querySelectorAll('.widget-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.dataset.section;
                this.navigateToSection(section);
            });
        });

        // Refresh button
        document.getElementById('refreshBtn')?.addEventListener('click', () => {
            this.refreshData();
        });

        // Theme toggle
        document.getElementById('themeToggle')?.addEventListener('click', () => {
            this.toggleTheme();
        });

        // Congress filters
        document.getElementById('congressSearch')?.addEventListener('input', 
            Utils.debounce(() => this.filterCongressData(), 300)
        );
        
        document.getElementById('congressChamber')?.addEventListener('change', () => {
            this.filterCongressData();
        });
        
        document.getElementById('congressType')?.addEventListener('change', () => {
            this.filterCongressData();
        });

        // Insiders filters
        document.getElementById('insidersSearch')?.addEventListener('input',
            Utils.debounce(() => this.filterInsidersData(), 300)
        );
        
        document.getElementById('insidersType')?.addEventListener('change', () => {
            this.filterInsidersData();
        });
        
        document.getElementById('insidersMinValue')?.addEventListener('input',
            Utils.debounce(() => this.filterInsidersData(), 300)
        );

        // Watchlist
        document.getElementById('watchlistAddBtn')?.addEventListener('click', () => {
            this.addToWatchlist();
        });
    }

    /**
     * Load all data
     */
    async loadAllData() {
        try {
            Utils.showToast('Ładowanie danych...', 'info');
            this.allData = await window.dataLoader.loadAllData();
            
            // Update last update time
            this.updateLastUpdateTime();
            
            Utils.showToast('Dane załadowane pomyślnie!', 'success');
        } catch (error) {
            console.error('Error loading data:', error);
            Utils.showToast('Błąd ładowania danych', 'error');
        }
    }

    /**
     * Refresh data
     */
    async refreshData() {
        await this.loadAllData();
        this.renderCurrentSection();
        Utils.showToast('Dane odświeżone!', 'success');
    }

    /**
     * Update last update time
     */
    updateLastUpdateTime() {
        const timeElement = document.getElementById('lastUpdateTime');
        if (timeElement) {
            timeElement.textContent = Utils.formatDateTime(new Date().toISOString());
        }
    }

    /**
     * Navigate to section
     */
    navigateToSection(section) {
        // Update nav
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.toggle('active', link.dataset.section === section);
        });

        // Hide all sections
        document.querySelectorAll('.section').forEach(s => {
            s.classList.remove('active');
        });

        // Show target section
        const targetSection = document.getElementById(`${section}-section`);
        if (targetSection) {
            targetSection.classList.add('active');
            this.currentSection = section;
            this.renderCurrentSection();
        }
    }

    /**
     * Render current section
     */
    renderCurrentSection() {
        switch(this.currentSection) {
            case 'dashboard':
                this.renderDashboard();
                break;
            case 'congress':
                this.renderCongress();
                break;
            case 'funds':
                this.renderFunds();
                break;
            case 'insiders':
                this.renderInsiders();
                break;
            case 'macro':
                this.renderMacro();
                break;
            case 'flow':
                this.renderFlow();
                break;
            case 'sentiment':
                this.renderSentiment();
                break;
            case 'watchlist':
                this.renderWatchlist();
                break;
        }
    }

    /**
     * Render Dashboard
     */
    async renderDashboard() {
        if (!this.allData) return;

        // Render alerts
        const alerts = await window.alertsManager.checkAllAlerts(this.allData);
        window.alertsManager.renderAlerts('alertsContainer');

        // Render congress widget
        this.renderCongressWidget();

        // Render funds widget
        this.renderFundsWidget();

        // Render macro widget
        this.renderMacroWidget();

        // Render sentiment widget
        this.renderSentimentWidget();
    }

    /**
     * Render Congress Widget (latest transactions)
     */
    renderCongressWidget() {
        const container = document.getElementById('congressWidget');
        if (!container || !this.allData?.congress) return;

        const transactions = this.allData.congress.transactions.slice(0, 5);

        const html = transactions.map(t => `
            <div class="widget-item">
                <div class="item-header">
                    <strong>${t.person}</strong>
                    <span class="badge badge-${t.chamber.toLowerCase()}">${t.chamber}</span>
                </div>
                <div class="item-details">
                    ${Utils.getTransactionIcon(t.transaction_type)} 
                    <strong>${t.ticker}</strong> - ${t.amount_range}
                    <span class="item-date">${Utils.daysAgo(t.date)}</span>
                </div>
            </div>
        `).join('');

        container.innerHTML = html || '<p>Brak danych</p>';
    }

    /**
     * Render Funds Widget
     */
    renderFundsWidget() {
        const container = document.getElementById('fundsWidget');
        if (!container || !this.allData?.funds) return;

        container.innerHTML = '<p>Dane funduszy 13F (demo)</p>';
    }

    /**
     * Render Macro Widget
     */
    renderMacroWidget() {
        const container = document.getElementById('macroWidget');
        if (!container || !this.allData?.macro) return;

        const indicators = this.allData.macro.indicators;
        const yields = indicators.yields || {};
        const volatility = indicators.volatility || {};

        const html = `
            <div class="macro-indicators">
                <div class="indicator">
                    <span class="indicator-label">Spread 2s10s:</span>
                    <span class="indicator-value ${yields.spread_2s10s < 0 ? 'negative' : 'positive'}">
                        ${Utils.formatNumber(yields.spread_2s10s)}%
                    </span>
                </div>
                <div class="indicator">
                    <span class="indicator-label">VIX:</span>
                    <span class="indicator-value">${Utils.formatNumber(volatility.VIX)}</span>
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    /**
     * Render Sentiment Widget
     */
    renderSentimentWidget() {
        const container = document.getElementById('sentimentWidget');
        if (!container || !this.allData?.sentiment) return;

        const fearGreed = this.allData.sentiment.fear_greed;

        const html = `
            <div class="sentiment-display">
                <div class="fear-greed-score">${fearGreed.index}</div>
                <div class="fear-greed-label">${fearGreed.classification}</div>
                <div class="fear-greed-signal">${fearGreed.signal}</div>
            </div>
        `;

        container.innerHTML = html;
    }

    /**
     * Render Congress Section
     */
    renderCongress() {
        if (!this.allData?.congress) return;
        this.filterCongressData();
    }

    /**
     * Filter and render Congress data
     */
    filterCongressData() {
        const search = document.getElementById('congressSearch')?.value;
        const chamber = document.getElementById('congressChamber')?.value;
        const type = document.getElementById('congressType')?.value;

        const filtered = window.dataFilters.filterCongressTransactions(
            this.allData.congress.transactions,
            { search, chamber, type }
        );

        this.renderCongressTable(filtered);
    }

    /**
     * Render Congress Table
     */
    renderCongressTable(transactions) {
        const container = document.getElementById('congressTable');
        if (!container) return;

        if (transactions.length === 0) {
            container.innerHTML = '<p class="no-data">Brak transakcji spełniających kryteria</p>';
            return;
        }

        const html = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Osoba</th>
                        <th>Izba</th>
                        <th>Ticker</th>
                        <th>Typ</th>
                        <th>Kwota</th>
                        <th>Data</th>
                    </tr>
                </thead>
                <tbody>
                    ${transactions.slice(0, 100).map(t => `
                        <tr>
                            <td>${t.person}</td>
                            <td><span class="badge badge-${t.chamber.toLowerCase()}">${t.chamber}</span></td>
                            <td><strong>${t.ticker}</strong></td>
                            <td>${Utils.getTransactionIcon(t.transaction_type)} ${t.transaction_type}</td>
                            <td>${t.amount_range}</td>
                            <td>${Utils.formatDate(t.date)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = html;
    }

    /**
     * Render other sections (simplified)
     */
    renderFunds() {
        console.log('Rendering Funds section');
    }

    renderInsiders() {
        if (!this.allData?.insiders) return;
        this.filterInsidersData();
    }

    filterInsidersData() {
        const search = document.getElementById('insidersSearch')?.value;
        const type = document.getElementById('insidersType')?.value;
        const minValue = document.getElementById('insidersMinValue')?.value;

        const filtered = window.dataFilters.filterInsiderTransactions(
            this.allData.insiders.transactions,
            { search, type, minValue: parseFloat(minValue) || 0 }
        );

        this.renderInsidersTable(filtered);
    }

    renderInsidersTable(transactions) {
        const container = document.getElementById('insidersTable');
        if (!container) return;

        if (transactions.length === 0) {
            container.innerHTML = '<p class="no-data">Brak transakcji</p>';
            return;
        }

        const html = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Insider</th>
                        <th>Firma</th>
                        <th>Ticker</th>
                        <th>Typ</th>
                        <th>Wartość</th>
                        <th>Data</th>
                    </tr>
                </thead>
                <tbody>
                    ${transactions.slice(0, 50).map(t => `
                        <tr>
                            <td>${t.insider_name}<br><small>${t.insider_title}</small></td>
                            <td>${t.company}</td>
                            <td><strong>${t.ticker}</strong></td>
                            <td>${Utils.getTransactionIcon(t.transaction_type)} ${t.transaction_type}</td>
                            <td>${Utils.formatCurrency(t.value)}</td>
                            <td>${Utils.formatDate(t.date)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = html;
    }

    renderMacro() {
        if (!this.allData?.macro) return;

        // Render charts
        window.chartManager.createYieldsChart('chartYields', this.allData.macro);
        window.chartManager.createVolatilityChart('chartVolatility', this.allData.macro);
        window.chartManager.createCommoditiesChart('chartCommodities', this.allData.macro);
        window.chartManager.createSpreadHistoryChart('chartSpread', this.allData.macro);
    }

    renderFlow() {
        console.log('Rendering Flow section');
    }

    renderSentiment() {
        if (!this.allData?.sentiment) return;

        // Render Fear & Greed gauge
        this.renderFearGreedGauge();

        // Render AAII chart
        window.chartManager.createAAIIChart('chartAAII', this.allData.sentiment);
    }

    renderFearGreedGauge() {
        const container = document.getElementById('fearGreedGauge');
        if (!container || !this.allData?.sentiment) return;

        const fg = this.allData.sentiment.fear_greed;

        const html = `
            <div class="fear-greed-gauge">
                <div class="gauge-value">${fg.index}</div>
                <div class="gauge-label">${fg.classification}</div>
                <div class="gauge-signal">Signal: ${fg.signal}</div>
            </div>
        `;

        container.innerHTML = html;
    }

    renderWatchlist() {
        const container = document.getElementById('watchlistContent');
        if (!container) return;

        if (this.watchlist.length === 0) {
            container.innerHTML = '<p class="empty-state">Twoja watchlista jest pusta. Dodaj pierwsze pozycje!</p>';
            return;
        }

        const html = this.watchlist.map(item => `
            <div class="watchlist-item">
                <span>${item}</span>
                <button onclick="app.removeFromWatchlist('${item}')" class="btn-remove">✕</button>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    /**
     * Watchlist methods
     */
    addToWatchlist() {
        const input = document.getElementById('watchlistInput');
        if (!input) return;

        const value = input.value.trim();
        if (!value) return;

        if (!this.watchlist.includes(value)) {
            this.watchlist.push(value);
            Utils.storage.set('watchlist', this.watchlist);
            input.value = '';
            this.renderWatchlist();
            Utils.showToast(`Dodano "${value}" do watchlisty`, 'success');
        } else {
            Utils.showToast(`"${value}" już jest na watchliście`, 'info');
        }
    }

    removeFromWatchlist(item) {
        this.watchlist = this.watchlist.filter(i => i !== item);
        Utils.storage.set('watchlist', this.watchlist);
        this.renderWatchlist();
        Utils.showToast(`Usunięto "${item}" z watchlisty`, 'success');
    }

    /**
     * Toggle theme
     */
    toggleTheme() {
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-theme');
        Utils.storage.set('theme', isDark ? 'dark' : 'light');
        
        const icon = document.querySelector('#themeToggle span');
        if (icon) {
            icon.textContent = isDark ? '☀️' : '🌙';
        }
    }
}

// Initialize app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new MarketRadarApp();
    app.init();
});

// Make app globally accessible
window.app = app;
