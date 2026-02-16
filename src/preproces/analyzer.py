import ast


class ASTAnalyzer:
    """
    Python kaynak kodunu analiz ederek metot ve sınıf bilgilerini çıkaran sınıf.
    """

    def __init__(self, source_code):
        self.source_code = source_code
        try:
            # Kodu Soyut Sözdizimi Ağacı'na (AST) dönüştürür
            self.tree = ast.parse(source_code)
        except SyntaxError:
            self.tree = None

    def get_methods_info(self):
        """
        Kod içerisindeki tüm fonksiyon ve metotları analiz eder.
        """
        methods = []

        if not self.tree:
            return methods

        for node in ast.walk(self.tree):
            # Sadece fonksiyon tanımlarını yakala
            if isinstance(node, ast.FunctionDef):
                method_data = {
                    "name": node.name,
                    "signature": self._build_signature(node),
                    "body": ast.get_source_segment(self.source_code, node),
                    "start_line": node.lineno,
                    "end_line": node.end_lineno,
                }
                methods.append(method_data)

        return methods

    def _build_signature(self, node):
        """
        Fonksiyonun imzasını (def name(args)) oluşturur.
        """
        args = [arg.arg for arg in node.args.args]
        signature = f"def {node.name}({', '.join(args)})"
        return signature
