from dataclasses import dataclass, field
from typing import List, Optional, Dict, Literal

@dataclass
class ComplexityMetrics:
    #Calculator tarafından doldurulan teknik skorlar.
    cyclomatic_complexity: int = 1
    cognitive_complexity: int = 0
    risk_level: Literal["LOW", "MODERATE", "HIGH", "VERY_HIGH"] = "LOW" #Microsoft standlarına göre

@dataclass
class MethodModel:
    name: str                           
    signature: str                      
    body: str                          

    module_name: str                   
    file_path: str                     
    start_line: int                    
    end_line: int                       
    class_name: Optional[str] = None    # Eğer bir sınıfın içindeyse sınıf adı

    is_async: bool = False              # 'async def' ise True olur.Fonksiyon 'beklemeli' çalışır 
    is_method: bool = False             # Bir class'a aitse True 
    return_type: Optional[str] = None  
    
    parameters: List[str] = field(default_factory=list)   # Parametre listesi 
    dependencies: List[str] = field(default_factory=list) # İçeride çağrılan kütüphaneler (Mocking için)
    decorators: List[str] = field(default_factory=list)   # @staticmethod, @auth gibi işaretçiler
    
    docstring: Optional[str] = None     # Metodun başındaki açıklama 
    
    complexity: ComplexityMetrics = field(default_factory=ComplexityMetrics)

    def to_dict(self) -> Dict:
        #Modeli gruplandırılmış bir dicte dönüştürür.
        return {
            "project_context": {
                "project_name": self.module_name,
                "file_path": self.file_path
            },
            "class_info": {
                "name": self.class_name,
                "is_method": self.is_method
            },
            "method_details": {
                "name": self.name,
                "is_async": self.is_async,
                "return_type": self.return_type,
                "parameters": self.parameters,
                "signature": self.signature,
                "body": self.body,
                "docstring": self.docstring,
                "lines": {"start": self.start_line, "end": self.end_line},
                "dependencies": self.dependencies,
                "decorators": self.decorators
            },
            "analysis_metrics": {
                "cyclomatic_complexity": self.complexity.cyclomatic_complexity,
                "cognitive_complexity": self.complexity.cognitive_complexity,
                "risk_level": self.complexity.risk_level
            }
        }