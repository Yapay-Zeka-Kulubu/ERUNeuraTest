class MethodSelector:
    """
    Analiz edilen metotlar arasından karmaşıklığa göre
    en önemli 50 metodu seçen sınıf.
    """

    def __init__(self, limit=50):
        self.limit = limit

    def select_best_methods(self, methods_with_complexity):
        """
        Metotları karmaşıklık puanlarına göre sıralar
        ve ilk 50 tanesini seçer.
        """

        # Metotları hem cyclomatic hem de cognitive complexity toplamına göre
        # büyükten küçüğe sıralıyoruz
        sorted_methods = sorted(
            methods_with_complexity,
            key=lambda x: (
                x["complexity"]["cyclomatic_complexity"]
                + x["complexity"]["cognitive_complexity"]
            ),
            reverse=True,
        )

        # En karmaşık yani test edilmesi en önemli ilk 50 metodu döndürüyoruz
        return sorted_methods[:self.limit]
