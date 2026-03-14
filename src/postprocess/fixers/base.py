class BaseFixer:
    """
    Postprocess aşamasındaki tüm fixer sınıfları için temel sınıftır.

    Her fixer LLM tarafından üretilen test kodunu alır,
    belirli kurallara göre düzeltir ve yeni kodu geri döndürür.

    Alt sınıflar fix() metodunu implement etmelidir.
    """

    def fix(self, code: str) -> str:
        raise NotImplementedError("Alt fixer sınıfları bu metodu implement etmelidir.")