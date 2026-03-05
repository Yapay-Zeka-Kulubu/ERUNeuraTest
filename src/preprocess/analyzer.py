#ASTAnaliz modülü kaynak kodunu analiz ederek metot ve sınıf bilgilerini çıkaran sınıfı içerir
import ast
from dataclasses import dataclass, field
from src.preprocess.models import MethodModel

@dataclass
class ASTAnalyzer:
    source_code: str
    module_name: str = "unknown"
    file_path: str = "unknown"
    
    def _parse_code(self):
        try:
            return ast.parse(self.source_code)
        except SyntaxError:
            print(f"Sözdizimi hatasi: {self.module_name}")
            return None

    def get_methods_info(self):
        #Kod içindeki tüm fonksiyon ve metotları bulup MethodModel listesi döner.
        methods = []
        tree = self._parse_code()       
        if not tree:
            return methods
        for node in tree.body:
            # Sınıf dışındaki bağımsız fonksiyonlar
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._extract_method(node))           
            # Sınıf içindeki metotlar
            elif isinstance(node, ast.ClassDef):
                class_name = node.name
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods.append(self._extract_method(item, class_name))
        return methods

    def _extract_method(self, node, class_name=None):
        # Tek bir metot için bilgileri çıkarır
        name = node.name
        signature = self._build_signature(node)
        body = ast.get_source_segment(self.source_code, node) or ""
        
        module_name = self.module_name
        file_path = self.file_path
        start_line = node.lineno
        end_line = node.end_lineno
        class_name = class_name
        
        is_async = isinstance(node, ast.AsyncFunctionDef)
        is_method = class_name is not None
        return_type = ast.unparse(node.returns) if node.returns else None
        
        parameters = [arg.arg for arg in node.args.args]
        dependencies = self._find_dependencies(node)
        decorators = [ast.unparse(d) for d in node.decorator_list]
        
        docstring = ast.get_docstring(node)

        return MethodModel(
            name=name,
            signature=signature,
            body=body,
            module_name=module_name,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            class_name=class_name,
            is_async=is_async,
            is_method=is_method,
            return_type=return_type,
            parameters=parameters,
            dependencies=dependencies,
            decorators=decorators,
            docstring=docstring
        )

    def _build_signature(self, node):
        #Metot imzasını tip ipuçlarıyla  birlikte alır.
        # ast.unparse() metodu, AST düğümünü tekrar Python koduna çevirir.
        args_str = ast.unparse(node.args)
        returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
        prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
        return f"{prefix} {node.name}({args_str}){returns}"
    
    def _find_dependencies(self, node):
        #Metot içinde çağrılan diğer fonksiyonları bulur (Mocking için).
        calls = []
        # ast.walk(node) ile fonksiyonun içindeki tüm kod satırlarını tek tek gezeriz
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        return list(set(calls))