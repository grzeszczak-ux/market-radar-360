/**
 * Moduł ładowania danych z plików JSON
 */

class DataLoader {
    constructor() {
        this.cache = {};
        this.baseUrl = window.location.hostname === 'localhost' ? '' : '';
    }

    /**
     * Ładuje dane z pliku JSON
     */
    async loadJSON(path) {
        // Sprawdź cache
        if (this.cache[path]) {
            console.log(`✓ Loaded from cache: ${path}`);
            return this.cache[path];
        }

        try {
            const response = await fetch(this.baseUrl + path);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            // Zapisz w cache
            this.cache[path] = data;
            console.log(`✓ Loaded: ${path}`);
            return data;
        } catch (error) {
            console.error(`✗ Error loading ${path}:`, error);
            return null;
        }
    }

    /**
     * Ładuje dane Kongresu
     */
    async loadCongressData() {
        return await this.loadJSON('data/congress/all.json');
    }

    /**
     * Ładuje dane funduszy 13F
     */
    async loadFundsData() {
        const fundSlugs = ['scion', 'berkshire', 'bridgewater', 'pershing', 'third', 'ark'];
        const fundsData = {};

        for (const slug of fundSlugs) {
            const data = await this.loadJSON(`data/funds/${slug}.json`);
            if (data) {
                fundsData[slug] = data;
            }
        }

        return fundsData;
    }

    /**
     * Ładuje dane insiderów
     */
    async loadInsidersData() {
        return await this.loadJSON('data/insiders/latest.json');
    }

    /**
     * Ładuje dane makro
     */
    async loadMacroData() {
        return await this.loadJSON('data/macro/indicators.json');
    }

    /**
     * Ładuje dane flows
     */
    async loadFlowsData() {
        return await this.loadJSON('data/flows/latest.json');
    }

    /**
     * Ładuje dane sentymentu
     */
    async loadSentimentData() {
        return await this.loadJSON('data/sentiment/latest.json');
    }

    /**
     * Ładuje wszystkie dane jednocześnie
     */
    async loadAllData() {
        console.log('=== Loading all data ===');
        
        const [congress, funds, insiders, macro, flows, sentiment] = await Promise.all([
            this.loadCongressData(),
            this.loadFundsData(),
            this.loadInsidersData(),
            this.loadMacroData(),
            this.loadFlowsData(),
            this.loadSentimentData()
        ]);

        const allData = {
            congress,
            funds,
            insiders,
            macro,
            flows,
            sentiment
        };

        console.log('=== All data loaded ===');
        return allData;
    }

    /**
     * Wyczyść cache
     */
    clearCache() {
        this.cache = {};
        console.log('Cache cleared');
    }

    /**
     * Odśwież wszystkie dane (czyści cache i ładuje ponownie)
     */
    async refreshAllData() {
        this.clearCache();
        return await this.loadAllData();
    }
}

// Globalna instancja
window.dataLoader = new DataLoader();
