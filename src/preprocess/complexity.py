#ComplexityCalculator modülü metotların karmaşıklık değerlerini hesaplar
from radon.complexity import cc_visit
from cognitive_complexity.api import get_cognitive_complexity

class ComplexityCalculator:
    #Metotların karmaşıklık değerlerini hesaplayan sınıf

    def calculate(self, source_code):
        # Kaynak kodu stringe çevir
        code_text = self._normalize_code(source_code)
        
        # Boş kod kontrolü
        if not code_text or code_text.strip() == "":
            return self._default_result()
        
        try:
            # Cyclomatic Complexity hesapla
            cc_results = cc_visit(code_text)
            cc_val = cc_results[0].complexity if cc_results else 1
            
            # Cognitive Complexity hesapla
            cog_val = get_cognitive_complexity(code_text)
            
            # Toplam karmaşıklık
            total = cc_val + cog_val
            
            return {
                "cyclomatic_complexity": cc_val,
                "cognitive_complexity": cog_val,
                "risk_levels": {
                    "overall_risk": self._get_risk_label(total),
                    "cyclomatic_risk": self._get_cc_risk_label(cc_val)
                }
            }
        except Exception:
            # Hata durumunda varsayılan değerleri döner
            return self._default_result()
    
    def _normalize_code(self, source_code):
        # String gelirse direkt döner, nesne gelirse body'sini alır
        if isinstance(source_code, str):
            return source_code
        return getattr(source_code, 'body', str(source_code))
    
    def _get_risk_label(self, score):
        # Toplam skora göre risk seviyesi 
        if score <= 10:
            return "Düşük"
        elif score <= 20:
            return "Orta"
        elif score <= 50:
            return "Yüksek"
        else:
            return "Çok Yüksek"
    
    def _get_cc_risk_label(self, cc_score):
        # Cyclomatic skora göre risk seviyesi
        if cc_score <= 10:
            return "Düşük"
        elif cc_score <= 20:
            return "Orta"
        elif cc_score <= 50:
            return "Yüksek"
        else:
            return "Çok Yüksek"
    
    def _default_result(self):
        # Hata durumunda dönecek default değerler
        return {
            "cyclomatic_complexity": 1,
            "cognitive_complexity": 0,
            "risk_levels": {
                "overall_risk": "Düşük",
                "cyclomatic_risk": "Düşük"
            }
        }
