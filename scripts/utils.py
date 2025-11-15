"""
Moduł pomocniczy dla skryptów pobierania danych Market Radar 360°
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import jsonschema
from jsonschema import validate
import logging

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataValidator:
    """Walidator danych JSON według schematów"""
    
    def __init__(self, schema_dir: str = "config/schemas"):
        self.schema_dir = Path(schema_dir)
        self.schemas: Dict[str, Dict] = {}
        self._load_schemas()
    
    def _load_schemas(self):
        """Ładuje wszystkie schematy JSON"""
        if not self.schema_dir.exists():
            logger.warning(f"Katalog schematów nie istnieje: {self.schema_dir}")
            return
        
        for schema_file in self.schema_dir.glob("*.json"):
            schema_name = schema_file.stem
            with open(schema_file, 'r', encoding='utf-8') as f:
                self.schemas[schema_name] = json.load(f)
            logger.info(f"Załadowano schemat: {schema_name}")
    
    def validate(self, data: Dict[str, Any], schema_name: str) -> bool:
        """
        Waliduje dane względem schematu
        
        Args:
            data: Dane do walidacji
            schema_name: Nazwa schematu (bez rozszerzenia .json)
        
        Returns:
            True jeśli dane są poprawne, False w przeciwnym razie
        """
        if schema_name not in self.schemas:
            logger.error(f"Schemat nie znaleziony: {schema_name}")
            return False
        
        try:
            validate(instance=data, schema=self.schemas[schema_name])
            logger.info(f"✓ Walidacja pomyślna: {schema_name}")
            return True
        except jsonschema.exceptions.ValidationError as e:
            logger.error(f"✗ Błąd walidacji {schema_name}: {e.message}")
            logger.error(f"  Ścieżka: {' -> '.join(str(p) for p in e.path)}")
            return False


class DataWriter:
    """Zapisywanie danych JSON z automatycznym tworzeniem katalogów"""
    
    @staticmethod
    def write_json(data: Dict[str, Any], output_path: str, pretty: bool = True) -> bool:
        """
        Zapisuje dane do pliku JSON
        
        Args:
            data: Dane do zapisania
            output_path: Ścieżka do pliku wyjściowego
            pretty: Czy formatować JSON (wcięcia)
        
        Returns:
            True jeśli zapis się powiódł
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(data, f, ensure_ascii=False)
            
            file_size = output_file.stat().st_size / 1024  # KB
            logger.info(f"✓ Zapisano: {output_path} ({file_size:.2f} KB)")
            return True
        except Exception as e:
            logger.error(f"✗ Błąd zapisu {output_path}: {str(e)}")
            return False


def get_timestamp() -> str:
    """Zwraca aktualny timestamp w formacie ISO"""
    return datetime.utcnow().isoformat() + "Z"


def load_config(config_name: str = "sources") -> Dict[str, Any]:
    """
    Ładuje plik konfiguracyjny
    
    Args:
        config_name: Nazwa pliku (bez rozszerzenia)
    
    Returns:
        Słownik z konfiguracją
    """
    config_path = Path(f"config/{config_name}.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info(f"✓ Załadowano konfigurację: {config_name}")
        return config
    except Exception as e:
        logger.error(f"✗ Błąd ładowania konfiguracji {config_name}: {str(e)}")
        return {}


def get_secret(secret_name: str, required: bool = False) -> Optional[str]:
    """
    Pobiera sekret z zmiennych środowiskowych
    
    Args:
        secret_name: Nazwa zmiennej środowiskowej
        required: Czy sekret jest wymagany (rzuci wyjątek jeśli brak)
    
    Returns:
        Wartość sekretu lub None
    """
    value = os.environ.get(secret_name)
    if required and not value:
        raise ValueError(f"Wymagany sekret nie został ustawiony: {secret_name}")
    return value


def create_metadata(total_count: int = 0, **kwargs) -> Dict[str, Any]:
    """
    Tworzy standardowy obiekt metadata
    
    Args:
        total_count: Liczba rekordów
        **kwargs: Dodatkowe pola metadanych
    
    Returns:
        Słownik z metadanymi
    """
    metadata = {
        "last_updated": get_timestamp(),
        "total_count": total_count
    }
    metadata.update(kwargs)
    return metadata


def safe_get(data: Dict, *keys, default=None):
    """
    Bezpieczne pobieranie wartości z zagnieżdżonego słownika
    
    Example:
        safe_get(data, 'level1', 'level2', 'level3', default='N/A')
    """
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data if data is not None else default


# Eksport głównych klas i funkcji
__all__ = [
    'DataValidator',
    'DataWriter',
    'get_timestamp',
    'load_config',
    'get_secret',
    'create_metadata',
    'safe_get',
    'logger'
]
