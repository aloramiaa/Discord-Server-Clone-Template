# Discord Server Cloner Bot

A Python script for cloning Discord server structure including roles, channels, and permissions.

## Features
- 🗂️ Replicates complete server structure
- 🔄 Maintains role hierarchy and permissions
- 📁 Copies categories and channels with exact settings
- ⚙️ Configurable through console input
- ✅ Error handling and permission validation

## Prerequisites
- Python 3.8+
- discord.py library (`pip install discord.py`)
- Bot token with:
  - Administrator permissions
  - Enabled privileged intents:
    * Server Members Intent
    * Message Content Intent

## Installation
```bash
git clone [repository-url]
cd py-clone
pip install discord.py
```

## Usage
1. Replace `YOUR_BOT_TOKEN_HERE` in `unified_clone.py`
2. Run the script:
```bash
python unified_clone.py
```
3. Follow the console prompts to:
   - Enter source and target server IDs
   - Confirm destructive operation
   - Monitor cloning progress

## Configuration
```python
# Bot setup
TOKEN = "YOUR_BOT_TOKEN_HERE"
intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
```

## Security Warning
⚠️ This script will:
- Permanently delete all existing roles/channels in target server
- Require bot administrator privileges
- Perform destructive operations that cannot be undone

❗ Always test with a backup server first
