# OSCP Headless Note Taker (`note`)

A robust, CLI-first Python utility designed for rapid, organized note-taking during penetration tests. It bridges the gap between terminal operations and Obsidian-ready Markdown notes, allowing you to log data, capture screenshots, and review progress without leaving the command line.

## Features

* **Context Aware:** "Switch" to a machine once; all subsequent commands log to that specific file.
* **Obsidian Compatible:** Generates standard Markdown structure with dedicated attachment folders.
* **Pipe Friendly:** Pipe tool output directly into your notes (`nmap ... | note log`).
* **Interactive Logging:** Opens your preferred editor (`nano`/`vim`) for manual entry if no input is piped.
* **Clipboard Screenshots:** Instantly saves clipboard images to the note's attachment folder using `xclip`.
* **Glow Integration:** Renders your markdown notes beautifully in the terminal with pagination.

---

## 🛠️ Installation & Prerequisites

### Dependencies

This tool relies on system utilities for clipboard management and markdown rendering.

```bash
# 1. Install xclip (for screenshots)
sudo apt update && sudo apt install xclip

# 2. Install Glow (for 'note show')
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://repo.charm.sh/apt/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/charm.gpg
echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | sudo tee /etc/apt/sources.list.d/charm.list
sudo apt update && sudo apt install glow

```

### Setup

1. Download the script and save it as `note`.
2. Make it executable and move it to your path:
```bash
chmod +x note
sudo mv note /usr/local/bin/

```


3. **Configuration:** Open the script and edit the `CONFIGURATION` block at the top:
```python
ROOT_PATH = "/mnt/hgfs/shared/"  # Where your Obsidian vault lives
DEFAULT_EDITOR = "nano"          # Your preferred text editor

```



---

## 📖 Usage Manual (Workflow)

The commands are designed to be used hierarchically during an engagement.

### 1. Initialization (`switch`)

**Always run this first.** This sets the active "context" for the tool. It creates the directory structure and a fresh Markdown file based on the built-in template if one doesn't exist.

**Syntax:**

```bash
note switch <MachineName> [--ip <IP>] [--os <linux/windows>]

```

**Example:**

```bash
note switch Flight --ip 10.10.11.187 --os windows
# Output: [OK] Context set to: Flight

```

### 2. Viewing Context (`show`)

Review your current progress without leaving the terminal. This launches `glow` in pager mode.

**Syntax:**

```bash
note show

```

* **Controls:** Use arrow keys to scroll, `q` to quit.

### 3. Logging Data (`log`)

There are two ways to log data: **Piped** (for automation) and **Interactive** (for manual notes).

#### A. Piped Input (Automated)

Great for dumping tool output directly into a specific section (e.g., "Enumeration").

**Example:**

```bash
nmap -p- --min-rate 1000 10.10.11.187 | note log

```

* *Action:* The script detects the pipe, captures the output, and prompts you to select a section (Enumeration, Exploitation, etc.) to append it to. Long output is auto-collapsed in `<details>` tags.

#### B. Interactive Input (Manual)

Great for writing thoughts, checklists, or copy-pasting data manually.

**Example:**

```bash
note log

```

* *Action:* Opens `nano` (or configured editor). Type your note, save, and exit. The script then asks which section to append the note to.

### 4. Evidence Gathering (`shot`)

Takes an image currently stored in your clipboard, saves it to the `attachments/` folder, and appends a Markdown link to your note.

**Syntax:**

```bash
note shot [-c "Caption text"]

```

**Workflow:**

1. Take a screenshot using your OS tool (e.g., `Shift+PrintScreen` or `Flameshot`) and **copy to clipboard**.
2. Run:
```bash
note shot -c "Initial Foothold"

```


3. **Result:** The image is saved as `MachineName_Timestamp.png` and linked in your note.

---

## ⚠️ Edge Cases & Troubleshooting

| Issue | Cause | Solution |
| --- | --- | --- |
| `[!] No active context` | You tried to run `log`, `show`, or `shot` without running `switch` first. | Run `note switch <Name>` to initialize the session. |
| `[!] Glow not installed` | You ran `note show` but the binary is missing. | Follow the installation instructions above. |
| `[!] Failed to grab image` | The clipboard is empty or contains text, not an image. | Ensure you copied the screenshot to the clipboard, not just saved it to disk. |
| **New Headers** | You want to log data to a section that doesn't exist in the template (e.g., "Tunneling"). | When `note log` asks for a section, choose `[Create New Section]` and type "Tunneling". The script will create the header automatically. |
| **Empty Pipe** | You ran `cat file | note log` but the file was empty. |

---

## 📂 Directory Structure created

If `ROOT_PATH` is set to `/mnt/hgfs/shared/`, running `note switch Flight` creates:

```text
/mnt/hgfs/shared/
└── Flight/
    ├── Flight.md          # Your main Obsidian Note
    └── attachments/       # Folder for screenshots
        ├── Flight_20231025_1030.png
        └── ...

```
