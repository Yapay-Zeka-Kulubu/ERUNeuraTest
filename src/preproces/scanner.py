import os
import sys
from pathlib import Path

# Proje ana dizinini Python yoluna ekle
base_path = Path(__file__).parent.parent.parent
sys.path.append(str(base_path))

from src.preproces.analyzer import ASTAnalyzer
from src.preproces.complexity import ComplexityCalculator
from src.preproces.selector import MethodSelector
from src.preproces.exporter import JSONExporter


class ProjectScanner:
    def __init__(self, benchmark_dir=None):
        self.benchmark_dir = base_path / "benchmark"
        self.complexity_calc = ComplexityCalculator()
        self.selector = MethodSelector(limit=50)
        self.exporter = JSONExporter()

    def run(self):
        print(f"Tarama dizini: {self.benchmark_dir.absolute()}")

        if not self.benchmark_dir.exists():
            print(f"Hata: {self.benchmark_dir} klasörü bulunamadı!")
            return

        projects = [d for d in self.benchmark_dir.iterdir() if d.is_dir()]
        print(f"Bulunan projeler: {[p.name for p in projects]}")

        for project_path in projects:
            project_name = project_path.name
            print(f"Isleniyor: {project_name}")
            all_methods = []

            python_files = list(project_path.rglob("*.py"))
            for file_path in python_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()

                    analyzer = ASTAnalyzer(code)
                    methods = analyzer.get_methods_info()

                    for m in methods:
                        comp_results = self.complexity_calc.calculate(m["body"])
                        all_methods.append(
                            {
                                "project": {"name": project_name},
                                "file": {
                                    "name": file_path.name,
                                    "path": str(file_path),
                                },
                                "method": m,
                                "complexity": comp_results,
                            }
                        )
                except Exception:
                    continue

            if all_methods:
                selected = self.selector.select_best_methods(all_methods)
                self.exporter.export(selected, project_name)


if __name__ == "__main__":
    scanner = ProjectScanner()
    scanner.run()
