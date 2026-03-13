"""
Analiz sonuçlarını JSON formatında dışa aktaran modül.

Seçilen metotları src/preprocess/output/selected_methods/ dizinine proje bazlı kaydeder.
UTF-8 encoding ve okunabilir format (indent=2) kullanır.
"""

import json
from pathlib import Path
from typing import List
from .models import MethodModel

DEFAULT_OUTPUT = Path(__file__).parent / "output" / "selected_methods"


class JSONExporter:
    """Seçilen metotları proje bazlı JSON dosyasına kaydeder."""

    def __init__(self, output_base_dir=None):
        self.output_base_dir = Path(output_base_dir) if output_base_dir else DEFAULT_OUTPUT
        self.output_base_dir.mkdir(parents=True, exist_ok=True)

    def export(self, methods: List[MethodModel], project_name: str) -> bool:
        """Metot listesini JSON dosyasına kaydeder. Başarılıysa True döner."""
        if not methods:
            print(f"Uyarı: {project_name} için dışa aktarılacak metot bulunamadı.")
            return False

        file_path = self.output_base_dir / f"{project_name}_methods.json"

        try:
            data = [self.format_method(m) for m in methods]

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"Kaydedildi: {file_path} ({len(data)} metot)")
            return True

        except Exception as e:
            print(f"Kaydetme hatasi: {e}")
            return False

    def format_method(self, method: MethodModel) -> dict:
        """MethodModel nesnesini JSON-uyumlu dict'e dönüştürür."""
        return method.to_dict()