from rich.console import Console
from pathlib import Path
from typing import Dict, List
import subprocess
import os

console = Console()

HISTORY: List = []

lang: str = "tr"

BASE_DIR = Path(__file__).resolve().parent.parent

MESSAGES: Dict[str, Dict[str, str]] = {
    "tr": {
        "session_title": "🧠 Linux Copilot Oturumu",
        "exit_hint": "Çıkmak için 'exit' veya 'quit' yaz.",
        "img_hint": "!img 'dosya_yolu' [soru] makrosu ile resim gönderebilirsiniz. (Geçici olarak devre dışı)",
        "system_loaded": "📦 Sistem bilgisi yüklendi.",
        "choose_mood": "Konuşma tarzı seçin:",
        "chosen_mood": "Seçilen mood",
        "respond_in_lang": "Lütfen tüm yanıtlarını Türkçe ver.",
        "history_content": "Sistemde duran önceki mesajlar:",
        "macros": "Sistemde kayıtlı macrolar:",
        "mood_selected": "Kullanıcı {mood} tarzında konuşmanı istedi. İşte {mood} moodunun tanıtımı:",
        "session_end": "Oturum sonlandırıldı.",
        "resp_err": "⚠️ Modelden geçerli bir yanıt alınamadı.",
        "response": "🤖 Yanıt",
        "terminate": "Oturum manuel olarak sonlandırıldı (Ctrl+C).",
        "err": "Hata:",
        "f_not_found": "HATA: system_prompt.md dosyası bulunamadı. Lütfen oluşturun.",
        "get_key": "Google Gemini API anahtarınızı girin:",
        "empty_key": "API anahtarı yuvası boş:",
        "found_key": "Geçerli Gemini API anahtarı bulundu.",
        "not_found": "Hiç API anahtarı bulunamadı.",
        "no_keys": "Hiç API anahtarı bulunamadı.",
        "list_keys": "Kayıtlı API Anahtarları:",
        "empty": "boş",
        "new_key_prompt": "Yeni API anahtarı girin",
        "key_saved": "Anahtar kaydedildi",
        "all_full": "Tüm slotlar dolu! Önce birini silin.",
        "delete_prompt": "Silmek istediğiniz anahtarın numarasını girin",
        "key_deleted": "Anahtar silindi",
        "slot_empty": "Bu slot zaten boş.",
        "invalid_slot": "Geçersiz slot numarası.",
        "invalid_input": "Geçersiz giriş.",
        "using_key": "Aktif API anahtarı kullanılıyor",
        "switched_to": "Yeni aktif API anahtarı seçildi",
        "no_other_keys": "Kullanılabilir başka anahtar yok.",
        "execute": "Çalıştırılıyor",
    },
    "en": {
        "session_title": "🧠 Linux Copilot Session",
        "exit_hint": "Type 'exit' or 'quit' to leave.",
        "img_hint": "You can send an image with !img 'file_path' [question]. (Temporarily disabled)",
        "system_loaded": "📦 System info loaded.",
        "choose_mood": "Choose a conversation style:",
        "chosen_mood": "Chosen mood",
        "respond_in_lang": "Please respond in English for all answers.",
        "history_content": "Last messages on this system:",
        "macros": "Macros saved in the system:",
        "mood_selected": "The user requested you to speak in {mood} style. Here is an introduction to the {mood} mood:",
        "session_end": "Session ended.",
        "resp_err": "⚠️ No valid response was received from the model.",
        "response": "🤖 Response",
        "terminate": "The session was manually terminated (Ctrl+C).",
        "err": "Error:",
        "f_not_found": "ERROR: The system_prompt.md file could not be found. Please create it.",
        "get_key": "Please enter your Google Gemini API key:",
        "empty_key": "API key slot is empty:",
        "not_found": "No API key found.",
        "no_keys": "No API key found.",
        "found_key": "A valid Gemini API key has been found.",
        "list_keys": "Registered API Keys:",
        "empty": "empty",
        "new_key_prompt": "Enter new API key",
        "key_saved": "Key saved",
        "all_full": "All slots are full! Please delete one first.",
        "delete_prompt": "Enter the number of the key to delete",
        "key_deleted": "Key deleted",
        "slot_empty": "That slot is already empty.",
        "invalid_slot": "Invalid slot number.",
        "invalid_input": "Invalid input.",
        "using_key": "Using active API key",
        "switched_to": "Switched to new active API key",
        "no_other_keys": "No other available API keys.",
        "execute": "Executing",
    },
}

MOODS = {
    "tr": {
        "açıklayıcı": "açıklayıcı",
        "ciddi": "ciddi",
        "eğitmen": "eğitmen",
        "minimalist": "minimalist",
        "mizahi": "mizahi",
    },
    "en": {
        "explanatory": "açıklayıcı",
        "serious": "ciddi",
        "learning": "eğitmen",
        "minimalist": "minimalist",
        "humorous": "mizahi",
    },
}


def t(language: str, key: str) -> str:
    """Translate key to given language; fallback to English."""
    table = MESSAGES.get(language) or MESSAGES["en"]
    return table.get(key, MESSAGES["en"].get(key, key))


def get_fastfetch_summary() -> str:
    """Returns a short fastfetch output for LLM context."""
    try:
        res = subprocess.run(
            "fastfetch --logo none",
            shell=True,
            text=True,
            capture_output=True,
            timeout=5
        )
        return "Sistem özellikleri: " + (res.stdout.strip() or "(fastfetch output unavailable)")
    except Exception:
        return "(fastfetch not installed)"

CMD_LOG = Path.home() / ".linuxcopilot_cmdlog.json"
