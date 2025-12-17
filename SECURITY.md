# Güvenlik Politikası

## Desteklenen Sürümler

| Sürüm | Destekleniyor |
| ----- | ------------- |
| 1.x   | ✅            |
| < 1.0 | ❌            |

## Güvenlik Açığı Bildirme

Bir güvenlik açığı keşfettiyseniz, lütfen **genel bir issue açmayın**.

Bunun yerine:

1. yapay-zeka-kulubu@erciyes.edu.tr adresine e-posta gönderin
2. Açığın detaylı açıklamasını paylaşın
3. Mümkünse, açığı yeniden oluşturma adımlarını belirtin

### Beklentiler

- 48 saat içinde ilk yanıt
- 7 gün içinde durum güncellemesi
- Açık kapatıldığında bilgilendirme

### Ödül

Bu proje şu anda bir bug bounty programı sunmamaktadır, ancak önemli güvenlik açıklarını bildirenlere teşekkür edilecek ve (onaylarıyla) kredi verilecektir.

## API Anahtarları

⚠️ **Uyarı:** GROQ_API_KEY değerini asla commit etmeyin.

`.env` dosyası `.gitignore`'a eklenmiştir. API anahtarlarını daima ortam değişkenleri veya secret manager ile yönetin.
