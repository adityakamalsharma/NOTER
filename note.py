#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import json
import datetime
import shutil
import re

# ================= CONFIGURATION =================
# CHANGE THIS to your shared folder path
ROOT_PATH = "/mnt/hgfs/shared/" 
STATE_FILE = os.path.expanduser("~/.oscp_note_state")
DEFAULT_EDITOR = "nano"

# Default Template for NEW files
# You can customize these headers.
DEFAULT_TEMPLATE = """# {name}

## Information
- **IP:** {ip}
- **OS:** {os_type}
- **Difficulty:** Unknown

## Enumeration
> Initial scans and service discovery.

## Exploitation
> Foothold and reverse shells.

## Privilege Escalation
> Path to root/system.

## Loot
> Flags and credentials.

## DUMP
> Raw output dump.
"""
# =================================================

def load_state():
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return None

def save_state(name, path, ip=None):
    with open(STATE_FILE, 'w') as f:
        json.dump({"name": name, "path": path, "ip": ip}, f)

def get_headers(file_path):
    """Parses MD file and returns a list of headers starting with ##"""
    headers = []
    if not os.path.exists(file_path):
        return headers
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith("## "):
                headers.append(line.strip().replace("## ", ""))
    return headers

def insert_content(file_path, header_name, content):
    """Inserts content at the bottom of a specific header section"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find the target header index
    target_index = -1
    for i, line in enumerate(lines):
        if line.strip() == f"## {header_name}":
            target_index = i
            break
    
    if target_index == -1:
        # Header not found? Create it at the end
        lines.append(f"\n## {header_name}\n")
        target_index = len(lines) - 1

    # Find the NEXT header to know where to stop
    insert_index = len(lines)
    for i in range(target_index + 1, len(lines)):
        if lines[i].startswith("## "):
            insert_index = i
            break
            
    # Insert before the next header (minus one line to keep spacing clean)
    # We construct the payload
    payload = f"\n{content}\n"
    lines.insert(insert_index, payload)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def cmd_switch(args):
    """Switch context to a machine"""
    name = args.name
    # Determine subfolder based on OS if provided, else root of Machines
    # Simplified: We put everything in Machines/<Name>
    machine_dir = os.path.join(ROOT_PATH, name)
    note_path = os.path.join(machine_dir, f"{name}.md")
    
    if not os.path.exists(machine_dir):
        print(f"[+] Creating new workspace for: {name}")
        os.makedirs(os.path.join(machine_dir, "attachments"), exist_ok=True)
        
        # Create Note from Template
        with open(note_path, 'w') as f:
            filled_template = DEFAULT_TEMPLATE.format(
                name=name, 
                ip=args.ip if args.ip else "X.X.X.X",
                os_type=args.os if args.os else "Unknown"
            )
            f.write(filled_template)
    
    save_state(name, note_path, args.ip)
    print(f"[OK] Context set to: {name}")

def cmd_log(args):
    """Log data to the current note"""
    state = load_state()
    if not state:
        print("[!] No active context. Run 'note switch <name>' first.")
        sys.exit(1)
        
    note_path = state['path']
    if not os.path.exists(note_path):
        print(f"[!] Note file not found at {note_path}")
        sys.exit(1)

    # 1. Get Content
    content = ""
    if not sys.stdin.isatty():
        # Data is being piped in
        content = sys.stdin.read()
    else:
        # Interactive mode: Open Editor
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False, mode='w+') as tf:
            tf_path = tf.name
        
        subprocess.call([DEFAULT_EDITOR, tf_path])
        
        with open(tf_path, 'r') as tf:
            content = tf.read()
        os.remove(tf_path)

    if not content.strip():
        print("[!] Empty content. Aborting.")
        sys.exit(0)

    # 2. Select Header
    headers = get_headers(note_path)
    print("\n[?] Select Section:")
    for i, h in enumerate(headers):
        print(f" {i+1}. {h}")
    print(f" {len(headers)+1}. [Create New Section]")
    print(f" {len(headers)+2}. [DUMP (Default)]")
    
    try:
        choice = input(f"\nSelect [Default: DUMP]: ").strip()
        if not choice:
            selected_header = "DUMP"
        elif int(choice) == len(headers) + 1:
            selected_header = input("Enter new Header Name: ").strip()
        elif int(choice) == len(headers) + 2:
            selected_header = "DUMP"
        else:
            selected_header = headers[int(choice)-1]
    except:
        selected_header = "DUMP"

    # 3. Formatting
    caption = input("Optional Caption (Enter for none): ").strip()
    timestamp = datetime.datetime.now().strftime("%H:%M")
    
    formatted_block = f"### {caption if caption else 'Log Entry'} ({timestamp})\n"
    
    # Auto-collapse large output
    if len(content.splitlines()) > 15:
        formatted_block += f"<details>\n<summary>Click to Expand Content</summary>\n\n```text\n{content}\n```\n</details>"
    else:
        formatted_block += f"```text\n{content}\n```"

    insert_content(note_path, selected_header, formatted_block)
    print(f"[OK] Appended to '{selected_header}' in {state['name']}")

def cmd_shot(args):
    state = load_state()
    if not state:
        print("[!] No context set.")
        sys.exit(1)
        
    machine_dir = os.path.dirname(state['path'])
    attach_dir = os.path.join(machine_dir, "attachments")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{state['name']}_{timestamp}.png"
    dest_path = os.path.join(attach_dir, filename)
    
    # Check if xclip is installed
    if shutil.which("xclip") is None:
        print("[!] xclip not installed. Run: sudo apt install xclip")
        sys.exit(1)

    print("[*] Grabbing clipboard...")
    # Dump clipboard to file
    with open(dest_path, 'wb') as f:
        # Run xclip to output png
        p = subprocess.run(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-o'], stdout=f)
        
    if p.returncode != 0:
        print("[!] Failed to grab image. Is there an image in your clipboard?")
        # Cleanup empty file
        if os.path.exists(dest_path) and os.path.getsize(dest_path) == 0:
            os.remove(dest_path)
        sys.exit(1)

    # Append link to note
    # We use relative path for Markdown: attachments/filename.png
    link = f"![[{filename}]]"
    
    # Insert at bottom of DUMP or specified section? 
    # Usually screenshots are context-heavy, let's ask or default to Loot/Dump
    # For speed, we default to DUMP.
    insert_content(state['path'], "DUMP", f"\n**Screenshot:** {args.caption}\n{link}\n")
    print(f"[OK] Screenshot saved: {filename}")

def main():
    parser = argparse.ArgumentParser(description="OSCP Headless Note Taker")
    subparsers = parser.add_subparsers(dest="command")

    # SWITCH
    sw = subparsers.add_parser("switch", help="Set current machine context")
    sw.add_argument("name", help="Machine Name")
    sw.add_argument("--ip", help="Machine IP")
    sw.add_argument("--os", help="Operating System (linux/windows)")

    # LOG
    lg = subparsers.add_parser("log", help="Log text/output to note")

    # SHOT
    sh = subparsers.add_parser("shot", help="Save clipboard image to note")
    sh.add_argument("-c", "--caption", help="Caption for image", default="")

    args = parser.parse_args()

    if args.command == "switch":
        cmd_switch(args)
    elif args.command == "log":
        cmd_log(args)
    elif args.command == "shot":
        cmd_shot(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
