# Postprocess Module

Bu modül, **Generation** aşamasından gelen ham test kodlarını **doğrular**, **düzeltir** ve **çalışır hale getirir**.

## Pipeline Akışı

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Generation │ ──► │   Postprocess    │ ──► │   Output    │
│  (Raw Code) │     │ (Fix & Validate) │     │ (Valid Test)│
└─────────────┘     └──────────────────┘     └─────────────┘
```

## Düzeltme Yaklaşımları

### 1. Rule-Based Fixing (Kural Tabanlı)

Otomatik olarak tespit edilip düzeltilebilen hatalar:

| Hata Türü | Düzeltme |
|-----------|----------|
| Import eksiklikleri | AST analizi ile otomatik import ekleme |
| Syntax hataları | Pattern matching ile düzeltme |
| İndentasyon hataları | Otomatik formatlama |
| Eksik test decorator | `@pytest.mark` veya `unittest` ekleme |

```python
class RuleBasedFixer:
    def fix_imports(self, code: str, method_info: dict) -> str:
        """Eksik importları tespit edip ekler."""
        pass
    
    def fix_syntax(self, code: str) -> str:
        """Basit syntax hatalarını düzeltir."""
        pass
    
    def fix_indentation(self, code: str) -> str:
        """İndentasyon hatalarını düzeltir."""
        pass
```

### 2. LLM Feedback (Geri Besleme)

Kural tabanlı düzeltilemeyen hatalar için LLM'e geri besleme yapılır:

```python
class LLMFeedbackFixer:
    def fix_with_error(self, code: str, error: str) -> str:
        """Hata mesajı ile LLM'den düzeltme ister."""
        prompt = f"""
        Aşağıdaki test kodu çalıştırıldığında hata aldı:
        
        Kod:
        {code}
        
        Hata:
        {error}
        
        Lütfen kodu düzelt.
        """
        return self.llm.invoke(prompt)
```

## Hata Kontrol Aşamaları

```
┌─────────────┐
│  Raw Code   │
└──────┬──────┘
       ▼
┌─────────────┐     ┌─────────────────┐
│ Syntax      │ ──► │ Rule-Based Fix  │
│ Check       │     │ (AST Parse)     │
└──────┬──────┘     └────────┬────────┘
       ▼                     │
┌─────────────┐              │
│ Compile     │ ◄────────────┘
│ Check       │
└──────┬──────┘
       ▼
┌─────────────┐     ┌─────────────────┐
│ Runtime     │ ──► │ LLM Feedback    │
│ Check       │     │ (Error + Code)  │
└──────┬──────┘     └────────┬────────┘
       ▼                     │
┌─────────────┐              │
│ Valid Test  │ ◄────────────┘
└─────────────┘
```

## Retry Mekanizması

> [!WARNING]
> Maksimum 3 deneme yapılır. Başarısız testler loglanır.

```python
MAX_RETRIES = 3

def process_test(code: str) -> TestResult:
    for attempt in range(MAX_RETRIES):
        # 1. Syntax kontrolü
        syntax_error = check_syntax(code)
        if syntax_error:
            code = rule_based_fix(code, syntax_error)
            continue
        
        # 2. Compile kontrolü
        compile_error = compile_check(code)
        if compile_error:
            code = rule_based_fix(code, compile_error)
            continue
        
        # 3. Runtime kontrolü
        runtime_error = run_test(code)
        if runtime_error:
            code = llm_feedback_fix(code, runtime_error)
            continue
        
        return TestResult(success=True, code=code)
    
    return TestResult(success=False, code=code)
```

## Çıktı

Başarılı testler `output/validated_tests/` klasörüne kaydedilir.
