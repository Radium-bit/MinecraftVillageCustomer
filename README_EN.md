# Minecraft Villager Trade Command Generator

---

## Introduction

This is a GUI tool developed based on Python Tkinter, designed for **Minecraft** players to quickly generate custom villager trade commands. It supports
 configuring villager names, professions, and trade items (emeralds for 
items / items for emeralds), and provides features like trade 
configuration saving/loading, batch reversal, and sorting. Finally, it 
outputs a standard `/data modify` command that complies with Minecraft syntax, eliminating the need to manually write complex NBT tags.

This software is open-source under the **GPL-V3 License**, allowing you to use, modify, and distribute it freely.

[在找中文文档？点这里！](README.md)

---

## ✨ Core Features

- ✅ Customize basic villager info: Name, profession (13 default professions optional, default level 5)
- ✅ Flexible trade item editing:
  - Support two trade modes: "Emeralds for Items" and "Items for Emeralds"
  - Customize item ID (auto-completes `minecraft:` prefix), quantity, and max trade uses
- ✅ Trade item management:
  - Right-click list items to modify parameters directly
  - Multi-select deletion and single-item up/down sorting
  - One-click reverse all trades and append (e.g., "1 emerald → 4 eggs" → "4 eggs → 1 emerald")
- ✅ Configuration save & load: Save current villager config (name,
   profession, trades) as a JSON file, or load existing JSON presets
- ✅ Standard command generation: Automatically generates commands that comply with Minecraft syntax, ensuring two spaces between `limit=1]` and `set` without manual format checking

---

## 📥 Download & Usage

### 1. Direct Use (Recommended for Regular Users)

Obtain
 the packaged EXE file (download from the open-source repository or 
release page) and double-click to run it—no Python environment required.

### 2. Run from Source Code (Recommended for Developers)

#### Environment Requirements

- Python Version: ≥3.7 (compatible with most 3.x versions)
- Dependencies: No additional installations (based on Python standard library `tkinter`, no third-party dependencies)

#### Running Steps

1. Download the source code file (e.g., `main.py`)
2. Open the command line and navigate to the source code directory
3. Execute: `python main.py` to launch the GUI

---

## 🛠️ Package as Single-File EXE

To package the tool yourself, ensure `PyInstaller` is installed, follow these steps:

### 1. Install Dependencies

bash

```bash
pip install pyinstaller
```

### 2. Prepare the .spec File

Generate or use an existing `main.spec` file in the source code directory (used to specify packaging parameters such as window mode, icon, etc.).

### 3. Execute the Packaging Command

In the command line, navigate to the source code directory and run:

bash

```bash
pyinstaller .\main.spec
```

After packaging, find the single-file EXE in the generated `dist` folder (filename matches the `.spec` file).

---

## 🚀 User Guide

### 1. Edit Villager Info

- In the "Villager Basic Info" section: Enter the villager name 
  (default: "CustomName") and select a profession from the dropdown (13 
  options, default: "armorer").

### 2. Add Trade Items

1. Select a trade mode (e.g., "Emeralds for Items") in the "Trade Item Edit" section
2. Enter the item ID (auto-completes `minecraft:` prefix), quantity, and max trade uses (default: 256)
3. Click "Add Trade Item"—the new trade will appear in the list below 
   (light gray-green = emeralds for items, light gray-pink = items for 
   emeralds, alternating grayscale for rows)

### 3. Manage Trade Items

- **Modify Parameters**: Right-click a target trade in 
  the list and select "Edit This Trade"—the edit box will auto-fill 
  current parameters. Click "Modify Trade Item" to save after editing.
- **Sort**: Select a single trade and click "Move Selected Up" or "Move Selected Down" to adjust order.
- **Delete**: Hold Ctrl to multi-select trades, then click "Delete Selected Trades" to remove them in bulk.
- **Reverse & Append**: Click "One-Click Reverse & Append Trades" to reverse all existing trades and append them to the list.

### 4. Save/Load Configuration

- **Save**: Click "Save Config to JSON" at the top, 
  select a path and name—the config will be saved as JSON (including name,
   profession, and all trades).
- **Load**: Click "Load JSON Preset" at the top, select 
  an existing JSON config file—it will automatically overwrite current 
  villager info and trades.

### 5. Generate Command

After all configurations are complete, click "Generate Command"—the full `/data modify` command will appear in the text box below. Copy it and use it directly in Minecraft's cheat mode.

---

## ⚠️ Notes

1. Accurate Item IDs: For custom mod items (e.g., `kaleidoscope_cookery:iron_kitchen_knife`),
   ensure the corresponding mod is loaded in the game—otherwise, the 
   villager may not display trades correctly after the command takes 
   effect.
2. Right-Click Edit Limit: Only single trades can be edited via 
   right-click; the "Edit" option does not appear for multi-selections.
3. JSON Compatibility: Loaded JSON files must follow the tool's specified format (including `villager_name`, `profession`, and `trades` fields)—otherwise, a load failure prompt will appear.

---

## 📄 License Declaration

This project is open-source under the **GPL-V3 License**. See the [LICENSE](https://www.doubao.com/chat/LICENSE) file for detailed terms. When using this software, you must comply with the following principles:

- Permits non-commercial and commercial use
- Permits source code modification, but modified distributions must retain the same license
- Must retain original author information and license statement
- Must not restrict others' legal rights
