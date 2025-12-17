# Code analyzer for extracting methods from Python files
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MethodInfo:
    """Information about a method/function extracted from source code."""
    name: str
    source: str
    lineno: int
    end_lineno: int
    docstring: Optional[str] = None
    class_name: Optional[str] = None
    

class CodeAnalyzer:
    """Analyze Python source files to extract methods and functions."""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.source_code = self.file_path.read_text(encoding="utf-8")
        self.tree = ast.parse(self.source_code)
    
    def get_all_methods(self) -> List[MethodInfo]:
        """Extract all methods and functions from the file."""
        methods = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Check if it's a method inside a class
                class_name = self._find_parent_class(node)
                
                method_info = MethodInfo(
                    name=node.name,
                    source=self._get_source(node),
                    lineno=node.lineno,
                    end_lineno=node.end_lineno or node.lineno,
                    docstring=ast.get_docstring(node),
                    class_name=class_name,
                )
                methods.append(method_info)
        
        return methods
    
    def get_methods_by_name(self, names: List[str]) -> List[MethodInfo]:
        """Get specific methods by their names."""
        all_methods = self.get_all_methods()
        return [m for m in all_methods if m.name in names]
    
    def _find_parent_class(self, node: ast.AST) -> Optional[str]:
        """Find the parent class of a method if it exists."""
        for parent in ast.walk(self.tree):
            if isinstance(parent, ast.ClassDef):
                for child in ast.iter_child_nodes(parent):
                    if child is node:
                        return parent.name
        return None
    
    def _get_source(self, node: ast.AST) -> str:
        """Extract source code for a specific node."""
        lines = self.source_code.splitlines()
        start = node.lineno - 1
        end = node.end_lineno if node.end_lineno else node.lineno
        return "\n".join(lines[start:end])


def analyze_file(file_path: str, method_names: Optional[List[str]] = None) -> List[MethodInfo]:

    analyzer = CodeAnalyzer(file_path)
    
    if method_names:
        return analyzer.get_methods_by_name(method_names)
    return analyzer.get_all_methods()
