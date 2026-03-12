# LLM’in ürettiği test kodunu çalıştırmadan önce kontrol etmek. 
# Bu dosya aslında yazılan kodları kontrol eden bir kontrolcü gibi düşünülebilir

#ValidationResult : Bir sonuç nesnesidir. "geçerli mi","hangi hatalar var","hangi uyarılar var" bilgilerini döndürür.

"""
ValidationResult(
    is_valid=False, #Kod çalışabilir mi ?
    errors=["SyntaxError at line 3"], #hatalar
    warnings=[] #çalışır ama risk var
)
"""

#validate_syntax: Yazım kuralları olarak geçer. if kontrolunden hemen sonra ":" koymamak. ->ast.parse

#Hata mesajını satır numarasıyla vermek : "SyntaxError at line 2 column 18: '(' was never closed" gibi raporlamak

#validate_imports : LLM kod üretir ama kütüphaneyi eklemez -> NameError: pytest is not defined

#Kural tabanlı düzeltme : Rule Based(Önceden belirlenmiş kurallar) Deterministic Programming'tir.
"""
kural 1 → pytest kullanılmış ama import yok
kural 2 → test fonksiyon adı test_ ile başlamalı
...
"""

import ast
import builtins


class ValidationResult:
    def __init__(self, is_valid=True, errors=None, warnings=None):
        self.is_valid = is_valid
        self.errors = errors if errors is not None else [] #her result için ayrı liste oluşturuyoruz.
        self.warnings = warnings if warnings is not None else []

    #Hata mesajını ekliyor ve hata oldugu için is_valid degerini False yapıyor.
    def add_errors(self, message):
        self.errors.append(message)
        self.is_valid = False

    #Uyarılar programı bozmaz, o yüzden sadece bilgi verir, is_Valid'i degiştirmeye geerk yok.
    def add_warnings(self, message):
        self.warnings.append(message)

    #Validator içinde şu yapılar olabilir: validate_syntax(),validate_imports(),validate_style() Biz bunları tek bir şekilde raporlamak için birleştiriyoruz.
    def merge(self, other):
        if not other.is_valid:
            self.is_valid = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)

    #Tamamen okunabilirlik.
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

    def validate(self, code:str) -> ValidationResult: #code str olmalı ve fonk. ValRes nesnesi döndürmeli
        final_result = ValidationResult() #ana sonuç nesnesi, en son bu döndürülecek

        syntax_result = self.validate_syntax(code) #syntax kontrolu
        final_result.merge(syntax_result) #syntax sonucunu ana sonuca ekliyoruz

        if not syntax_result.is_valid: #syntax bozuksa diger analizleri yapmak mantıksız
            return final_result

        import_result = self.validate_imports(code) #kodda kullanılan ama import edilmemiş kütüphane ve fonkiyonları kontrol eder.
        final_result.merge(import_result)

        rule_result = self.validate_rule_based(code) #kurallara uyup uymadıgını kontrol eder.
        final_result.merge(rule_result)

        return final_result

    #koun python syntaxının geçerli olup olmadıgını kontrol eder. 
    def validate_syntax(self, code:str) -> ValidationResult:
        result  = ValidationResult()

        try:
            ast.parse(code) #abstract syntax tree, bir şey döndürmez, kodun syntaxına bakar.
        except SyntaxError as e: #eger syntax error olursa
            line = e.lineno if e.lineno is not None else "unknown" #kaçıncı satır
            column = e.offset if e.offset is not None else "unknown"#kaçıncı sütun
            message = e.msg if e.msg else "invalid syntax" #hata mesajı

            result.add_errors( #error listeye ekle ve is_valid = False yap
            f"SyntaxError at line {line}, column {column}: {message}"
        )
        return result

    #Bu kusursuz degildir, sezgiseldir.
    def validate_imports(self, code: str) -> ValidationResult:
        result = ValidationResult()

        try:
            tree = ast.parse(code) #önce syntax olarak dogru mu bunu kontrol etmemiz gerekiyor.
        except SyntaxError: 
            result.add_errors("Import validation skipped because syntax is invalid.")
            return result    

        imported_modules, imported_names = self._collect_imports(tree) #import edilen modulleri ve isimleri toplar
        used_names = self._collect_used_names(tree) #kod içinde kullanılan isimleri toplar

        missing_messages = self._detect_missing_imports( #toplanan verileri karşılaştırır.
            imported_modules = imported_modules,
            imported_names = imported_names,
            used_names = used_names,
        )

        for message in missing_messages:
            result.add_warnings(message)

        return result
    
    #kural tabanlı kontrol yapar.Mesela _test ile başlayan fonk. var mı? assert var mı gibi kontroller yapılabilir
    #ŞUAN İÇİN BU FONKSİYON ÇOK YÜZEYSEL.
    def validate_rule_based(self, code:str) -> ValidationResult:
        result = ValidationResult()

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return result
        
        #tüm fonksiyonları tarar, test_ ile başlayanları liste içine atar.
        test_functions = [
            node for node in tree.body 
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        ]

        #liste boşsa test_ ile başlayan fonk. yoktur.
        if not test_functions:
            result.add_warnings(
                "No test function found. Expected at least one function starting with 'test_'."
            )

        #assert veya pytest.raises yoksa test anlamsızdır. Bunun kontrolu yapılıyor.
        if "assert" not in code and "pytest.raises" not in code:
            result.add_warnings(
                "No assertion pattern found. Test code may be incomplete."
            )

        return result

    #ATS'deki kodlarda hangi importların yapıldıgını toplar. imported_modules, imported_names
    def _collect_imports(self, tree:ast.AST) -> tuple[set[str], set[str]]: #fonk. 2 set döndürüyor.
        imported_modules = set() #set olmasının sebebi tekrarı engellemek.
        imported_names = set()

        for node in ast.walk(tree): #ast içindeki tüm dügümleri dolaşır
            if isinstance(node, ast.Import):
                for alias in node.names: #import edilen parçaları tutar -> os,sys vb. import numpy as np -> name:"numpy" asname="py"
                    imported_modules.add(alias.name.split(".")[0]) #-> import package.submodule olursa alias.name="package.submodule" olur

                    if alias.asname: #import numpy as np 'de hangi alias'ı kullanacagımızı belirliyoruz
                        imported_names.add(alias.asname)
                    else:
                        imported_names.add(alias.name.split(".")[0])

            elif isinstance(node, ast.ImportFrom): #from X import Y kısmını yakalıyoruz.
                if node.module: #node.module X kısmıdır.
                    imported_modules.add(node.module.split(".")[0])

                for alias in node.names:
                    imported_names.add(alias.asname or alias.name) #kod içinde Y kullanılacak.

        return imported_modules, imported_names
        #from X import * durumu için bu fonksiyon zora girebilir.  
    """
    _collect_imports için somut örnek

    import os
    import numpy as np
    from math import sqrt
    from unittest.mock import patch as mock_patch


    imported_modules = {"os", "numpy", "math", "unittest"}
    imported_names = {"os", "np", "sqrt", "mock_patch"}


    """

    #kod içinde hangi isimlerin kullanıldıgını toplar
    def _collect_used_names(self, tree:ast.AST) -> set[str]:
        used_names = set()

        for node in ast.walk(tree): #AST içindeki tüm dügümleri dolaşır,biz burada Name ve Attribute ile ilgileniyoruz.
            if isinstance(node, ast.Name): #x,math,pytest,result vb
                used_names.add(node.id) #kodda doğrudan geçen tekil isimleri topluyor.
            
            elif isinstance(node, ast.Attribute): #math.sqrt,os.path.join,pytest.raises vb.
                current = node
                while isinstance(current, ast.Attribute):
                    current = current.value
                    #Attribute(attr="join", value=Attribute(attr="path", value=Name(id="os")))
                    #current = Attribute(attr="path", value=Name(id="os"))
                    #current = Name(id="os") -> "os"

                if isinstance(current,ast.Name):
                    used_names.add(current.id)

        return used_names

    #Kodda kullanılan isimlerden hangileri import edilmemiş olabilir.
    #Yani aslında şuna benzer bir mesaj listesi almak istiyoruz:
    #["Possible missing import: 'pytest' is used but 'pytest' does not appear to be imported.",
    #"Possible missing import: 'patch' is used but not imported. Suggested import: from unittest.mock import patch"]
    def _detect_missing_imports(
            self,
            imported_modules:set[str], #import edilen moduller
            imported_names:set[str], #import ile erişilebilen isimler
            used_names:set[str], #kod içinde kullanılan isimler
        ) -> list[str]:

        messages = []

        # | -> birleşim demek. Burada tüm isimler tek kümede birleştiriliyor.
        available_names = imported_modules | imported_names | set(dir(builtins))

        for used in used_names:
            if used in self.COMMON_EXTERNALS: #common_external içinde var mı ?
                expected_module = self.COMMON_EXTERNALS[used]
                if used not in available_names and expected_module not in imported_modules:
                    messages.append(
                        f"Possible missing import: '{used}' is used but '{expected_module}' does not appear to be imported."
                    )
        #pytest kullanılmış ama import pytest yok
        #np kullanılmış ama numpy veya import numpy as np tarzı bir şey yok. Bu durumlar için kulalnılır

        for used in used_names:
            if used in self.COMMON_IMPORT_HINTS and used not in available_names:
                messages.append(
                    f"Possible missing import: '{used}' is used but not imported. Suggested import: {self.COMMON_IMPORT_HINTS[used]}"
                )
        #“eksik olabilir” demiyor, “şu importu eklemeyi düşünebilirsin” diyor.
        
        return messages
    
#Genel anlamda burada şu iş yapılmış oluyor
# AST
# -> importları f, is_valid, er
# -> kullanılan isimleri topla
# -> farkı analiz et
# -> olası eksik import mesajlarını üret
# 
# 
# 
# 
# 
# 
#     
