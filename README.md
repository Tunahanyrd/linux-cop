# 🐧 LinuxCop

**A mood-aware, multi-language AI copilot for your Linux terminal**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![AI](https://img.shields.io/badge/AI-Google%20Gemini-orange.svg)](https://ai.google/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚀 Quick Install

Run this single command to install **LinuxCop**:

```bash
bash <(curl -s https://raw.githubusercontent.com/Tunahanyrd/linux-cop/master/install.sh)
```

Once installation finishes, restart your terminal or run:

```bash
source ~/.bashrc
```

Then start your AI copilot:

```bash
cop session
```

---

## ✨ Highlights

| Feature                     | Description                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------- |
| 🌍 **Multi-language UI**    | English 🇬🇧 and Turkish 🇹🇷 interface support                                             |
| 🎭 **Mood System**          | Choose between 5 conversation styles (Humorous, Minimalist, Explanatory, Learning, Serious) |
| 🔑 **API Key Manager**      | Add, remove, list, and switch between multiple Gemini API keys                              |
| 🧠 **Persistent Memory**    | Remembers last conversations, saved facts, and user macros                                  |
| 🧰 **Command Execution**    | Runs real shell commands with persistent `bash` session                                     |
| 📚 **Integrated Knowledge** | Wikipedia & DuckDuckGo search tools                                                         |
| 💾 **File Tools**           | Read, write, move, delete, and search files safely                                          |
| 🔒 **Secure**               | Stores API keys locally with 0600 file permissions                                          |

---

## 💬 Example Interaction

```
👤 User: Show me my current directory
🤖 AI: [Executes `pwd` → /home/user/linux-cop]

👤 User: Go up one folder
🤖 AI: [Executes `cd ..` → persistent session kept]

👤 User: Search Wikipedia for “Linux kernel”
🤖 AI: [Fetches summary and displays it]
```

---

## 🧱 Project Structure

```
linux-cop/
├── app.py                 # Main entry point
├── install.sh             # One-line installer
├── requirements.txt
├── src/
│   ├── context.py         # Global context and translations
│   ├── get_api.py         # API key manager
│   ├── i18n.py            # Internationalization
│   ├── session_start.py   # Session handler & mood selection
│   └── tools.py           # Shell, memory, and AI tools
└── docs/
    ├── prompts/           # Mood and system prompts
    └── memory/            # Agent memory and macros
```

---

## 🧠 Memory System

* Saves last 20 messages to `docs/memory/system/system_history.json`
* User macros stored in `docs/memory/agent/user_macros.md`
* Agent learns user preferences dynamically

Example:

```
👤 User: Remember that I prefer Python over C++
🤖 AI: Got it — I’ll keep that in mind.
```

---

## 🎭 Moods

| Mood           | Description                     |
| -------------- | ------------------------------- |
| 😄 Humorous    | Casual and witty tone           |
| 📝 Minimalist  | Short, clean answers            |
| 📚 Explanatory | Detailed, educational responses |
| 🎓 Learning    | Step-by-step instructor mode    |
| 💼 Serious     | Professional tone               |

---

## 🔑 API Management

```bash
cop apis         # List all keys
cop add-api      # Add new key
cop del-api      # Delete a key
cop switch-api   # Switch to next available key
```

Stored securely in `~/.linuxcop_api_keys` (JSON).

---

## 🛠 Development

### Built With

* [Python 3.10+](https://python.org)
* [Typer](https://typer.tiangolo.com/) – CLI Framework
* [Rich](https://rich.readthedocs.io/) – Terminal UI
* [LangChain](https://www.langchain.com/) – AI agent orchestration
* [Google Gemini](https://ai.google/) – Core model backend

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push and open a Pull Request

---

## 📄 License

Licensed under the **MIT License**.
See [LICENSE](LICENSE) for details.

---

## 💙 Credits

* Google Gemini for language models
* LangChain for agent framework
* Rich & Typer for an amazing CLI experience

---

<div align="center">
	Made with ❤️ for the Linux community.  
	<br>
	⭐ Star this repo if you enjoy LinuxCop!
</div>
