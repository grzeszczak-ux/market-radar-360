"""
Skrypt do pobierania danych o sentymencie rynkowym
Syntetyczny Fear & Greed Index bazujący na dostępnych wskaźnikach
"""

from typing import Dict, Any
from datetime import datetime
from utils import (
    DataValidator, DataWriter, create_metadata,
    logger
)
import json


class SentimentDataFetcher:
    """Pobiera i oblicza dane sentymentu rynkowego"""
    
    def __init__(self):
        self.validator = DataValidator()
        self.writer = DataWriter()
    
    def calculate_fear_greed_index(self) -> Dict[str, Any]:
        """
        Oblicza syntetyczny Fear & Greed Index
        
        Komponenty:
        - VIX (zmienność)
        - Put/Call Ratio
        - Market Momentum (52-week high/low)
        - Junk Bond Demand (spread)
        
        Returns:
            Słownik z indeksem (0-100) i klasyfikacją
        """
        logger.info("Obliczanie syntetycznego Fear & Greed Index...")
        
        # W produkcji: pobierz prawdziwe dane
        # Tutaj używamy przykładowych wartości
        
        # Komponent 1: VIX (0-100, niższy VIX = więcej greed)
        vix_value = 18.5  # Przykład
        vix_normalized = max(0, min(100, 100 - (vix_value - 10) * 5))
        
        # Komponent 2: Put/Call Ratio (niższy = greed)
        put_call_ratio = 0.75  # Przykład
        put_call_normalized = max(0, min(100, 100 - (put_call_ratio - 0.5) * 100))
        
        # Komponent 3: Market Momentum (% powyżej 52-week low)
        market_momentum = 0.65  # 65% powyżej minimum
        momentum_normalized = market_momentum * 100
        
        # Komponent 4: Safe Haven Demand (odwrócone)
        safe_haven_demand = 0.35  # Niska potrzeba = greed
        safe_haven_normalized = (1 - safe_haven_demand) * 100
        
        # Średnia ważona
        weights = {
            "vix": 0.30,
            "put_call": 0.25,
            "momentum": 0.25,
            "safe_haven": 0.20
        }
        
        fear_greed_score = (
            vix_normalized * weights["vix"] +
            put_call_normalized * weights["put_call"] +
            momentum_normalized * weights["momentum"] +
            safe_haven_normalized * weights["safe_haven"]
        )
        
        # Klasyfikacja
        if fear_greed_score <= 20:
            classification = "Extreme Fear"
            signal = "contrarian_buy"
        elif fear_greed_score <= 40:
            classification = "Fear"
            signal = "cautious"
        elif fear_greed_score <= 60:
            classification = "Neutral"
            signal = "neutral"
        elif fear_greed_score <= 80:
            classification = "Greed"
            signal = "cautious"
        else:
            classification = "Extreme Greed"
            signal = "contrarian_sell"
        
        result = {
            "index": round(fear_greed_score, 1),
            "classification": classification,
            "signal": signal,
            "components": {
                "vix": {
                    "value": vix_value,
                    "normalized": round(vix_normalized, 1),
                    "weight": weights["vix"]
                },
                "put_call_ratio": {
                    "value": put_call_ratio,
                    "normalized": round(put_call_normalized, 1),
                    "weight": weights["put_call"]
                },
                "market_momentum": {
                    "value": market_momentum,
                    "normalized": round(momentum_normalized, 1),
                    "weight": weights["momentum"]
                },
                "safe_haven_demand": {
                    "value": safe_haven_demand,
                    "normalized": round(safe_haven_normalized, 1),
                    "weight": weights["safe_haven"]
                }
            }
        }
        
        logger.info(f"✓ Fear & Greed Index: {fear_greed_score:.1f} ({classification})")
        return result
    
    def fetch_aaii_sentiment(self) -> Dict[str, Any]:
        """
        Pobiera dane AAII Sentiment Survey
        
        UWAGA: AAII wymaga subskrypcji dla pełnych danych
        Ta wersja używa przykładowych danych
        """
        logger.info("Pobieranie AAII Sentiment...")
        logger.info("⚠ Używam przykładowych danych (AAII wymaga subskrypcji)")
        
        # Przykładowe dane
        aaii_data = {
            "bullish": 32.5,  # % byków
            "neutral": 30.0,  # % neutralnych
            "bearish": 37.5,  # % niedźwiedzi
            "bull_bear_spread": -5.0,  # Byki - Niedźwiedzie
            "date": datetime.now().strftime("%Y-%m-%d"),
            "interpretation": "Slightly Bearish"
        }
        
        logger.info(f"✓ AAII: Bulls {aaii_data['bullish']}%, Bears {aaii_data['bearish']}%")
        return aaii_data
    
    def fetch_all(self) -> Dict[str, Any]:
        """
        Pobiera wszystkie dane sentymentu
        
        Returns:
            Słownik z danymi sentymentu i metadanymi
        """
        logger.info("=== Rozpoczęcie pobierania danych Sentiment ===")
        
        fear_greed = self.calculate_fear_greed_index()
        aaii = self.fetch_aaii_sentiment()
        
        output_data = {
            "metadata": create_metadata(),
            "fear_greed": fear_greed,
            "aaii": aaii
        }
        
        logger.info("✓ Pobrano dane sentymentu")
        return output_data
    
    def save(self, data: Dict[str, Any], output_path: str = "data/sentiment/latest.json") -> bool:
        """
        Zapisuje dane
        
        Args:
            data: Dane do zapisania
            output_path: Ścieżka wyjściowa
        
        Returns:
            True jeśli zapis się powiódł
        """
        return self.writer.write_json(data, output_path)


def main():
    """Główna funkcja"""
    fetcher = SentimentDataFetcher()
    data = fetcher.fetch_all()
    
    if data:
        success = fetcher.save(data)
        if success:
            logger.info("✓✓✓ Sentiment data update - SUCCESS ✓✓✓")
        else:
            logger.error("✗✗✗ Sentiment data update - FAILED ✗✗✗")
            exit(1)
    else:
        logger.warning("⚠ Brak danych sentymentu do zapisania")
        exit(1)


if __name__ == "__main__":
    main()
