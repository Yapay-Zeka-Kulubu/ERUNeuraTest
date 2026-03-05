import json
from pathlib import Path


class JSONExporter:
    """
    Seçilen metotları ve analiz sonuçlarını JSON formatında dışa aktaran sınıf.
    """

    def __init__(self, output_base_dir="output/selected_methods"):
        self.output_base_dir = Path(output_base_dir)

        # Çıktı klasörü yoksa oluşturur
        self.output_base_dir.mkdir(parents=True, exist_ok=True)

    def export(self, data, project_name):
        """
        Verileri belirtilen proje adı ile JSON dosyasına kaydeder.
        """
        file_path = self.output_base_dir / f"{project_name}_methods.json"

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                # İstenen formatta, girintili ve Türkçe karakter destekli kaydeder
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"Basariyla kaydedildi: {file_path}")
            return True

        except Exception as e:
            print(f"Kaydetme hatasi: {e}")
            return False
