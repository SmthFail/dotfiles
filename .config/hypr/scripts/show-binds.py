#!/usr/bin/env python3

import re
import subprocess
import sys
from pathlib import Path

CONFIG = Path.home() / ".config" / "hypr" / "hyprland" / "keybinds.lua"

PROGRAMS = {
    "terminal": "Open terminal",
    "fileManager": "Open file manager",
    "menu": "Open app launcher",
}

XF86 = {
    "XF86AudioRaiseVolume": "Volume up",
    "XF86AudioLowerVolume": "Volume down",
    "XF86AudioMute": "Mute volume",
    "XF86AudioMicMute": "Mute mic",
    "XF86MonBrightnessUp": "Brightness up",
    "XF86MonBrightnessDown": "Brightness down",
    "XF86AudioNext": "Next track",
    "XF86AudioPause": "Play/pause",
    "XF86AudioPlay": "Play/pause",
    "XF86AudioPrev": "Previous track",
}

MOUSE = {"mouse:272": "LMB", "mouse:273": "RMB"}


def normalize_combo(expr, main_mod):
    expr = expr.replace("mainMod", main_mod)
    tokens = re.findall(r'"[^"]*"|[A-Za-z0-9_:()<>?/-]+', expr)
    parts = []
    for t in tokens:
        t = t.strip('"').strip()
        if not t or t == "..":
            continue
        for piece in t.split("+"):
            piece = piece.strip()
            if piece:
                parts.append(piece)
    combo = " + ".join(parts)
    return combo.replace("SHIFT + slash", "?")


def describe(dsp, args):
    arg = args.strip()
    if dsp == "exec_cmd":
        if "hyprshutdown" in arg or "hl.dsp.exit" in arg:
            return "Exit Hyprland"
        if "show-binds" in arg:
            return "Show keybind help"
        if "screenshot.sh area" in arg:
            return "Screenshot area"
        if "screenshot.sh full" in arg:
            return "Screenshot fullscreen"
        if "screenshot.sh edit" in arg:
            return "Screenshot area and edit"
        if arg in PROGRAMS:
            return PROGRAMS[arg]
        return f"Run: {arg[:48]}"
    if dsp == "window.close":
        return "Close window"
    if dsp == "window.float":
        return "Toggle window float"
    if dsp == "window.pseudo":
        return "Toggle pseudo tiling"
    if dsp == "window.fullscreen":
        return "Toggle fullscreen"
    if dsp == "window.drag":
        return "Drag window"
    if dsp == "window.resize":
        return "Resize window"
    if dsp == "window.move":
        if "special" in arg:
            return "Move window to scratchpad"
        m = re.search(r"workspace\s*=\s*(\d+)", arg)
        if m:
            return f"Move window to workspace {m.group(1)}"
        return "Move window"
    if dsp == "workspace.toggle_special":
        return "Toggle scratchpad"
    if dsp == "layout":
        return "Toggle split layout"
    if dsp == "focus":
        m = re.search(r"direction\s*=\s*\"(\w+)\"", arg)
        if m:
            return f"Move focus {m.group(1)}"
        m = re.search(r"workspace\s*=\s*(\d+)", arg)
        if m:
            return f"Switch to workspace {m.group(1)}"
        if "e+1" in arg:
            return "Next workspace"
        if "e-1" in arg:
            return "Previous workspace"
        return "Focus"
    return ""


def main():
    text = CONFIG.read_text()

    main_mod = "SUPER"
    m = re.search(r'local\s+mainMod\s*=\s*"([^"]+)"', text)
    if m:
        main_mod = m.group(1)

    rows = []

    # Workspace loop: for i = 1, 10 do ... end  ->  keys 1-9 and 0
    loop = re.search(r"for\s+i\s*=\s*(\d+)\s*,\s*(\d+)\s*do(.*?)end", text, re.DOTALL)
    if loop:
        start, end = int(loop.group(1)), int(loop.group(2))
        body = loop.group(3)
        text = text.replace(loop.group(0), "", 1)
        for i in range(start, end + 1):
            key = str(i % 10)
            if "focus" in body and "workspace" in body:
                rows.append(f"SUPER + {key:<34}-> Switch to workspace {i}")
            if "SHIFT" in body:
                rows.append(f"SUPER + SHIFT + {key:<26}-> Move window to workspace {i}")

    # Regular binds (combo may be a pure string or built with 'mainMod .. " ... "').
    for m in re.finditer(
        r"hl\.bind\(\s*([^,]+?)\s*,\s*hl\.dsp\.([a-z_.]+)\s*\(\s*([^)]*)\)",
        text,
    ):
        combo = normalize_combo(m.group(1), main_mod)
        dsp, args = m.group(2), m.group(3)

        if combo.startswith("XF86"):
            rows.append(f"{combo:<38}-> {XF86.get(combo, 'Run command')}")
            continue

        for k, v in MOUSE.items():
            combo = combo.replace(k, v)

        desc = describe(dsp, args)
        if desc:
            rows.append(f"{combo:<38}-> {desc}")

    # Dedupe, sort by key combo
    seen, out = set(), []
    for r in rows:
        if r not in seen:
            seen.add(r)
            out.append(r)
    out.sort(key=str.lower)

    subprocess.run(
        ["rofi", "-dmenu", "-i", "-p", "Keybinds"],
        input="\n".join(out) + "\n",
        text=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
