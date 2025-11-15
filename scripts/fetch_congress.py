"""
Skrypt do pobierania danych o transakcjach polityków USA (Congress & Senate)
Źródła: House Stock Watcher & Senate Stock Watcher (publiczne JSON)
"""

import requests
from typing import List, Dict, Any
from datetime import datetime
from utils import (
    DataValidator, DataWriter, create_metadata, 
    load_config, logger, safe_get
)


class CongressDataFetcher:
    """Pobiera i przetwarza dane o transakcjach kongresmenów"""
    
    def __init__(self):
        self.config = load_config("sources")
        self.validator = DataValidator()
        self.writer = DataWriter()
        
        # URLs z konfiguracji
        self.house_url = safe_get(self.config, "congress", "house", "url")
        self.senate_url = safe_get(self.config, "congress", "senate", "url")
        
    def fetch_house_transactions(self) -> List[Dict[str, Any]]:
        """Pobiera transakcje z House of Representatives"""
        logger.info("Pobieranie danych z House...")
        
        try:
            response = requests.get(self.house_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Normalizacja danych
            transactions = []
            for item in data:
                transaction = self._normalize_transaction(item, "House")
                if transaction:
                    transactions.append(transaction)
            
            logger.info(f"✓ Pobrano {len(transactions)} transakcji z House")
            return transactions
            
        except Exception as e:
            logger.error(f"✗ Błąd pobierania danych z House: {str(e)}")
            return []
    
    def fetch_senate_transactions(self) -> List[Dict[str, Any]]:
        """Pobiera transakcje z Senate"""
        logger.info("Pobieranie danych z Senate...")
        
        try:
            response = requests.get(self.senate_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Normalizacja danych
            transactions = []
            for item in data:
                transaction = self._normalize_transaction(item, "Senate")
                if transaction:
                    transactions.append(transaction)
            
            logger.info(f"✓ Pobrano {len(transactions)} transakcji z Senate")
            return transactions
            
        except Exception as e:
            logger.error(f"✗ Błąd pobierania danych z Senate: {str(e)}")
            return []
    
    def _normalize_transaction(self, raw_data: Dict, chamber: str) -> Dict[str, Any]:
        """
        Normalizuje transakcję do standardowego formatu
        
        Args:
            raw_data: Surowe dane z API
            chamber: "House" lub "Senate"
        
        Returns:
            Znormalizowana transakcja
        """
        try:
            # Mapowanie pól (może się różnić między źródłami)
            transaction = {
                "person": safe_get(raw_data, "representative", default="Unknown"),
                "chamber": chamber,
                "ticker": safe_get(raw_data, "ticker", default="N/A"),
                "sector": safe_get(raw_data, "sector", default="Unknown"),
                "transaction_type": self._normalize_transaction_type(
                    safe_get(raw_data, "type", default="purchase")
                ),
                "amount_range": safe_get(raw_data, "amount", default="N/A"),
                "date": safe_get(raw_data, "transaction_date", default=""),
                "disclosure_date": safe_get(raw_data, "disclosure_date", default=""),
                "link": safe_get(raw_data, "ptr_link", default="")
            }
            
            # Parsowanie zakresu kwoty do min/max
            amount_min, amount_max = self._parse_amount_range(transaction["amount_range"])
            transaction["amount_min"] = amount_min
            transaction["amount_max"] = amount_max
            
            return transaction
            
        except Exception as e:
            logger.warning(f"Błąd normalizacji transakcji: {str(e)}")
            return None
    
    def _normalize_transaction_type(self, raw_type: str) -> str:
        """Normalizuje typ transakcji"""
        raw_type_lower = raw_type.lower()
        
        if "purchase" in raw_type_lower or "buy" in raw_type_lower:
            return "purchase"
        elif "sale" in raw_type_lower or "sell" in raw_type_lower:
            return "sale"
        elif "exchange" in raw_type_lower:
            return "exchange"
        else:
            return "purchase"  # domyślnie
    
    def _parse_amount_range(self, amount_str: str) -> tuple:
        """
        Parsuje zakres kwoty (np. "$15,001 - $50,000")
        
        Returns:
            (min, max) tuple
        """
        try:
            # Usuwanie $ i przecinków
            amount_str = amount_str.replace("$", "").replace(",", "")
            
            if "-" in amount_str:
                parts = amount_str.split("-")
                min_val = float(parts[0].strip())
                max_val = float(parts[1].strip())
                return (min_val, max_val)
            else:
                # Pojedyncza wartość
                val = float(amount_str.strip())
                return (val, val)
        except:
            return (0, 0)
    
    def fetch_all(self) -> Dict[str, Any]:
        """
        Pobiera wszystkie dane (House + Senate) i scala
        
        Returns:
            Słownik z transakcjami i metadanymi
        """
        logger.info("=== Rozpoczęcie pobierania danych Congress ===")
        
        house_transactions = self.fetch_house_transactions()
        senate_transactions = self.fetch_senate_transactions()
        
        all_transactions = house_transactions + senate_transactions
        
        # Sortowanie po dacie (najnowsze pierwsze)
        all_transactions.sort(
            key=lambda x: x.get("date", ""), 
            reverse=True
        )
        
        # Przygotowanie danych wyjściowych
        output_data = {
            "metadata": create_metadata(
                total_count=len(all_transactions),
                house_count=len(house_transactions),
                senate_count=len(senate_transactions),
                date_range={
                    "from": all_transactions[-1]["date"] if all_transactions else "",
                    "to": all_transactions[0]["date"] if all_transactions else ""
                }
            ),
            "transactions": all_transactions
        }
        
        logger.info(f"✓ Łącznie {len(all_transactions)} transakcji")
        return output_data
    
    def save(self, data: Dict[str, Any], output_path: str = "data/congress/all.json") -> bool:
        """
        Waliduje i zapisuje dane
        
        Args:
            data: Dane do zapisania
            output_path: Ścieżka wyjściowa
        
        Returns:
            True jeśli zapis się powiódł
        """
        # Walidacja
        if not self.validator.validate(data, "congress"):
            logger.error("✗ Walidacja nie powiodła się")
            return False
        
        # Zapis
        return self.writer.write_json(data, output_path)


def main():
    """Główna funkcja"""
    fetcher = CongressDataFetcher()
    data = fetcher.fetch_all()
    
    if data["transactions"]:
        success = fetcher.save(data)
        if success:
            logger.info("✓✓✓ Congress data update - SUCCESS ✓✓✓")
        else:
            logger.error("✗✗✗ Congress data update - FAILED ✗✗✗")
            exit(1)
    else:
        logger.warning("⚠ Brak danych do zapisania")
        exit(1)


if __name__ == "__main__":
    main()
