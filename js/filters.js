/**
 * Moduł filtrowania i sortowania danych
 */

class DataFilters {
    constructor() {
        this.currentFilters = {};
    }

    /**
     * Filtruje transakcje Kongresu
     */
    filterCongressTransactions(transactions, filters = {}) {
        let filtered = [...transactions];

        // Filtr wyszukiwania
        if (filters.search) {
            const term = filters.search.toLowerCase();
            filtered = filtered.filter(t => 
                (t.person && t.person.toLowerCase().includes(term)) ||
                (t.ticker && t.ticker.toLowerCase().includes(term))
            );
        }

        // Filtr izby
        if (filters.chamber) {
            filtered = filtered.filter(t => t.chamber === filters.chamber);
        }

        // Filtr typu transakcji
        if (filters.type) {
            filtered = filtered.filter(t => t.transaction_type === filters.type);
        }

        // Filtr minimalnej wartości
        if (filters.minValue) {
            filtered = filtered.filter(t => 
                (t.amount_min && t.amount_min >= filters.minValue)
            );
        }

        return filtered;
    }

    /**
     * Filtruje holding funduszy 13F
     */
    filterFundHoldings(holdings, filters = {}) {
        let filtered = [...holdings];

        // Filtr wyszukiwania
        if (filters.search) {
            const term = filters.search.toLowerCase();
            filtered = filtered.filter(h => 
                (h.ticker && h.ticker.toLowerCase().includes(term)) ||
                (h.name && h.name.toLowerCase().includes(term))
            );
        }

        // Filtr typu zmiany pozycji
        if (filters.positionType) {
            filtered = filtered.filter(h => h.position_type === filters.positionType);
        }

        // Filtr minimalnej wartości
        if (filters.minValue) {
            filtered = filtered.filter(h => h.value >= filters.minValue);
        }

        return filtered;
    }

    /**
     * Filtruje transakcje insiderów
     */
    filterInsiderTransactions(transactions, filters = {}) {
        let filtered = [...transactions];

        // Filtr wyszukiwania
        if (filters.search) {
            const term = filters.search.toLowerCase();
            filtered = filtered.filter(t => 
                (t.company && t.company.toLowerCase().includes(term)) ||
                (t.ticker && t.ticker.toLowerCase().includes(term)) ||
                (t.insider_name && t.insider_name.toLowerCase().includes(term))
            );
        }

        // Filtr typu transakcji
        if (filters.type) {
            filtered = filtered.filter(t => t.transaction_type === filters.type);
        }

        // Filtr minimalnej wartości
        if (filters.minValue) {
            filtered = filtered.filter(t => 
                (t.value && t.value >= filters.minValue)
            );
        }

        return filtered;
    }

    /**
     * Sortuje dane wg właściwości
     */
    sortData(data, property, direction = 'desc') {
        return Utils.sortBy(data, property, direction);
    }

    /**
     * Paginacja danych
     */
    paginate(data, page = 1, perPage = 50) {
        const start = (page - 1) * perPage;
        const end = start + perPage;
        return {
            data: data.slice(start, end),
            totalPages: Math.ceil(data.length / perPage),
            currentPage: page,
            total: data.length
        };
    }

    /**
     * Zapisuje filtry do localStorage
     */
    saveFilters(section, filters) {
        Utils.storage.set(`filters_${section}`, filters);
    }

    /**
     * Ładuje filtry z localStorage
     */
    loadFilters(section) {
        return Utils.storage.get(`filters_${section}`, {});
    }
}

// Globalna instancja
window.dataFilters = new DataFilters();
