<div align="center">
	<h1>LinuxCop</h1>
	<b>A modern, mood-aware, multi-language AI copilot for your Linux terminal</b>
</div>

---

## Features

- **Natural Language & Mood:** Interact in English or Turkish; Copilot adapts its style (humorous, minimalist, explanatory, serious, learning) to your mood selection.
- **i18n:** Choose your interface and answer language (tr/en) at startup. All UI and system prompts adapt automatically.
- **API Key Management:** Add, delete, and switch between multiple Google Gemini API keys securely (stored at `~/.linuxcop_api_key`).
- **Memory:** Remembers the last 20 messages and important user facts for personalized, context-aware answers.
- **Packagable:** Ready for PyPI/conda with `pyproject.toml` and `requirements.txt`.
- **Advanced Tools:** File read/write, directory listing, Wikipedia & DuckDuckGo search, (image analysis coming soon).

---

## Installation

```fish
# Install dependencies
pip install -r requirements.txt

# (optional) Install as a package
pip install .
```

---

## Usage

```fish
# Start from terminal
python app.py session
# or if installed as a package
linuxcop session
```

### Mood & Language Selection
- On startup, select your language (tr/en) and mood. All answers and UI adapt automatically.

### API Key Management
- On first run, you will be prompted for your Google Gemini API key (stored securely).
- On subsequent runs, the key is loaded automatically.
- Manage keys with:
	```fish
	linuxcop apis        # List registered keys
	linuxcop add-api     # Add a new key
	linuxcop del-api     # Delete a key
	linuxcop switch-api  # Switch to another key
	```

---

## Project Structure

```
├─ src/
│  ├─ tools.py
│  ├─ i18n.py
│  ├─ session_start.py
│  ├─ get_api.py
├─ docs/
│  ├─ prompts/
│  │  ├─ system_prompt.md
│  │  └─ mood/
│  │      ├─ mizahi.md
│  │      ├─ minimalist.md
│  │      ├─ açıklayıcı.md
│  │      ├─ ciddi.md
│  │      ├─ eğitmen.md
│  ├─ memory/
│  │  ├─ agent/
│  │  │   └─ agent_memory.md
│  │  └─ system/
│  │      └─ system_history.json
├─ app.py
├─ requirements.txt
├─ pyproject.toml
└─ README.md
```

---

## Contributing & License

- MIT License.
- Contributions welcome! Feel free to submit PRs or share new moods/language files.

---

## Summary

**LinuxCop** is a modern, mood-aware, multi-language, memory-enabled AI assistant for your Linux terminal. It supports secure Google Gemini API key management, i18n, and is ready for packaging and distribution.
---

## Özellikler

- **Doğal Dil ile Terminal**: Komutları ve soruları Türkçe veya İngilizce yazabilirsin, Copilot uygun komutları üretir ve çalıştırır.
- **Gelişmiş Dosya Araçları**: Dosya okuma/yazma, dizin listeleme, dosya arama, taşıma, silme gibi işlemler.
- **Wikipedia & Web Arama**: Wikipedia ve DuckDuckGo üzerinden bilgi sorgulama.
- **Görsel Analiz**: !img makrosu ile görsel gönderip analiz ettirebilirsin (Gemini Pro ile).
- **Kapsamlı Sistem Bilgisi**: Oturum başında sistem özetini otomatik gösterir.
- **Güvenli ve Samimi Yanıtlar**: system_prompt.md ile belirlenen sıcak, açıklayıcı ve güvenli yanıt tarzı.

---

## Temel Dosyalar

- `app.py`: Ana uygulama. Typer ile komut satırı arayüzü sağlar. Sohbet geçmişi, görsel analizi ve komut yürütmeyi yönetir.
- `src/tools.py`: Tüm yardımcı araçlar burada tanımlı. Shell komutları, dosya işlemleri, Wikipedia/web arama, ekran görüntüsü gibi fonksiyonlar içerir.
- `docs/prompts/system_prompt.md`: Copilot'un kişiliği, güvenlik kuralları ve yanıt tarzı burada tanımlı.

---

## Kurulum

1. Gerekli Python paketlerini yükle:
	 ```fish
	 pip install -r requirements.txt
	 ```
2. `.env` dosyasına Google Gemini API anahtarını ekle:
	 ```env
	 GEMINI_API_KEY3=senin_anahtarın
	 ```
3. Uygulamayı başlat:
	 ```fish
	 python app.py session
	 ```

---

## Kullanım

Terminalde çalıştır:

```fish
python app.py session
```

### Komut Örnekleri

- Basit soru:
	> Diskimde en çok yer kaplayan klasör hangisi?
- Shell komutu:
	> ls -lh /var/log
- Dosya okuma:
	> src/tools.py dosyasının ilk 100 satırını oku
- Wikipedia araması:
	> Wikipedia'da "Linux çekirdeği" nedir?
- Görsel analizi:
	> !img ~/resim.png Bu görselde ne var?

---

## Klasör Yapısı

```
├─ src/
│  └─ tools.py
├─ docs/
│  └─ prompts/
│      └─ system_prompt.md
├─ .github/
│  └─ workflows/
│      └─ ci.yml
├─ .vscode/
│  └─ settings.json
├─ tests/
├─ app.py
├─ .env
├─ .editorconfig
├─ .gitignore
├─ LICENSE
├─ CHANGELOG.md
├─ CONTRIBUTING.md
├─ CODE_OF_CONDUCT.md
└─ README.md
```

---

## Katkı ve Lisans

- Katkı için `CONTRIBUTING.md` ve `CODE_OF_CONDUCT.md` dosyalarını inceleyin.
- MIT Lisansı ile sunulmaktadır.

---

## Notlar

- Proje, Google Gemini API ile çalışır. Anahtarınızı `.env` dosyasına eklemeyi unutmayın.
- Ekran görüntüsü alma özelliği KDE/Wayland + Spectacle gerektirir ve varsayılan olarak pasif durumdadır.

---

Her türlü öneri ve katkı için PR gönderebilirsin!
