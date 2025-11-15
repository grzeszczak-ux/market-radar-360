# 🚀 Instrukcja wdrożenia Market Radar 360°

## Krok 1: Przygotowanie repozytorium GitHub

1. **Utwórz nowe repozytorium** na GitHub (np. `market-radar-360`)
   
2. **Skopiuj wszystkie pliki** z folderu `/workspace/market-radar-360/` do swojego repozytorium

3. **Wyślij kod do GitHub**:
   ```bash
   cd market-radar-360
   git init
   git add .
   git commit -m "Initial commit - Market Radar 360°"
   git branch -M main
   git remote add origin https://github.com/TWOJE-USERNAME/market-radar-360.git
   git push -u origin main
   ```

## Krok 2: Konfiguracja GitHub Secrets

Przejdź do: **Settings → Secrets and variables → Actions**

Dodaj następujące sekrety:

1. **SEC_EDGAR_USER_AGENT** (WYMAGANE)
   - Wartość: `Twoje-Imię Nazwisko email@example.com`
   - SEC wymaga identyfikacji użytkownika w User-Agent
   - Format: `FirstName LastName email@example.com`

2. **FRED_API_KEY** (OPCJONALNE)
   - Jeśli chcesz używać FRED API dla danych makro
   - Zarejestruj się na: https://fred.stlouisfed.org/docs/api/api_key.html

## Krok 3: Włączenie GitHub Actions

1. Przejdź do zakładki **Actions** w repozytorium
2. Kliknij **"I understand my workflows, go ahead and enable them"**
3. Workflows będą uruchamiane automatycznie według harmonogramu

### Ręczne uruchomienie workflows

Możesz uruchomić każdy workflow ręcznie:
1. Przejdź do **Actions**
2. Wybierz workflow (np. "Fetch Congress Data")
3. Kliknij **"Run workflow"** → **"Run workflow"**

## Krok 4: Włączenie GitHub Pages

1. Przejdź do **Settings → Pages**
2. W sekcji **Source**:
   - **Branch**: Wybierz `main`
   - **Folder**: Wybierz `/ (root)`
3. Kliknij **Save**

⏰ GitHub Pages potrzebuje kilku minut na wdrożenie

4. **Sprawdź status**:
   - Na dole strony Settings → Pages zobaczysz:
   - ✅ "Your site is live at https://TWOJE-USERNAME.github.io/market-radar-360/"

## Krok 5: Weryfikacja

### 1. Sprawdź Actions
- Przejdź do **Actions**
- Upewnij się, że workflows działają bez błędów
- Zielone ✅ = sukces, czerwone ❌ = błąd

### 2. Sprawdź dane
- Po uruchomieniu workflows sprawdź katalog `data/`
- Powinny pojawić się pliki JSON z danymi

### 3. Otwórz stronę
- Wejdź na: `https://TWOJE-USERNAME.github.io/market-radar-360/`
- Strona powinna załadować się z przykładowymi danymi
- Po uruchomieniu workflows dane będą aktualizowane automatycznie

## Harmonogram automatycznych aktualizacji

| Workflow | Częstotliwość | Opis |
|----------|---------------|------|
| Congress | Co 30 min | Transakcje polityków |
| 13F Funds | Raz dziennie (8:00 UTC) | Portfele funduszy |
| Insiders | Co 30 min | Form 4 insiders |
| Macro | Co 15 min (godz. rynkowe) | Wskaźniki makro |
| Flow | Co 30 min | ETF flows, opcje |
| Sentiment | 2x dziennie (6:00, 18:00 UTC) | Sentyment |

## Rozwiązywanie problemów

### Problem: Workflow kończy się błędem

**Rozwiązanie**:
1. Sprawdź logi workflow w zakładce Actions
2. Upewnij się, że SEC_EDGAR_USER_AGENT jest ustawiony
3. Sprawdź czy format User-Agent jest poprawny

### Problem: Strona nie ładuje się na GitHub Pages

**Rozwiązanie**:
1. Sprawdź czy GitHub Pages jest włączone
2. Upewnij się, że branch to `main` i folder to `/ (root)`
3. Poczekaj kilka minut - deployment trwa
4. Sprawdź czy plik `index.html` jest w root repozytorium

### Problem: Dane nie są aktualizowane

**Rozwiązanie**:
1. Sprawdź czy workflows działają (Actions)
2. Sprawdź czy pliki JSON w `data/` są aktualizowane
3. Wyczyść cache przeglądarki (Ctrl+Shift+R)

### Problem: "Error loading data"

**Rozwiązanie**:
1. Sprawdź czy pliki JSON istnieją w katalogu `data/`
2. Otwórz DevTools (F12) → Console i sprawdź błędy
3. Upewnij się, że ścieżki do plików są poprawne

## Customizacja

### Dodanie nowych funduszy 13F

1. Edytuj `config/sources.json`:
   ```json
   "funds": {
     "priority_ciks": {
       "0001234567": "Nazwa Funduszu"
     }
   }
   ```

2. Edytuj `scripts/fetch_13f.py` i dodaj logikę pobierania

3. Edytuj `js/data-loader.js` i dodaj slug funduszu do `fundSlugs`

### Zmiana reguł alertów

Edytuj `config/rules.json`:
```json
{
  "id": "custom_alert",
  "name": "Mój alert",
  "condition": "value > 1000000",
  "priority": "high",
  "description": "Opis alertu"
}
```

### Zmiana wyglądu

Edytuj `css/styles.css`:
- Zmienne CSS w `:root` (kolory, czcionki)
- Dark mode w `body.dark-theme`

## Zaawansowane opcje

### Dodanie własnego backendu

Jeśli potrzebujesz więcej niż statyczne dane:

1. Rozważ użycie Supabase dla:
   - Bazy danych (historia alertów)
   - Autentykacji użytkowników
   - Edge Functions (przetwarzanie danych)

2. Lub deploy tradycyjnego backendu:
   - Heroku, Vercel, Railway
   - Python/Node.js + PostgreSQL
   - API dla frontendu

### Monitoring i alerty

1. **Email notifications**: Dodaj w GitHub Actions
   ```yaml
   - name: Send email
     uses: dawidd6/action-send-mail@v3
   ```

2. **Slack/Discord webhooks**: Powiadomienia o alertach

3. **RSS Feed**: Generuj RSS w Actions

## Pomoc i wsparcie

### Dokumentacja zewnętrzna
- **GitHub Actions**: https://docs.github.com/en/actions
- **GitHub Pages**: https://docs.github.com/en/pages
- **SEC EDGAR API**: https://www.sec.gov/edgar/sec-api-documentation
- **Chart.js**: https://www.chartjs.org/docs/

### Zgłaszanie problemów
Utwórz issue w repozytorium z:
- Opisem problemu
- Logami z Actions (jeśli dotyczy)
- Krokami do reprodukcji

---

## ✅ Checklist przed uruchomieniem

- [ ] Utworzono repozytorium GitHub
- [ ] Wysłano kod do GitHub
- [ ] Dodano SEC_EDGAR_USER_AGENT w Secrets
- [ ] Włączono GitHub Actions
- [ ] Włączono GitHub Pages
- [ ] Uruchomiono workflows ręcznie (pierwszy raz)
- [ ] Sprawdzono czy strona działa
- [ ] Sprawdzono czy dane są pobierane

## 🎉 Gotowe!

Twój Market Radar 360° jest gotowy do użycia!

Strona: `https://TWOJE-USERNAME.github.io/market-radar-360/`

**Pamiętaj**: Dane polityków mają opóźnienia ustawowe (STOCK Act - do 45 dni). To NIE jest porada inwestycyjna!
