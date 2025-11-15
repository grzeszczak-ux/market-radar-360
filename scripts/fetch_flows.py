"""
Skrypt do pobierania danych o przepływach kapitału (ETF flows, opcje)
UWAGA: To uproszczona wersja - pełna implementacja wymaga płatnych API
"""

from typing import Dict, Any, List
from datetime import datetime
from utils import (
    DataValidator, DataWriter, create_metadata,
    logger
)


class FlowDataFetcher:
    """Pobiera dane o przepływach kapitału"""
    
    def __init__(self):
        self.validator = DataValidator()
        self.writer = DataWriter()
    
    def fetch_etf_flows(self) -> List[Dict[str, Any]]:
        """
        Pobiera dane o napływach/odpływach ETF
        
        UWAGA: Wymaga płatnych API (np. ETF.com, Bloomberg)
        Ta wersja używa przykładowych danych
        """
        logger.info("Pobieranie danych ETF flows...")
        logger.info("⚠ Używam przykładowych danych (brak darmowego API)")
        
        # Przykładowe dane dla głównych ETF
        sample_flows = [
            {
                "ticker": "SPY",
                "name": "SPDR S&P 500 ETF",
                "flow_1d": -250000000,  # Odpływ $250M
                "flow_5d": -1200000000,
                "flow_30d": 3500000000,
                "aum": 450000000000,  # $450B AUM
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "ticker": "QQQ",
                "name": "Invesco QQQ Trust",
                "flow_1d": 150000000,  # Napływ $150M
                "flow_5d": 800000000,
                "flow_30d": 5200000000,
                "aum": 250000000000,
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "ticker": "IWM",
                "name": "iShares Russell 2000 ETF",
                "flow_1d": -50000000,
                "flow_5d": -200000000,
                "flow_30d": -1500000000,
                "aum": 65000000000,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
        ]
        
        logger.info(f"✓ Pobrano dane flows dla {len(sample_flows)} ETF")
        return sample_flows
    
    def fetch_options_data(self) -> List[Dict[str, Any]]:
        """
        Pobiera dane o wolumenie opcji i open interest
        
        UWAGA: Wymaga płatnych API (np. CBOE, OptionsPrice.com)
        Ta wersja używa przykładowych danych
        """
        logger.info("Pobieranie danych opcji...")
        logger.info("⚠ Używam przykładowych danych (brak darmowego API)")
        
        sample_options = [
            {
                "ticker": "SPY",
                "total_volume": 8500000,
                "call_volume": 5000000,
                "put_volume": 3500000,
                "put_call_ratio": 0.70,
                "total_oi": 15000000,
                "avg_volume_30d": 6500000,
                "volume_anomaly": True,  # Wolumen > 1.3x średniej
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "ticker": "AAPL",
                "total_volume": 1200000,
                "call_volume": 800000,
                "put_volume": 400000,
                "put_call_ratio": 0.50,
                "total_oi": 2500000,
                "avg_volume_30d": 950000,
                "volume_anomaly": True,
                "date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "ticker": "TSLA",
                "total_volume": 2000000,
                "call_volume": 1400000,
                "put_volume": 600000,
                "put_call_ratio": 0.43,
                "total_oi": 3200000,
                "avg_volume_30d": 1800000,
                "volume_anomaly": False,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
        ]
        
        logger.info(f"✓ Pobrano dane opcji dla {len(sample_options)} tickerów")
        return sample_options
    
    def fetch_all(self) -> Dict[str, Any]:
        """
        Pobiera wszystkie dane o przepływach
        
        Returns:
            Słownik z danymi flows i metadanymi
        """
        logger.info("=== Rozpoczęcie pobierania danych Flow ===")
        
        etf_flows = self.fetch_etf_flows()
        options_data = self.fetch_options_data()
        
        output_data = {
            "metadata": create_metadata(
                etf_count=len(etf_flows),
                options_count=len(options_data)
            ),
            "etf_flows": etf_flows,
            "options": options_data
        }
        
        logger.info(f"✓ Pobrano {len(etf_flows)} ETF flows i {len(options_data)} opcji")
        return output_data
    
    def save(self, data: Dict[str, Any], output_path: str = "data/flows/latest.json") -> bool:
        """
        Zapisuje dane (bez walidacji - brak schematu)
        
        Args:
            data: Dane do zapisania
            output_path: Ścieżka wyjściowa
        
        Returns:
            True jeśli zapis się powiódł
        """
        return self.writer.write_json(data, output_path)


def main():
    """Główna funkcja"""
    fetcher = FlowDataFetcher()
    data = fetcher.fetch_all()
    
    if data:
        success = fetcher.save(data)
        if success:
            logger.info("✓✓✓ Flow data update - SUCCESS ✓✓✓")
        else:
            logger.error("✗✗✗ Flow data update - FAILED ✗✗✗")
            exit(1)
    else:
        logger.warning("⚠ Brak danych flows do zapisania")
        exit(1)


if __name__ == "__main__":
    main()
