from src import context
import os
import json
from pathlib import Path

MAX_KEYS = 5
KEY_FILE = Path.home() / ".linuxcop_api_keys"
ACTIVE_FILE = Path.home() / ".linuxcop_active_key"

def load_keys():
    """Kaydedilmiş API anahtarlarını JSON dosyasından yükler."""
    if KEY_FILE.exists():
        try:
            data = json.loads(KEY_FILE.read_text())
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return [None] * MAX_KEYS


def save_keys(keys):
    """Anahtar listesini JSON olarak kaydeder."""
    KEY_FILE.write_text(json.dumps(keys, indent=2))
    KEY_FILE.chmod(0o600)


def get_active_index():
    """Aktif anahtarın indeksini döndürür (yoksa 0)."""
    if ACTIVE_FILE.exists():
        try:
            return int(ACTIVE_FILE.read_text().strip())
        except Exception:
            pass
    return 0


def set_active_index(index: int):
    """Aktif anahtar indeksini kaydeder."""
    ACTIVE_FILE.write_text(str(index))
    ACTIVE_FILE.chmod(0o600)


def get_api_key() -> str:
    """Gemini API anahtarlarını sırayla dener, eksikleri kullanıcıdan ister."""
    keys = load_keys()

    for i in range(MAX_KEYS):
        env_name = f"GEMINI_API_KEY{i+1}" if i > 0 else "GEMINI_API_KEY"
        env_val = os.getenv(env_name)
        if env_val:
            keys[i] = env_val.strip()

    save_keys(keys)

    idx = get_active_index()

    if 0 <= idx < MAX_KEYS and keys[idx]:
        context.console.print(f"[green]✔ {context.t(context.lang, 'using_key')} #{idx+1}[/green]")
        return keys[idx]

    for i, key in enumerate(keys):
        if key:
            set_active_index(i)
            context.console.print(f"[green]✔ {context.t(context.lang, 'found_key')} (slot {i+1})[/green]")
            return key

    context.console.print("[red]❌ " + context.t(context.lang, "no_keys") + "[/red]")
    api = context.console.input(f"🔑 {context.t(context.lang, 'get_key')}: ").strip()
    keys[0] = api
    save_keys(keys)
    set_active_index(0)
    return api


def list_api_keys():
    """Kayıtlı API anahtarlarını listeler."""
    keys = load_keys()
    active_idx = get_active_index()
    context.console.print(f"\n[yellow]{context.t(context.lang, 'list_keys')}[/yellow]")
    for i, key in enumerate(keys, start=1):
        slot = f"{i}."
        prefix = "[cyan]*[/cyan]" if (i - 1) == active_idx else " "
        if key:
            masked = key[:6] + "..." + key[-4:]
            context.console.print(f"{prefix} {slot} {masked}")
        else:
            context.console.print(f"{prefix} {slot} [dim]<{context.t(context.lang, 'empty')}>[/dim]")
    context.console.print()


def add_api_key():
    """Yeni bir API anahtarı ekler."""
    keys = load_keys()
    for i in range(MAX_KEYS):
        if not keys[i]:
            val = context.console.input(f"{context.t(context.lang, 'new_key_prompt')} (slot {i+1}): ").strip()
            if val:
                keys[i] = val
                save_keys(keys)
                context.console.print(f"[green]✔ {context.t(context.lang, 'key_saved')} (slot {i+1})[/green]")
                return
    context.console.print(f"[red]⚠ {context.t(context.lang, 'all_full')}[/red]")


def delete_api_key():
    """Belirtilen API anahtarını siler."""
    keys = load_keys()
    list_api_keys()
    try:
        idx = int(context.console.input(f"{context.t(context.lang, 'delete_prompt')}: ").strip()) - 1
        if 0 <= idx < MAX_KEYS:
            if keys[idx]:
                keys[idx] = None
                save_keys(keys)
                context.console.print(f"[green]✔ {context.t(context.lang, 'key_deleted')} (slot {idx+1})[/green]")
                if get_active_index() == idx:
                    set_active_index(0)
            else:
                context.console.print(f"[yellow]{context.t(context.lang, 'slot_empty')}[/yellow]")
        else:
            context.console.print(f"[red]{context.t(context.lang, 'invalid_slot')}[/red]")
    except ValueError:
        context.console.print(f"[red]{context.t(context.lang, 'invalid_input')}[/red]")


def switch_api_key():
    """Aktif API anahtarını sıradakine geçirir."""
    keys = load_keys()
    active = get_active_index()

    for i in range(1, MAX_KEYS + 1):
        next_idx = (active + i) % MAX_KEYS
        if keys[next_idx]:
            set_active_index(next_idx)
            masked = keys[next_idx][:6] + "..." + keys[next_idx][-4:]
            context.console.print(f"[green]🔄 {context.t(context.lang, 'switched_to')} (#{next_idx+1}) → {masked}[/green]")
            return

    context.console.print(f"[red]{context.t(context.lang, 'no_other_keys')}[/red]")
