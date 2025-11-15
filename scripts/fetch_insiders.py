"""
Skrypt do pobierania danych insiderów (Form 4) z SEC EDGAR
"""

import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta
from utils import (
    DataValidator, DataWriter, create_metadata,
    get_secret, logger, safe_get
)


class InsiderDataFetcher:
    """Pobiera i przetwarza dane Form 4 (insider trading)"""
    
    def __init__(self):
        self.validator = DataValidator()
        self.writer = DataWriter()
        
        # SEC wymaga User-Agent
        self.user_agent = get_secret("SEC_EDGAR_USER_AGENT", required=True)
        self.headers = {
            "User-Agent": self.user_agent
        }
        
        # SEC EDGAR search endpoint
        self.edgar_search_base = "https://efts.sec.gov/LATEST/search-index"
    
    def fetch_recent_form4(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Pobiera ostatnie zgłoszenia Form 4
        
        Args:
            days_back: Ile dni wstecz szukać
        
        Returns:
            Lista transakcji insiderów
        """
        logger.info(f"Pobieranie Form 4 z ostatnich {days_back} dni...")
        
        try:
            # Parametry wyszukiwania
            # UWAGA: To uproszczona wersja - SEC EDGAR API jest złożone
            # W produkcji potrzebny parser XML dla każdego Form 4
            
            from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            to_date = datetime.now().strftime("%Y-%m-%d")
            
            # Przykładowe zapytanie (SEC ma różne endpointy)
            # Ten endpoint może się różnić - sprawdź dokumentację SEC
            params = {
                "dateRange": "custom",
                "startdt": from_date,
                "enddt": to_date,
                "forms": "4"
            }
            
            # UWAGA: To jest placeholder URL - SEC może wymagać innego podejścia
            # Prawdopodobnie trzeba użyć RSS feed lub web scrapingu
            
            logger.info("⚠ UWAGA: Implementacja Form 4 wymaga parsowania XML")
            logger.info("  Używam przykładowych danych dla demonstracji")
            
            # Przykładowe dane (w produkcji: parsuj rzeczywiste Form 4)
            transactions = self._generate_sample_transactions()
            
            logger.info(f"✓ Pobrano {len(transactions)} transakcji insiderów")
            return transactions
            
        except Exception as e:
            logger.error(f"✗ Błąd pobierania Form 4: {str(e)}")
            return []
    
    def _generate_sample_transactions(self) -> List[Dict[str, Any]]:
        """
        Generuje przykładowe transakcje dla demonstracji
        W produkcji: zamień na prawdziwe parsowanie Form 4
        """
        samples = [
            {
                "insider_name": "John Smith",
                "insider_title": "CEO",
                "company": "Tech Corp",
                "ticker": "TECH",
                "transaction_type": "BUY",
                "shares": 10000,
                "price_per_share": 150.50,
                "value": 1505000,
                "shares_owned_after": 250000,
                "date": "2025-11-10",
                "filing_date": "2025-11-12",
                "form_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=..."
            },
            {
                "insider_name": "Jane Doe",
                "insider_title": "CFO",
                "company": "Finance Inc",
                "ticker": "FIN",
                "transaction_type": "SELL",
                "shares": 5000,
                "price_per_share": 85.25,
                "value": 426250,
                "shares_owned_after": 50000,
                "date": "2025-11-11",
                "filing_date": "2025-11-13",
                "form_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=..."
            }
        ]
        return samples
    
    def fetch_all(self) -> Dict[str, Any]:
        """
        Pobiera wszystkie dane insiderów
        
        Returns:
            Słownik z transakcjami i metadanymi
        """
        logger.info("=== Rozpoczęcie pobierania danych Insiders ===")
        
        transactions = self.fetch_recent_form4(days_back=30)
        
        # Sortowanie po dacie (najnowsze pierwsze)
        transactions.sort(
            key=lambda x: x.get("date", ""),
            reverse=True
        )
        
        output_data = {
            "metadata": create_metadata(
                total_count=len(transactions)
            ),
            "transactions": transactions
        }
        
        logger.info(f"✓ Łącznie {len(transactions)} transakcji insiderów")
        return output_data
    
    def save(self, data: Dict[str, Any], output_path: str = "data/insiders/latest.json") -> bool:
        """
        Waliduje i zapisuje dane
        
        Args:
            data: Dane do zapisania
            output_path: Ścieżka wyjściowa
        
        Returns:
            True jeśli zapis się powiódł
        """
        # Walidacja
        if not self.validator.validate(data, "insiders"):
            logger.error("✗ Walidacja nie powiodła się")
            return False
        
        # Zapis
        return self.writer.write_json(data, output_path)


def main():
    """Główna funkcja"""
    fetcher = InsiderDataFetcher()
    data = fetcher.fetch_all()
    
    if data["transactions"]:
        success = fetcher.save(data)
        if success:
            logger.info("✓✓✓ Insiders data update - SUCCESS ✓✓✓")
        else:
            logger.error("✗✗✗ Insiders data update - FAILED ✗✗✗")
            exit(1)
    else:
        logger.warning("⚠ Brak danych insiderów do zapisania")
        exit(1)


if __name__ == "__main__":
    main()
