# 📊 Market Radar 360° 

## O projekcie

**Market Radar 360°** to statyczna aplikacja webowa do monitorowania i analizy rynku finansowego, agregująca dane z wielu źródeł:

- 🏛️ **Transakcje polityków USA** (Congress/Senate)
- 💰 **Portfele funduszy 13F** (Burry, Berkshire, Bridgewater i inne)
- 🔍 **Insider trading** (Form 4)
- 📈 **Wskaźniki makroekonomiczne** (krzywa dochodowości, VIX, DXY, surowce)
- 💸 **Przepływy kapitału** (ETF flows, opcje)
- 😱 **Sentyment rynkowy** (Fear & Greed Index)
- 🚨 **System alertów** bazujący na regułach

## Architektura

### Frontend
- **Statyczna strona HTML/JS/CSS** hostowana na GitHub Pages
- Odczyt danych z plików JSON w `/data/`
- Interaktywne tabele, filtry, wykresy
- Watchlista użytkownika (localStorage)
- Responsywny design (mobile-first)

### Backend (GitHub Actions)
- **Automatyczne pobieranie danych** z zewnętrznych źródeł (cron)
- **Normalizacja i walidacja** danych wg schematów JSON
- **Przetwarzanie offline** - klucze API w GitHub Secrets
- **Publikacja** zaktualizowanych danych do GitHub Pages

### Bezpieczeństwo
- ✅ Klucze API przechowywane w GitHub Secrets
- ✅ Frontend nie ma dostępu do sekretów
- ✅ Wszystkie zapytania wykonywane przez GitHub Actions
- ✅ Publikowane tylko przetworzone dane JSON

## Struktura katalogów

```
market-radar-360/
├── index.html              # Główna strona dashboardu
├── css/
│   └── styles.css          # Stylizacja
├── js/
│   ├── app.js              # Główna logika aplikacji
│   ├── data-loader.js      # Ładowanie danych z JSON
│   ├── filters.js          # Filtry i sortowanie
│   ├── charts.js           # Wykresy
│   └── alerts.js           # System alertów
├── data/                   # Dane JSON (generowane przez Actions)
│   ├── congress/
│   │   └── all.json
│   ├── funds/
│   │   ├── scion.json
│   │   ├── berkshire.json
│   │   └── ...
│   ├── insiders/
│   │   └── latest.json
│   ├── macro/
│   │   └── indicators.json
│   ├── flows/
│   │   └── etf_flows.json
│   └── sentiment/
│       └── fear_greed.json
├── config/                 # Konfiguracja
│   ├── sources.json        # Źródła danych
│   ├── rules.json          # Reguły alertów
│   └── schemas/            # Schematy walidacji JSON
├── scripts/                # Skrypty Python dla GitHub Actions
│   ├── fetch_congress.py
│   ├── fetch_13f.py
│   ├── fetch_insiders.py
│   ├── fetch_macro.py
│   ├── fetch_flows.py
│   ├── fetch_sentiment.py
│   └── utils.py
├── .github/
│   └── workflows/          # GitHub Actions workflows
│       ├── fetch-congress.yml
│       ├── fetch-13f.yml
│       ├── fetch-insiders.yml
│       ├── fetch-macro.yml
│       ├── fetch-flows.yml
│       ├── fetch-sentiment.yml
│       └── deploy.yml
└── docs/                   # Dokumentacja
```

## Źródła danych

### Congress (Politycy)
- **House**: House Stock Watcher (publiczne JSON)
- **Senate**: Senate Stock Watcher (publiczne JSON)
- **Częstotliwość**: Co 30-60 min
- **Dane**: Osoba, izba, ticker, sektor, typ transakcji, kwota, data

### Fundusze 13F
- **Źródło**: SEC EDGAR API
- **Fundusze**: Scion (Burry), Berkshire, Bridgewater, Pershing Square, Third Point, ARK
- **Częstotliwość**: Raz dziennie
- **Dane**: Ticker, liczba akcji, wartość, zmiana QoQ

### Insiders (Form 4)
- **Źródło**: SEC EDGAR Form 4
- **Częstotliwość**: Co 30-60 min
- **Dane**: Insider, firma, ticker, liczba akcji, cena, typ transakcji

### Makroekonomia
- **Źródła**: FRED API, Yahoo Finance
- **Wskaźniki**: US2Y, US10Y, spread 2s10s, DXY, VIX, złoto, ropa, miedź
- **Częstotliwość**: Co 15-60 min (w godzinach rynkowych)

### Flow (Przepływy kapitału)
- **Dane**: ETF inflows/outflows, wolumen opcji, open interest
- **Częstotliwość**: Co 30-60 min

### Sentyment
- **Źródła**: AAII, syntetyczny Fear & Greed Index
- **Częstotliwość**: 1-2 razy dziennie

## Funkcje UI

### 🎯 Dashboard (strona główna)
- Ostatnie transakcje polityków
- Największe zmiany w 13F
- Kluczowe wskaźniki makro
- Aktywne alerty
- Sygnały "High Priority"

