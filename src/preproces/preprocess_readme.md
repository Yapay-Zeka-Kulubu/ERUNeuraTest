# Preprocess Module

Bu modül benchmark projelerini işleyerek her projeden **50 metot** seçer ve JSON formatında çıktı üretir.
Modülde yazılan sınıf ve metotlar bu readme.md dosyasının altında kısaca açıklanır.

## Çıktı Formatı

Çıktı dosyası `preprocess/selected_methods/` klasörüne kaydedilir. Her metot için aşağıdaki bilgiler elde edilir:


```json
{
  "project": {
    "name": "project_name",
  },
  "file": {
    "name": "file.py",
    "path": "absolute/path/to/file.py"
  },
  "class": {
    "name": "ClassName",
    "module": "module.name",
    "fqn": "module.name.ClassName",
    "docstring": "Class documentation...",
    "bases": ["BaseClass"],
    "modifiers": ["public"]
  },
  "method": {
    "name": "method_name",
    "signature": "def method_name(self, param: str) -> bool",
    "fqn": "module.name.ClassName.method_name",
    "return_type": "bool",
    "parameters": [
      {"name": "param", "type": "str"}
    ],
    "modifiers": ["public"],
    "docstring": "Method documentation...",
    "body": "def method_name(self, param):\n    return True",
    "start_line": 10,
    "end_line": 12
  },
  "complexity": {
    "cyclomatic_complexity": 2,
    "cognitive_complexity": 1,
    "lines_of_code": 3,
    "risk_levels": {
      "cc_risk": "LOW",
      "overall_risk": "LOW"
    }
  },
  "class_fields": [...],
  "other_methods": [...]
}
```

## Seçim Kriterleri

- Her projeden **50 metot** seçilir
- Cyclomatic complexity ve cognitive complexity hesaplanır
- Risk seviyeleri belirlenir


