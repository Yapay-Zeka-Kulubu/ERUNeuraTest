"""CodeValidator sınıfı için birim testleri."""

import pytest
from src.postprocess.validator import CodeValidator


@pytest.fixture
def validator():
    """Her test için yeni bir CodeValidator örneği döndürür."""
    return CodeValidator()


# ─── Syntax Testleri ─────────────────────────────────────────

class TestValidateSyntax:
    """validate_syntax metodu testleri."""

    def test_gecerli_kod(self, validator):
        """Geçerli Python kodu için True dönmeli."""
        code = "x = 1 + 2\nprint(x)"
        result = validator.validate_syntax(code)
        assert result.is_valid is True

    def test_hatali_kod(self, validator):
        """Sözdizimi hatası olan kod için False dönmeli."""
        code = "def foo(\n    broken"
        result = validator.validate_syntax(code)
        assert result.is_valid is False
        assert "Syntax hatası" in result.message

    def test_bos_kod(self, validator):
        """Boş string geçerli Python kodudur."""
        result = validator.validate_syntax("")
        assert result.is_valid is True

    def test_fonksiyon_tanimli_kod(self, validator):
        """Fonksiyon tanımı içeren kod geçerli olmalı."""
        code = """
def toplama(a, b):
    return a + b
"""
        result = validator.validate_syntax(code)
        assert result.is_valid is True

    def test_sinif_tanimli_kod(self, validator):
        """Sınıf tanımı içeren kod geçerli olmalı."""
        code = """
class Hesap:
    def __init__(self, bakiye=0):
        self.bakiye = bakiye

    def para_yatir(self, miktar):
        self.bakiye += miktar
"""
        result = validator.validate_syntax(code)
        assert result.is_valid is True


# ─── Import Testleri ─────────────────────────────────────────

class TestValidateImports:
    """validate_imports metodu testleri."""

    def test_gecerli_importlar(self, validator):
        """Standart kütüphane importları geçerli olmalı."""
        code = "import os\nimport sys"
        result = validator.validate_imports(code)
        assert result.is_valid is True

    def test_gecersiz_import(self, validator):
        """Var olmayan modül importu hata vermeli."""
        code = "import bu_modul_yok_12345"
        result = validator.validate_imports(code)
        assert result.is_valid is False
        assert "bulunamadı" in result.message

    def test_importsuz_kod(self, validator):
        """Import içermeyen kod geçerli sayılmalı."""
        code = "x = 42\nprint(x)"
        result = validator.validate_imports(code)
        assert result.is_valid is True

    def test_from_import_gecerli(self, validator):
        """from ... import ... stili geçerli olmalı."""
        code = "from os.path import join"
        result = validator.validate_imports(code)
        assert result.is_valid is True

    def test_from_import_gecersiz(self, validator):
        """from ... import ... stili ile var olmayan modül hata vermeli."""
        code = "from sahte_paket_xyz import birsey"
        result = validator.validate_imports(code)
        assert result.is_valid is False


# ─── Run Test Testleri ───────────────────────────────────────

class TestRunTest:
    """run_test metodu testleri."""

    def test_gecen_test(self, validator):
        """Başarılı bir test kodu çalıştırıldığında passed=True olmalı."""
        test_code = """
def test_toplama():
    assert 1 + 1 == 2
"""
        result = validator.run_test(test_code)
        assert result.passed is True
        assert result.return_code == 0

    def test_kalan_test(self, validator):
        """Başarısız bir test kodu çalıştırıldığında passed=False olmalı."""
        test_code = """
def test_yanlis():
    assert 1 + 1 == 5
"""
        result = validator.run_test(test_code)
        assert result.passed is False
        assert result.return_code != 0
