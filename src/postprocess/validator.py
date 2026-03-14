"""
CodeValidator

LLM tarafından üretilen test kodunu çalıştırmadan önce kontrol eder.

Kontrol edilen başlıca konular:

1) Syntax kontrolü
2) Eksik import tespiti
3) Basit kural tabanlı test kontrolleri

Sonuçlar ValidationResult nesnesi içinde döndürülür.
"""

import ast
import builtins


class ValidationResult:
    def __init__(self, is_valid=True, errors=None, warnings=None):
        self.is_valid = is_valid
        self.errors = errors if errors is not None else []
        self.warnings = warnings if warnings is not None else []

    def add_error(self, message):
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message):
        self.warnings.append(message)

    def merge(self, other):
        if not other.is_valid:
            self.is_valid = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)

    def __repr__(self):
        return(
            f"ValidationResult("
            f"is_valid={self.is_valid},"
            f"errors={self.errors}, "
            f"warnings={self.warnings})"
        )

class CodeValidator:
    COMMON_EXTERNALS = {
        "pytest": "pytest",
        "np": "numpy",
        "pd": "pandas",
    }

    COMMON_IMPORT_HINTS = {
        "patch": "from unittest.mock import patch",
        "Mock": "from unittest.mock import Mock",
        "MagicMock": "from unittest.mock import MagicMock",
        "datetime": "import datetime",
        "timedelta": "from datetime import timedelta",
        "Path": "from pathlib import Path",
        "os": "import os",
        "sys": "import sys",
        "math": "import math",
        "json": "import json",
        "re": "import re",
    }

    def validate(self, code:str) -> ValidationResult:
        final_result = ValidationResult()

        syntax_result = self.validate_syntax(code)
        final_result.merge(syntax_result)

        if not syntax_result.is_valid:
            return final_result

        import_result = self.validate_imports(code)
        final_result.merge(import_result)

        rule_result = self.validate_rule_based(code)
        final_result.merge(rule_result)

        return final_result

    def validate_syntax(self, code:str) -> ValidationResult:
        result  = ValidationResult()

        try:
            ast.parse(code)
        except SyntaxError as e:
            line = e.lineno if e.lineno is not None else "unknown"
            column = e.offset if e.offset is not None else "unknown"
            message = e.msg if e.msg else "invalid syntax"

            result.add_error(
            f"SyntaxError at line {line}, column {column}: {message}"
        )
        return result

    def validate_imports(self, code: str) -> ValidationResult:
        result = ValidationResult()

        try:
            tree = ast.parse(code)
        except SyntaxError: 
            result.add_error("Import validation skipped because syntax is invalid.")
            return result    

        imported_modules, imported_names = self._collect_imports(tree)
        used_names = self._collect_used_names(tree)

        missing_messages = self._detect_missing_imports(
            imported_modules = imported_modules,
            imported_names = imported_names,
            used_names = used_names,
        )

        for message in missing_messages:
            result.add_warning(message)

        return result
    
    def validate_rule_based(self, code:str) -> ValidationResult:
        result = ValidationResult()

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return result
        
        test_functions = [
            node for node in tree.body 
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        ]

        if not test_functions:
            result.add_warning(
                "No test function found. Expected at least one function starting with 'test_'."
            )

        if "assert" not in code and "pytest.raises" not in code:
            result.add_warning(
                "No assertion pattern found. Test code may be incomplete."
            )

        return result

    def _collect_imports(self, tree:ast.AST) -> tuple[set[str], set[str]]:
        imported_modules = set()
        imported_names = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules.add(alias.name.split(".")[0])

                    if alias.asname:
                        imported_names.add(alias.asname)
                    else:
                        imported_names.add(alias.name.split(".")[0])

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_modules.add(node.module.split(".")[0])

                for alias in node.names:
                    imported_names.add(alias.asname or alias.name)

        return imported_modules, imported_names

    def _collect_used_names(self, tree:ast.AST) -> set[str]:
        used_names = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            
            elif isinstance(node, ast.Attribute):
                current = node
                while isinstance(current, ast.Attribute):
                    current = current.value

                if isinstance(current,ast.Name):
                    used_names.add(current.id)

        return used_names

    def _detect_missing_imports(
            self,
            imported_modules:set[str],
            imported_names:set[str],
            used_names:set[str],
        ) -> list[str]:

        messages = []

        available_names = imported_modules | imported_names | set(dir(builtins))

        for used in used_names:
            if used in self.COMMON_EXTERNALS:
                expected_module = self.COMMON_EXTERNALS[used]
                if used not in available_names and expected_module not in imported_modules:
                    messages.append(
                        f"Possible missing import: '{used}' is used but '{expected_module}' does not appear to be imported."
                    )

        for used in used_names:
            if used in self.COMMON_IMPORT_HINTS and used not in available_names:
                messages.append(
                    f"Possible missing import: '{used}' is used but not imported. Suggested import: {self.COMMON_IMPORT_HINTS[used]}"
                )
        
        return messages