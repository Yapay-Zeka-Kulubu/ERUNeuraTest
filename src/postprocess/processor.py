class PostProcessor:
    """
    LLM tarafından üretilen test kodlarının son işleme (postprocess) aşamasını yönetir.

    Bu aşamada:

        1) Kod doğrulanır (validator)
        2) FixerChain ile hatalar düzeltilir
        3) Çalıştırılabilir test kodu elde edilir
    """