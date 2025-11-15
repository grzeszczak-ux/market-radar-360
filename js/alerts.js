/**
 * Moduł systemu alertów
 */

class AlertsManager {
    constructor() {
        this.rules = null;
        this.activeAlerts = [];
    }

    /**
     * Ładuje reguły alertów
     */
    async loadRules() {
        try {
            const response = await fetch('config/rules.json');
            this.rules = await response.json();
            console.log('✓ Alert rules loaded');
        } catch (error) {
            console.error('✗ Error loading alert rules:', error);
        }
    }

    /**
     * Sprawdza alerty dla danych Kongresu
     */
    checkCongressAlerts(data) {
        if (!data || !data.transactions) return [];
        
        const alerts = [];
        const rules = this.rules?.alerts?.congress || [];

        data.transactions.forEach(transaction => {
            rules.forEach(rule => {
                let triggered = false;

                // Large trade alert
                if (rule.id === 'congress_large_trade') {
                    if (transaction.amount_min > 250000) {
                        triggered = true;
                    }
                }

                if (triggered) {
                    alerts.push({
                        id: rule.id,
                        name: rule.name,
                        priority: rule.priority,
                        description: rule.description,
                        data: transaction,
                        timestamp: new Date().toISOString()
                    });
                }
            });
        });

        return alerts;
    }

    /**
     * Sprawdza alerty dla funduszy 13F
     */
    checkFundsAlerts(fundsData) {
        if (!fundsData) return [];
        
        const alerts = [];
        const rules = this.rules?.alerts?.funds_13f || [];

        Object.entries(fundsData).forEach(([fundSlug, fundData]) => {
            if (!fundData.holdings) return;

            fundData.holdings.forEach(holding => {
                rules.forEach(rule => {
                    let triggered = false;

                    // Burry new position
                    if (rule.id === 'burry_new_position') {
                        if (fundSlug === 'scion' && holding.position_type === 'NEW') {
                            triggered = true;
                        }
                    }

                    // Large position increase
                    if (rule.id === 'large_position_increase') {
                        if (holding.change_pct > 50 && holding.value > 10000000) {
                            triggered = true;
                        }
                    }

                    if (triggered) {
                        alerts.push({
                            id: rule.id,
                            name: rule.name,
                            priority: rule.priority,
                            description: rule.description,
                            data: { ...holding, fund: fundData.fund_info.name },
                            timestamp: new Date().toISOString()
                        });
                    }
                });
            });
        });

        return alerts;
    }

    /**
     * Sprawdza alerty makro
     */
    checkMacroAlerts(data) {
        if (!data || !data.indicators) return [];
        
        const alerts = [];
        const rules = this.rules?.alerts?.macro || [];
        const indicators = data.indicators;

        rules.forEach(rule => {
            let triggered = false;
            let value = null;

            // Yield curve inversion
            if (rule.id === 'yield_curve_inversion') {
                value = indicators.yields?.spread_2s10s;
                if (value < 0) {
                    triggered = true;
                }
            }

            // VIX spike
            if (rule.id === 'vix_spike') {
                value = indicators.volatility?.VIX;
                if (value > 30) {
                    triggered = true;
                }
            }

            // VIX extreme low
            if (rule.id === 'vix_extreme_low') {
                value = indicators.volatility?.VIX;
                if (value < 12) {
                    triggered = true;
                }
            }

            if (triggered) {
                alerts.push({
                    id: rule.id,
                    name: rule.name,
                    priority: rule.priority,
                    description: rule.description,
                    data: { indicator: rule.id, value },
                    timestamp: new Date().toISOString()
                });
            }
        });

        return alerts;
    }

    /**
     * Sprawdza alerty sentymentu
     */
    checkSentimentAlerts(data) {
        if (!data || !data.fear_greed) return [];
        
        const alerts = [];
        const rules = this.rules?.alerts?.sentiment || [];
        const fearGreedIndex = data.fear_greed.index;

        rules.forEach(rule => {
            let triggered = false;

            // Extreme fear
            if (rule.id === 'extreme_fear' && fearGreedIndex < 20) {
                triggered = true;
            }

            // Extreme greed
            if (rule.id === 'extreme_greed' && fearGreedIndex > 80) {
                triggered = true;
            }

            if (triggered) {
                alerts.push({
                    id: rule.id,
                    name: rule.name,
                    priority: rule.priority,
                    description: rule.description,
                    data: { fearGreedIndex },
                    timestamp: new Date().toISOString()
                });
            }
        });

        return alerts;
    }

    /**
     * Sprawdza wszystkie alerty
     */
    async checkAllAlerts(allData) {
        await this.loadRules();

        const congressAlerts = this.checkCongressAlerts(allData.congress);
        const fundsAlerts = this.checkFundsAlerts(allData.funds);
        const macroAlerts = this.checkMacroAlerts(allData.macro);
        const sentimentAlerts = this.checkSentimentAlerts(allData.sentiment);

        this.activeAlerts = [
            ...congressAlerts,
            ...fundsAlerts,
            ...macroAlerts,
            ...sentimentAlerts
        ];

        // Sortuj po priorytecie (high first)
        this.activeAlerts.sort((a, b) => {
            const priorityOrder = { high: 1, medium: 2, low: 3 };
            return priorityOrder[a.priority] - priorityOrder[b.priority];
        });

        console.log(`✓ Found ${this.activeAlerts.length} active alerts`);
        return this.activeAlerts;
    }

    /**
     * Renderuje alerty na stronie
     */
    renderAlerts(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (this.activeAlerts.length === 0) {
            container.innerHTML = '<p class="no-alerts">✓ Brak aktywnych alertów</p>';
            return;
        }

        const html = this.activeAlerts.map(alert => `
            <div class="alert alert-${alert.priority}">
                <div class="alert-header">
                    <span class="alert-icon">${alert.priority === 'high' ? '🚨' : '⚠️'}</span>
                    <span class="alert-title">${alert.name}</span>
                    <span class="alert-priority">${alert.priority.toUpperCase()}</span>
                </div>
                <p class="alert-description">${alert.description}</p>
            </div>
        `).join('');

        container.innerHTML = html;
    }
}

// Globalna instancja
window.alertsManager = new AlertsManager();
