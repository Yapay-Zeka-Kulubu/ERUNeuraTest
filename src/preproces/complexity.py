from radon.complexity import cc_visit
from cognitive_complexity.api import get_cognitive_complexity

class ComplexityCalculator:
    def calculate(self, source_code):
        # 1. Girdi kontrolü: Nesne gelirse body'sini al, string gelirse direkt kullan
        code_text = source_code
        if not isinstance(source_code, str):
            code_text = getattr(source_code, 'body', str(source_code))

        # Eğer hala boşsa veya geçersizse varsayılan değer dön (Çökmeyi önler)
        if not code_text or code_text.strip() == "" or code_text == "None":
            return self._default_result()

        try:
            # 2. Karmaşıklık hesapla
            cc_results = cc_visit(code_text)
            cc_val = cc_results[0].complexity if cc_results else 1
            
            cog_val = get_cognitive_complexity(code_text)
            
            total = cc_val + cog_val
            return {
                "cyclomatic_complexity": cc_val,
                "cognitive_complexity": cog_val,
                "risk_levels": {"overall_risk": self._get_risk_label(total)}
            }
        except Exception:
            # Herhangi bir hatada 'None' yerine güvenli bir sözlük dön
            return self._default_result()

    def _get_risk_label(self, score):
        if score <= 10: return "Düşük (LOW)"
        if score <= 20: return "Orta (MEDIUM)"
        return "Yüksek (HIGH)"

    def _default_result(self):
        return {
            "cyclomatic_complexity": 1,
            "cognitive_complexity": 0,
            "risk_levels": {"overall_risk": "Düşük (Minimal)"}
        }