# NOTER

# Headless Note Taker (CLI-to-Obsidian)

A Python-based CLI automation tool designed for Penetration Testers. It allows you to log command output, screenshots, and notes directly from your Kali terminal into your Obsidian Vault (hosted on Windows/Host OS) without leaving the command line.

## 🚀 Features

* **Context Aware:** "Switch" modes to focus on specific machines (e.g., `note switch Sufferance`). The script remembers where to log data.
* **Headless Logging:** Pipe tool output directly to notes (`nmap ... | note log`).
* **Smart Parsing:** Automatically detects headers in your Markdown file and asks where to file the data (Enumeration, Exploitation, Loot, etc.).
* **Clipboard Screenshots:** Instantly grabs images from your clipboard, saves them to the correct attachment folder, and embeds the link in your note.
* **Auto-Templating:** Generates a clean directory structure and Markdown template for new machines.

## 🛠 Prerequisites

1.  **Environment:** Linux (Kali) VM with a Shared Folder connected to a Windows Host (where Obsidian lives).
2.  **Dependencies:**
    * Python 3
    * `xclip` (for clipboard manipulation)
    * `nano` (or your preferred terminal editor)

```bash
sudo apt update && sudo apt install xclip
```


## ⚙️ Installation & Configuration

1. **Download the Script:**
Save the script as `note.py` in your home or scripts directory.
2. **Configure Paths:**
Open `note.py` and edit the `ROOT_PATH` variable to point to your Shared Folder mount point inside Kali.
```python
# Inside note.py
ROOT_PATH = "/mnt/hgfs/Vault/Machines"  # <--- CHANGE THIS

```


3. **Create Alias:**
Add a helper function to your shell configuration (`~/.zshrc` or `~/.bashrc`) to run the script easily.
```bash
function note() {
    python3 /path/to/your/note.py "$@"
}

```


*Run `source ~/.zshrc` to apply.*

## 📖 Usage

### 1. Set the Context (Start a Box)

Before you start hacking, tell the script which machine you are working on. This creates the file structure if it doesn't exist.

```bash
note switch MachineName --ip 10.10.10.x --os linux

```

### 2. Log Tool Output (Piping)

Don't copy-paste terminal output. Pipe it.

```bash
nmap -p- -sC -sV 10.10.10.x | note log

```

* The script will ask you which **Header** (Enumeration, exploitation, etc.) to append the data to.
* Large outputs are automatically wrapped in `<details>` tags to keep your notes clean.

### 3. Log Manual Notes (Interactive)

Just want to write a quick thought?

```bash
note log

```

* Opens `nano` (or your default editor).
* Write your note, save, and exit.
* Select the target header.

### 4. Save Screenshots

Take a screenshot using your preferred tool (Flameshot, Windows Snipping Tool, etc.) and copy it to the **Clipboard**. Then run:

```bash
note shot -c "Login Page"

```

* Saves the image to `MachineName/attachments/`.
* Appends `![[Image.png]]` to the note.

## 📂 Directory Structure Created

The script organizes your vault automatically:

```text
/ROOT_PATH/
├── MachineName/
│   ├── MachineName.md      <-- The Note
│   └── attachments/        <-- Screenshots

```

## Troubleshooting

* **"Note file not found":** Ensure you ran `note switch <name>` first.
* **Permission Denied:** Ensure your VM has write access to the Shared Folder.
* **Screenshot Fails:** Ensure `xclip` is installed and you actually have an image in your clipboard.

---


```

```
