# Generation Module

Bu modül, **Preprocess** aşamasından gelen metot bilgilerini kullanarak **büyük dil modelleri (LLM)** ile Python birim testleri üretir. Üretilen testler **Postprocess** modülüne aktarılarak tamamlanır.

## Pipeline Akışı

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  Preprocess │ ──► │  Generation │ ──► │  Postprocess │
│   (JSON)    │     │   (LLM)     │     │  (Validate)  │
└─────────────┘     └─────────────┘     └──────────────┘
```

## Girdi

Preprocess modülünden gelen JSON dosyaları kullanılır:
- Metot bilgileri (signature, body, docstring)
- Sınıf bilgileri (fields, other_methods)
- Complexity metrikleri

## Çıktı

Her metot için üretilen birim test kodu:
```python
# Generated test for: module.ClassName.method_name
import unittest
from module import ClassName

class TestClassName(unittest.TestCase):
    def test_method_name_case1(self):
        # Test implementation
        ...
```

---

## LLM Provider Mimarisi

> [!IMPORTANT]
> LLM sağlayıcıları **soyut sınıftan miras alınarak** genişletilebilir. Yeni sağlayıcılar kolayca eklenebilir.

### Temel Soyut Sınıf

```python
from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):
    """Tüm LLM sağlayıcıları için temel soyut sınıf."""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
    
    @abstractmethod
    def invoke(self, prompt: str) -> str:
        """Prompt gönderir ve yanıt alır."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Kullanılabilir modelleri listeler."""
        pass
```

### Mevcut Sağlayıcılar

```python
class OpenAIProvider(BaseLLMProvider):
    """OpenAI API entegrasyonu (GPT-4, GPT-3.5)."""
    
    def invoke(self, prompt: str) -> str:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def get_available_models(self) -> list[str]:
        return ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]


class GroqProvider(BaseLLMProvider):
    """Groq API entegrasyonu (Llama, Mixtral)."""
    
    def invoke(self, prompt: str) -> str:
        from groq import Groq
        client = Groq(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def get_available_models(self) -> list[str]:
        return ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]
```

### Yeni Sağlayıcı Ekleme

```python
class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude entegrasyonu."""
    
    def invoke(self, prompt: str) -> str:
        # Claude API implementasyonu
        pass
    
    def get_available_models(self) -> list[str]:
        return ["claude-3-opus", "claude-3-sonnet"]
```

### Factory Pattern ile Kullanım

```python
class LLMFactory:
    @staticmethod
    def create(provider: str, api_key: str, model: str) -> BaseLLMProvider:
        providers = {
            "openai": OpenAIProvider,
            "groq": GroqProvider,
        }
        return providers[provider](api_key, model)

# Kullanım
llm = LLMFactory.create("groq", "api_key", "llama-3.3-70b-versatile")
response = llm.invoke("Generate test for...")
```

---

## Strateji Mimarisi

> [!IMPORTANT]
> Test üretimi için **Strategy Pattern** kullanılarak farklı prompt stratejileri eklenebilir.

### Temel Arayüz

```python
from abc import ABC, abstractmethod

class GenerationStrategy(ABC):
    """Tüm test üretim stratejileri için temel arayüz."""
    
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm = llm_provider
    
    @abstractmethod
    def generate(self, method_info: dict) -> str:
        """Verilen metot bilgisinden test kodu üretir."""
        pass
    
    @abstractmethod
    def get_prompt(self, method_info: dict) -> str:
        """LLM için prompt oluşturur."""
        pass
```

### Mevcut Stratejiler

| Strateji | Açıklama |
|----------|----------|
| `BasicStrategy` | Temel prompt ile test üretimi |
| `FewShotStrategy` | Örnek testlerle zenginleştirilmiş prompt |
| `ChainOfThoughtStrategy` | Adım adım düşünme ile test üretimi |
| `ContextAwareStrategy` | Sınıf bağlamını kullanarak test üretimi |

---

## Postprocess ile İlişki

Generation modülü **ham test kodu** üretir. Bu kod:
1. Syntax hatası içerebilir
2. Import eksiklikleri olabilir
3. Çalıştırılamayabilir

**Postprocess** modülü bu sorunları çözer:
- Rule-based fixing (import, syntax)
- LLM feedback (runtime errors)
