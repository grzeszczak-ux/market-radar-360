"""
Skrypt do pobierania danych makroekonomicznych
Źródła: Yahoo Finance (publiczne API bez klucza)
Opcjonalnie: FRED API (wymaga klucza)
"""

import requests
from typing import Dict, Any, List
from datetime import datetime, timedelta
from utils import (
    DataValidator, DataWriter, create_metadata,
    load_config, get_secret, logger, safe_get
)


class MacroDataFetcher:
    """Pobiera dane makroekonomiczne"""
    
    def __init__(self):
        self.config = load_config("sources")
        self.validator = DataValidator()
        self.writer = DataWriter()
        
        # Symbole do śledzenia
        self.yahoo_symbols = safe_get(self.config, "macro", "yahoo", "symbols", default=[])
        
    def fetch_yahoo_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Pobiera aktualną cenę z Yahoo Finance
        
        Args:
            symbol: Symbol instrumentu (np. ^VIX, GC=F)
        
        Returns:
            Dane o instrumencie
        """
        try:
            # Yahoo Finance v8 API (publiczny endpoint)
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                "range": "1d",
                "interval": "1d"
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Wyciąganie danych
            result = safe_get(data, "chart", "result", default=[])
            if not result:
                logger.warning(f"Brak danych dla {symbol}")
                return None
            
            meta = safe_get(result[0], "meta", default={})
            current_price = safe_get(meta, "regularMarketPrice", default=0)
            previous_close = safe_get(meta, "previousClose", default=0)
            
            change = current_price - previous_close if previous_close else 0
            change_pct = (change / previous_close * 100) if previous_close else 0
            
            return {
                "symbol": symbol,
                "price": current_price,
                "previous_close": previous_close,
                "change": change,
                "change_pct": change_pct,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"✗ Błąd pobierania {symbol}: {str(e)}")
            return None
    
    def fetch_yahoo_history(self, symbol: str, days: int = 90) -> List[Dict[str, Any]]:
        """
        Pobiera dane historyczne z Yahoo Finance
        
        Args:
            symbol: Symbol instrumentu
            days: Ile dni historii
        
        Returns:
            Lista danych historycznych
        """
        try:
            end_timestamp = int(datetime.now().timestamp())
            start_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                "period1": start_timestamp,
                "period2": end_timestamp,
                "interval": "1d"
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = safe_get(data, "chart", "result", default=[])
            if not result:
                return []
            
            timestamps = safe_get(result[0], "timestamp", default=[])
            quotes = safe_get(result[0], "indicators", "quote", default=[])
            if not quotes:
                return []
            
            closes = safe_get(quotes[0], "close", default=[])
            
            history = []
            for i, ts in enumerate(timestamps):
                if i < len(closes) and closes[i] is not None:
                    history.append({
                        "date": datetime.fromtimestamp(ts).strftime("%Y-%m-%d"),
                        "value": closes[i]
                    })
            
            return history
            
        except Exception as e:
            logger.error(f"✗ Błąd pobierania historii {symbol}: {str(e)}")
            return []
    
    def calculate_spread_2s10s(self, us2y: float, us10y: float) -> float:
        """Oblicza spread krzywej dochodowości (10Y - 2Y)"""
        return us10y - us2y
    
    def fetch_all(self) -> Dict[str, Any]:
        """
        Pobiera wszystkie dane makro
        
        Returns:
            Słownik z wskaźnikami i metadanymi
        """
        logger.info("=== Rozpoczęcie pobierania danych Macro ===")
        
        # Mapowanie symboli Yahoo na nasze nazwy
        symbol_map = {
            "^TNX": "US10Y",
            "^IRX": "US2Y",
            "DX-Y.NYB": "DXY",
            "^VIX": "VIX",
            "GC=F": "gold",
            "CL=F": "oil",
            "HG=F": "copper"
        }
        
        indicators = {
            "yields": {},
            "currencies": {},
            "volatility": {},
            "commodities": {}
        }
        
        history = {}
        
        # Pobieranie danych dla każdego symbolu
        for yahoo_symbol, our_name in symbol_map.items():
            logger.info(f"Pobieranie: {our_name} ({yahoo_symbol})")
            
            # Aktualna cena
            quote = self.fetch_yahoo_quote(yahoo_symbol)
            if quote:
                value = quote["price"]
                
                # Kategoryzacja
                if our_name in ["US2Y", "US10Y"]:
                    indicators["yields"][our_name] = value
                elif our_name == "DXY":
                    indicators["currencies"][our_name] = value
                elif our_name == "VIX":
                    indicators["volatility"][our_name] = value
                else:
                    indicators["commodities"][our_name] = value
            
            # Historia
            hist = self.fetch_yahoo_history(yahoo_symbol, days=90)
            if hist:
                history[our_name] = hist
        
        # Obliczenie spreadu 2s10s
        if "US2Y" in indicators["yields"] and "US10Y" in indicators["yields"]:
            spread = self.calculate_spread_2s10s(
                indicators["yields"]["US2Y"],
                indicators["yields"]["US10Y"]
            )
            indicators["yields"]["spread_2s10s"] = spread
            logger.info(f"  Spread 2s10s: {spread:.4f}")
        
        output_data = {
            "metadata": create_metadata(),
            "indicators": indicators,
            "history": history
        }
        
        logger.info("✓ Pobrano dane makroekonomiczne")
        return output_data
    
    def save(self, data: Dict[str, Any], output_path: str = "data/macro/indicators.json") -> bool:
        """
        Waliduje i zapisuje dane
        
        Args:
            data: Dane do zapisania
            output_path: Ścieżka wyjściowa
        
        Returns:
            True jeśli zapis się powiódł
        """
        # Walidacja
        if not self.validator.validate(data, "macro"):
            logger.error("✗ Walidacja nie powiodła się")
            return False
        
        # Zapis
        return self.writer.write_json(data, output_path)


def main():
    """Główna funkcja"""
    fetcher = MacroDataFetcher()
    data = fetcher.fetch_all()
    
    if data["indicators"]:
        success = fetcher.save(data)
        if success:
            logger.info("✓✓✓ Macro data update - SUCCESS ✓✓✓")
        else:
            logger.error("✗✗✗ Macro data update - FAILED ✗✗✗")
            exit(1)
    else:
        logger.warning("⚠ Brak danych makro do zapisania")
        exit(1)


if __name__ == "__main__":
    main()
