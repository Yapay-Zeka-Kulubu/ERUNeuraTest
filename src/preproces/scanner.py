"""
Benchmark projelerini tarayıp preprocess pipeline'ını çalıştıran modül.

benchmark/ altındaki her projeyi dolaşır, .py dosyalarını bulur,
ASTAnalyzer ile analiz eder, ComplexityCalculator ile skorlar,
MethodSelector ile 50 metot seçer ve JSONExporter ile dışa aktarır.
"""