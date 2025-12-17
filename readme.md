# ERUNeuraTest

**LLM tabanlı otomatik Python birim test üretimi framework'ü.**

Groq API üzerinden LLM kullanarak Python kodlarınız için pytest testleri üretir ve Pass@k metriği ile değerlendirir.

## 🚀 Hızlı Başlangıç

```bash
# 1. Sanal ortamı aktifleştir
.venv\Scripts\activate

# 2. API key ayarla
set GROQ_API_KEY=your_key_here
set GROQ_MODEL=llama-3.3-70b-versatile

# 3. Kendi dosyanız için test üret
python -m src.main test --file your_code.py --output tests/
```

## 📋 Framework Kullanımı

### Kendi Projeniz İçin Test Üretme

```bash
# Tüm metotlar için test üret
python -m src.main test --file src/mymodule.py --output tests/

# Belirli metotlar için
python -m src.main test --file src/mymodule.py --output tests/ --methods calculate_sum validate_input

# Sadece test üret, çalıştırma (hızlı mod)
python -m src.main test --file src/mymodule.py --output tests/ --no-eval
```

### Çıktı
```
🧪 ERUNeuraTest Framework
   Source: src/mymodule.py
   Output: tests/
📝 Found 3 methods to test

==================================================
📊 Results
==================================================
   Methods tested: 3
   Tests passed:   2
   Tests failed:   1
   Pass@1:         66.67%

✅ Tests saved to: tests/
```

## 📊 Metrikler

| Metrik | Açıklama |
|--------|----------|
| **Pass@1** | Tek denemede tüm testleri geçme oranı |
| **Pass@k** | k deneme içinde başarı oranı |
| **Methods Tested** | Test edilen metot sayısı |
| **Pass Rate** | Genel başarı yüzdesi |

### Benchmark Sonuçları (LeetCode-Contest)

| Model | Pass@1 |
|-------|--------|
| llama-3.3-70b-versatile | Test üretimi başarılı |

## 🔧 CLI Komutları

| Komut | Açıklama |
|-------|----------|
| `test` | Proje dosyaları için test üret |
| `generate` | Benchmark veri setinden test üret |
| `evaluate` | Üretilen testleri değerlendir |
| `download` | Benchmark indir |
| `list` | Mevcut benchmark'ları listele |

## 📁 Proje Yapısı

```
ERUNeuraTest/
├── src/
│   ├── config.py         # Konfigürasyon
│   ├── llm_client.py     # Groq API
│   ├── code_analyzer.py  # AST ile kod analizi
│   ├── framework.py      # Framework runner
│   ├── test_generator.py # Test üretici
│   ├── metrics.py        # Pass@k hesaplama
│   └── main.py           # CLI
├── benchmark/            # Benchmark veri setleri
├── examples/             # Örnek dosyalar
└── requirements.txt
```

## 📚 Desteklenen Benchmark'lar

| Benchmark | Amaç |
|-----------|------|
| LeetCode-Contest | Algoritma problemleri (180 soru) |
| ProjectTest | Gerçek dünya projeleri |
| ULT | Veri kirliliğinden arındırılmış |
| DevEval | Repo seviyesi değerlendirme |

## ⚙️ Gereksinimler

```
groq>=0.37.0
datasets>=2.16.0
numpy>=1.26.0
pytest>=7.4.0
```

## License

Apache 2.0
