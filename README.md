# Proje Adı

Bu depo, modern GitHub proje standartlarına uyumlu bir başlangıç klasör yapısı ile oluşturulmuştur. Aşağıdaki yapıyı temel alır:

- `src/`: Uygulama kaynak kodu
- `tests/`: Test dosyaları
- `docs/`: Dokümantasyon
- `.github/workflows/`: CI/CD iş akışları
- `.vscode/`: VS Code ayarları

## Hızlı Başlangıç

1. Proje adını ve açıklamasını bu dosyada güncelleyin.
2. Lisans ve katkı yönergelerini gözden geçirin.
3. `src/` ve `tests/` klasörlerini kendi dilinize/çerçevenize göre yapılandırın.

## Gereksinimler

- Git 2.40+
- VS Code (opsiyonel)

## GitHub'a Gönderme (fish shell)

```
# Yerel repo başlatma
git init
git add .
git commit -m "chore: initial project skeleton"

# Uzaktan repo ekleme (örnek)
git branch -M main
git remote add origin https://github.com/<kullanici>/<repo>.git
git push -u origin main
```

## Klasör Yapısı

```
├─ src/
├─ tests/
├─ docs/
├─ .github/
│  └─ workflows/
├─ .vscode/
├─ .editorconfig
├─ .gitignore
├─ LICENSE
├─ CHANGELOG.md
├─ CONTRIBUTING.md
├─ CODE_OF_CONDUCT.md
└─ README.md
```

## CI

GitHub Actions ile basit bir doğrulama iş akışı sağlanır. Dosyayı `.github/workflows/ci.yml` altında bulabilirsiniz ve dilinize göre uyarlayabilirsiniz.

## Katkı

Lütfen `CONTRIBUTING.md` ve `CODE_OF_CONDUCT.md` dosyalarını okuyun.
