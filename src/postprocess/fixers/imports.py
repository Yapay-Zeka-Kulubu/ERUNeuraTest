class ImportFixer:
    """
    Kod içinde kullanılmış fakat import edilmemiş kütüphaneleri tespit eder.

    Örneğin:
        pytest kullanılmış ama 'import pytest' yok
        patch kullanılmış ama 'from unittest.mock import patch' yok

    Bu durumlarda eksik importları eklemeyi amaçlar.
    """