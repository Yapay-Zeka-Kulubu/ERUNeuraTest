"""
Karmaşıklığa göre en kritik metotları seçen modül.

Metotları (cyclomatic + cognitive) toplam skoruna göre büyükten küçüğe sıralar
ve en karmaşık N metodu seçer. Varsayılan limit: 50.
"""

from typing import List
from .models import MethodModel


class MethodSelector:
    """Complexity skoruna göre en önemli N metodu seçer."""

    def __init__(self, limit: int = 50):
        self.limit = limit

    def select_best_methods(self, methods: List[MethodModel]) -> List[MethodModel]:
        """
        Metotları karmaşıklık puanına göre sıralar ve ilk N tanesini seçer.
        Aynı skorlarda satır sayısı fazla olan önceliklidir.
        """
        ranked = self._rank_by_complexity(methods)
        return ranked[:self.limit]

    def _rank_by_complexity(self, methods: List[MethodModel]) -> List[MethodModel]:
        """
        Metotları toplam complexity skoruna göre büyükten küçüğe sıralar.
        İkincil kriter: satır sayısı (line_count).
        """
        return sorted(
            methods,
            key=lambda m: (
                m.complexity.cyclomatic_complexity + m.complexity.cognitive_complexity,
                m.line_count,
            ),
            reverse=True,
        )