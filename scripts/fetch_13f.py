"""
Skrypt do pobierania danych 13F (fundusze hedge) z SEC EDGAR
"""

import requests
from typing import List, Dict, Any
from datetime import datetime
from utils import (
    DataValidator, DataWriter, create_metadata,
    load_config, get_secret, logger, safe_get
)


class Fund13FFetcher:
    """Pobiera i przetwarza dane 13F z SEC EDGAR"""
    
    def __init__(self):
        self.config = load_config("sources")
        self.validator = DataValidator()
        self.writer = DataWriter()
        
        # SEC wymaga User-Agent
        self.user_agent = get_secret("SEC_EDGAR_USER_AGENT", required=True)
        self.headers = {
            "User-Agent": self.user_agent
        }
        
        # Lista priorytetowych funduszy z CIK
        self.priority_funds = safe_get(self.config, "funds", "priority_ciks", default={})
        
        self.sec_api_base = "https://data.sec.gov/submissions/"
    
    def fetch_fund_13f(self, cik: str, fund_name: str) -> Dict[str, Any]:
        """
        Pobiera najnowsze zgłoszenie 13F dla funduszu
        
        Args:
            cik: Central Index Key funduszu (10 cyfr z zerami wiodącymi)
            fund_name: Nazwa funduszu
        
        Returns:
            Dane 13F w standardowym formacie
        """
        logger.info(f"Pobieranie 13F dla: {fund_name} (CIK: {cik})")
        
        try:
            # Format: CIK0001234567.json
            cik_padded = f"CIK{cik.zfill(10)}"
            url = f"{self.sec_api_base}{cik_padded}.json"
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Znajdujemy najnowsze zgłoszenie 13F-HR
            recent_filings = safe_get(data, "filings", "recent", default={})
            forms = safe_get(recent_filings, "form", default=[])
            
            # Szukamy 13F-HR
            f13_index = None
            for i, form in enumerate(forms):
                if form == "13F-HR":
                    f13_index = i
                    break
            
            if f13_index is None:
                logger.warning(f"Brak zgłoszeń 13F-HR dla {fund_name}")
                return None
            
            # Wyciąganie metadanych
            filing_date = safe_get(recent_filings, "filingDate", default=[])[f13_index]
            period_end = safe_get(recent_filings, "reportDate", default=[])[f13_index]
            accession_number = safe_get(recent_filings, "accessionNumber", default=[])[f13_index]
            
            logger.info(f"  Znaleziono 13F-HR: {filing_date} (okres: {period_end})")
            
            # W rzeczywistości trzeba by parsować XML z holdings
            # Dla uproszczenia zwracamy strukturę z placeholderami
            # W produkcji: pobierz pełny XML i sparsuj holdings
            
            fund_data = {
                "fund_info": {
                    "name": fund_name,
                    "cik": cik,
                    "filing_date": filing_date,
                    "period_end": period_end,
                    "total_value": 0  # Do obliczenia z holdings
                },
                "metadata": create_metadata(
                    holdings_count=0,
                    accession_number=accession_number
                ),
                "holdings": []  # Tutaj byłyby rzeczywiste pozycje
            }
            
            logger.info(f"✓ Pobrano dane 13F dla {fund_name}")
            return fund_data
            
        except Exception as e:
            logger.error(f"✗ Błąd pobierania 13F dla {fund_name}: {str(e)}")
            return None
    
    def fetch_all_priority_funds(self) -> Dict[str, Dict[str, Any]]:
        """
        Pobiera 13F dla wszystkich priorytetowych funduszy
        
        Returns:
            Słownik {fund_slug: fund_data}
        """
        logger.info("=== Rozpoczęcie pobierania danych 13F ===")
        
        all_funds_data = {}
        
        for cik, fund_name in self.priority_funds.items():
            fund_slug = self._create_slug(fund_name)
            fund_data = self.fetch_fund_13f(cik, fund_name)
            
            if fund_data:
                all_funds_data[fund_slug] = fund_data
        
        logger.info(f"✓ Pobrano dane dla {len(all_funds_data)} funduszy")
        return all_funds_data
    
    def _create_slug(self, fund_name: str) -> str:
        """Tworzy slug z nazwy funduszu (np. 'scion', 'berkshire')"""
        # Wyciąga pierwsze słowo i konwertuje do lowercase
        first_word = fund_name.split()[0].lower()
        # Usuwa znaki specjalne
        slug = "".join(c for c in first_word if c.isalnum())
        return slug
    
    def save_all(self, funds_data: Dict[str, Dict[str, Any]]) -> bool:
        """
        Zapisuje dane wszystkich funduszy do osobnych plików
        
        Args:
            funds_data: Słownik {fund_slug: fund_data}
        
        Returns:
            True jeśli wszystkie zapisy się powiodły
        """
        all_success = True
        
        for fund_slug, fund_data in funds_data.items():
            output_path = f"data/funds/{fund_slug}.json"
            
            # Walidacja
            if not self.validator.validate(fund_data, "fund_13f"):
                logger.error(f"✗ Walidacja nie powiodła się dla {fund_slug}")
                all_success = False
                continue
            
            # Zapis
            if not self.writer.write_json(fund_data, output_path):
                all_success = False
        
        return all_success


def main():
    """Główna funkcja"""
    fetcher = Fund13FFetcher()
    funds_data = fetcher.fetch_all_priority_funds()
    
    if funds_data:
        success = fetcher.save_all(funds_data)
        if success:
            logger.info("✓✓✓ 13F data update - SUCCESS ✓✓✓")
        else:
            logger.error("✗✗✗ 13F data update - PARTIAL FAILURE ✗✗✗")
            exit(1)
    else:
        logger.warning("⚠ Brak danych 13F do zapisania")
        exit(1)


if __name__ == "__main__":
    main()
