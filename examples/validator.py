"""Postprocess Validator - Kod doğrulama modülü."""

import ast
import sys
import tempfile
import subprocess
import os
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Doğrulama sonucunu tutan sınıf."""
    is_valid: bool
    message: str


@dataclass
class TestResult:
    """Test çalıştırma sonucunu tutan sınıf."""
    passed: bool
    output: str
    return_code: int


class CodeValidator:
    """Python kodlarını doğrulayan sınıf."""

    def validate_syntax(self, code: str) -> ValidationResult:
        """Kodun sözdizimini (syntax) kontrol eder."""
        try:
            ast.parse(code)
            return ValidationResult(is_valid=True, message="Syntax geçerli.")
        except SyntaxError as e:
            return ValidationResult(is_valid=False, message=f"Syntax hatası: {e}")

    def validate_imports(self, code: str) -> ValidationResult:
        """Koddaki import ifadelerinin geçerliliğini kontrol eder."""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return ValidationResult(is_valid=False, message=f"Parse hatası: {e}")

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if not self._module_exists(alias.name):
                        return ValidationResult(
                            is_valid=False,
                            message=f"Modül bulunamadı: {alias.name}",
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module and not self._module_exists(node.module):
                    return ValidationResult(
                        is_valid=False,
                        message=f"Modül bulunamadı: {node.module}",
                    )

        return ValidationResult(is_valid=True, message="Tüm importlar geçerli.")

    def run_test(self, test_code: str) -> TestResult:
        """Verilen test kodunu geçici dosyaya yazıp pytest ile çalıştırır."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(test_code)
            tmp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", tmp_path, "-v"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return TestResult(
                passed=(result.returncode == 0),
                output=result.stdout + result.stderr,
                return_code=result.returncode,
            )
        finally:
            os.unlink(tmp_path)

    @staticmethod
    def _module_exists(module_name: str) -> bool:
        """Bir modülün import edilebilir olup olmadığını kontrol eder."""
        import importlib

        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False
