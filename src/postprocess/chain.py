class FixerChain:
    """
    Birden fazla fixer'ı sırayla çalıştıran yapı.

    Kod önce SyntaxFixer'a,
    sonra ImportFixer'a,
    ardından diğer fixer'lara gönderilir.

    Her fixer kodu düzenler ve bir sonraki fixer'a aktarır.
    """