### 🏛️ Sekcja Kongres
- Tabela z filtrami: osoba, izba, ticker, sektor, typ, wartość, data
- Widok szczegółowy polityka
- Statystyki: liczba transakcji, sektory

### 💰 Sekcja Fundusze 13F
- Lista funduszy
- Skład portfela
- Zmiany QoQ
- Heatmapa sektorów

### 🔍 Sekcja Insiderzy
- Ostatnie transakcje Form 4
- Filtry: tylko zakupy, minimalna wartość
- Historia dla wybranych tickerów

### 📈 Sekcja Makro
- Wykresy czasowe dla wszystkich wskaźników
- Kolorowane progi alarmowe
- Historia 30/90/180 dni

### 💸 Sekcja Flow
- Napływy/odpływy ETF
- Top opcje (OI/volume)
- Wykrywanie anomalii

### 😱 Sekcja Sentyment
- AAII Bull/Bear spread
- Fear & Greed Index
- Historia ekstremów

### ⭐ Watchlista
- Zapisywana w localStorage
- Dodawanie tickerów, polityków, funduszy
- Przefiltrowane widoki

## Konfiguracja GitHub Actions

### Wymagane Secrets

Dodaj w Settings → Secrets and variables → Actions:

- `FRED_API_KEY` - klucz do FRED API (opcjonalny, jeśli używasz Yahoo)
- `SEC_EDGAR_USER_AGENT` - User-Agent dla SEC EDGAR (wymagane przez SEC)

### Harmonogram

| Workflow | Częstotliwość | Opis |
|----------|---------------|------|
| fetch-congress | */30 * * * * | Co 30 min |
| fetch-13f | 0 8 * * * | Raz dziennie (8:00 UTC) |
| fetch-insiders | */30 * * * * | Co 30 min |
| fetch-macro | */15 13-21 * * 1-5 | Co 15 min (godz. rynkowe USA) |
| fetch-flows | */30 * * * * | Co 30 min |
| fetch-sentiment | 0 */12 * * * | 2 razy dziennie |
| deploy | on push to main | Po każdym push |

## Instalacja i deployment

### 1. Fork/Clone repozytorium

```bash
git clone https://github.com/twoje-username/market-radar-360.git
cd market-radar-360
```

### 2. Skonfiguruj GitHub Secrets

- Przejdź do Settings → Secrets and variables → Actions
- Dodaj wymagane klucze API

### 3. Włącz GitHub Actions

- Przejdź do zakładki Actions
- Włącz workflows

### 4. Włącz GitHub Pages

- Settings → Pages
- Source: Deploy from a branch
- Branch: `gh-pages` (zostanie utworzona automatycznie przez workflow)
- Folder: `/ (root)`

### 5. Uruchom pierwszy workflow manualnie

- Przejdź do Actions
- Wybierz workflow "Deploy to GitHub Pages"
- Kliknij "Run workflow"

Strona będzie dostępna pod: `https://twoje-username.github.io/market-radar-360/`

## Rozwój lokalny

### Wymagania
- Python 3.9+
- Node.js (opcjonalnie, dla serwera dev)

### Instalacja zależności Python

```bash
pip install -r requirements.txt
```

### Uruchomienie lokalnego serwera

```bash
python -m http.server 8000
```

Otwórz: http://localhost:8000

### Testowanie skryptów

```bash
# Testuj pojedynczy skrypt
python scripts/fetch_congress.py

# Sprawdź walidację
python scripts/utils.py validate data/congress/all.json config/schemas/congress.json
```

## Ograniczenia i disclaimer

⚠️ **WAŻNE INFORMACJE:**

1. **Opóźnienia danych**: Transakcje polityków mają opóźnienia ustawowe (STOCK Act - do 45 dni)
2. **Tylko informacyjne**: Dane służą wyłącznie celom edukacyjnym i informacyjnym
3. **Nie stanowi porady**: To NIE jest porada inwestycyjna
4. **Dane "as-is"**: Dane prezentowane bez gwarancji dokładności
5. **Limity API**: Respektuj limity rate-limit źródeł danych
6. **SEC EDGAR**: Wymaga User-Agent (zgodnie z wytycznymi SEC)

## Technologie

- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Wykresy**: Chart.js
- **Backend**: Python 3.9+, GitHub Actions
- **Hosting**: GitHub Pages
- **API**: SEC EDGAR, FRED, Yahoo Finance

## Roadmap

- [ ] Dodanie RSS feed z alertami
- [ ] Email notifications przez GitHub Actions
- [ ] Eksport danych do CSV
- [ ] Dark mode
- [ ] PWA (Progressive Web App)
- [ ] Więcej funduszy 13F
- [ ] Analiza korelacji
- [ ] Backtesting strategii

## Contributing

Pull requesty mile widziane! Dla większych zmian proszę najpierw otworzyć issue.

## Licencja

MIT License - zobacz plik LICENSE

## Autor

Market Radar 360° © 2025

---

**⚠️ Disclaimer**: Ten projekt służy wyłącznie celom edukacyjnym. Nie stanowi porady inwestycyjnej, finansowej ani prawnej. Zawsze przeprowadzaj własne badania (DYOR) przed podjęciem decyzji inwestycyjnych.
