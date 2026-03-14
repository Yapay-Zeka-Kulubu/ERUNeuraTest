class LLMFixer:
    """
    Kural tabanlı fixer'ların düzeltemediği durumlarda devreye girer.

    Bu fixer, problemi tekrar bir LLM'e göndererek
    kodun düzeltilmiş halini üretmeyi amaçlar.

    Bu sayede karmaşık hatalar da giderilebilir.
    """