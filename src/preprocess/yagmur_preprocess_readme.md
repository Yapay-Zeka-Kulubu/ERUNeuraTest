Preprocess Modülü: Kod Anatomisi ve Analitik

Bu modül, Python projelerini Abstract Syntax Tree (AST) kullanarak statik analize tabi tutar.
Kaynak kodun yapısal anatomisini çıkarır ve her bir metodu bağımsız bir veri modeli (MethodModel) haline getirir. Ardından bu modellere karmaşıklık (complexity) metrikleri eklenir.

Bu modülün amacı, kaynak kodu yapısal ve analiz edilebilir bir veri formatına dönüştürmektir. Böylece ileri seviye analiz, raporlama ve görselleştirme işlemleri yapılabilir.

Teknik Altyapı ve Bağımlılıklar
Bileşen	Açıklama	Kaynak
AST Parsing	Python kodunu hiyerarşik bir ağaç yapısına dönüştürür	ast (Built-in)
Veri Modelleme	Veri yapılarını standardize eder ve DTO sağlar	dataclasses
Tip İpuçları	Gelişmiş tip kontrolü ve statik analiz desteği sağlar	typing
Modül Mimarisi
src/preproces/
│
├── __init__.py      # Paket dışa aktarımı ve API yönetimi
├── models.py        # Veri yapıları (MethodModel & ComplexityMetrics)
└── analyzer.py      # AST tabanlı analiz motoru (ASTAnalyzer)
1. models.py — Veri Modelleri ve Şemalar

Bu dosya, analiz edilen verilerin hangi formatta saklanacağını ve nasıl temsil edileceğini tanımlar.

MethodModel

Her bir metot için oluşturulan bir kimlik kartıdır.

Veriler dört ana kategori altında gruplanır:

project_context → Proje ve dosya bilgileri

class_info → Metodun ait olduğu sınıf bilgisi

method_details → Metodun yapısal özellikleri

analysis_metrics → Karmaşıklık ve risk skorları

Önemli Metot

to_dict()

Bu metot, MethodModel nesnesini hiyerarşik bir sözlük yapısına dönüştürür.
Bu sayede analiz çıktıları JSON formatında kolayca dışa aktarılabilir.

ComplexityMetrics

Bu sınıf, bir metodun teknik zorluk ve bakım maliyeti ile ilgili metriklerini saklar.

Tutulan Metrikler
Metrik	Açıklama
cyclomatic_complexity	Kontrol akışının karmaşıklığını ölçer
cognitive_complexity	Kodun okunabilirlik ve anlaşılabilirlik seviyesini ölçer
risk_level	Karmaşıklık skoruna göre belirlenen risk seviyesi
Risk Seviyeleri
LOW
MODERATE
HIGH
VERY_HIGH
2. analyzer.py — AST Analiz Motoru

Bu modül, ham Python kodunu analiz ederek fonksiyonları ve metotları ayrıştırır.

ASTAnalyzer

Python kodunu AST kullanarak analiz eden ana analiz motorudur.

Metotların Görevleri
Metot	Görevi
_parse_code()	Kaynak kodu AST ağacına dönüştürür ve SyntaxError hatalarını yakalar
get_methods_info()	Dosyayı baştan sona tarar ve bağımsız fonksiyonları ile sınıf metotlarını tespit eder
_extract_method()	Bir metodun adı, gövdesi, satır numaraları, dekoratörleri ve tip ipuçlarını çıkarır
_build_signature()	def veya async def ayrımını yaparak metodun imzasını yeniden oluşturur
_find_dependencies()	Metot içerisinde çağrılan diğer fonksiyonları tespit ederek bağımlılıkları çıkarır
Çıktı Formatı (JSON Örneği)

Modül, analiz edilen her metot için yapısal bir JSON çıktısı üretir.

{
  "project_context": {
    "project_name": "auth_module",
    "file_path": "src/auth.py"
  },
  "class_info": {
    "name": "UserAuth",
    "is_method": true
  },
  "method_details": {
    "name": "login",
    "is_async": true,
    "return_type": "bool",
    "parameters": ["self", "username", "password"],
    "signature": "async def login(self, username: str, password: str) -> bool",
    "body": "async def login(self, username: str, password: str) -> bool:\n    ...",
    "docstring": "Kullanıcı girişini kontrol eden asenkron metot.",
    "lines": { "start": 45, "end": 58 },
    "dependencies": ["check_password", "db_connect"],
    "decorators": ["@validate_input"]
  },
  "analysis_metrics": {
    "cyclomatic_complexity": 3,
    "cognitive_complexity": 2,
    "risk_level": "LOW"
  }
}
İşlem Akış Algoritması (Pipeline)

Modül analiz sürecini çok aşamalı bir işlem hattı ile gerçekleştirir.

1️⃣ Initialization (Başlatma)

ASTAnalyzer, analiz edilecek ham kaynak kod ile başlatılır.

2️⃣ Parsing (Ayrıştırma)

Python kodu, ast kütüphanesi kullanılarak AST ağaç yapısına dönüştürülür.

3️⃣ Discovery (Keşif)

AST ağacı üzerinde dolaşılarak şu düğümler tespit edilir:

FunctionDef

AsyncFunctionDef

ClassDef

4️⃣ Metadata Extraction (Veri Ayıklama)

Tespit edilen her metottan aşağıdaki bilgiler çıkarılır:

satır numaraları

parametreler

dekoratörler

dönüş tipi

metot gövdesi

bağımlılıklar

5️⃣ Model Mapping (Modelleme)

Elde edilen tüm bilgiler bir MethodModel nesnesine dönüştürülür ve analiz sonuçları liste halinde döndürülür.