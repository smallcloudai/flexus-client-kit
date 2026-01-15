#!/bin/bash
# Check bot installation readiness
# Usage: ./check_bot_install.sh <bot_path> [workspace_id]
# Example: ./check_bot_install.sh flexus_simple_bots/frog solarsystem

set -e

BOT_PATH="${1:?Usage: $0 <bot_path> [workspace_id]}"
WORKSPACE="${2:-solarsystem}"

# Extract bot name from path
BOT_NAME=$(basename "$BOT_PATH")

echo "=== Checking bot: $BOT_NAME ==="

# 1. Check required files exist
echo -e "\n[1/5] Checking required files..."
MISSING=0
for f in "${BOT_PATH}/${BOT_NAME}_bot.py" "${BOT_PATH}/${BOT_NAME}_prompts.py" "${BOT_PATH}/${BOT_NAME}_install.py"; do
    if [[ -f "$f" ]]; then
        echo "  ✓ $f"
    else
        echo "  ✗ $f MISSING"
        MISSING=1
    fi
done

# 2. Check images
echo -e "\n[2/5] Checking images..."
for ext in webp png jpg; do
    BIG="${BOT_PATH}/${BOT_NAME}-1024x1536.${ext}"
    SMALL="${BOT_PATH}/${BOT_NAME}-256x256.${ext}"
    if [[ -f "$BIG" ]]; then
        echo "  ✓ Big image: $BIG"
        break
    fi
done
[[ ! -f "$BIG" ]] && echo "  ✗ Missing big image (1024x1536)" && MISSING=1

for ext in webp png jpg; do
    SMALL="${BOT_PATH}/${BOT_NAME}-256x256.${ext}"
    if [[ -f "$SMALL" ]]; then
        echo "  ✓ Small image: $SMALL"
        break
    fi
done
[[ ! -f "$SMALL" ]] && echo "  ✗ Missing small image (256x256)" && MISSING=1

# 3. Syntax check
echo -e "\n[3/5] Syntax check..."
python -m py_compile "${BOT_PATH}/${BOT_NAME}_bot.py" "${BOT_PATH}/${BOT_NAME}_prompts.py" "${BOT_PATH}/${BOT_NAME}_install.py" && echo "  ✓ Syntax OK" || exit 1

# 4. Import check
echo -e "\n[4/5] Import check..."
MODULE_PATH=$(echo "$BOT_PATH" | tr '/' '.')
python -c "import ${MODULE_PATH}.${BOT_NAME}_bot; import ${MODULE_PATH}.${BOT_NAME}_install; print('  ✓ Imports OK')" || exit 1

# 5. Run install (if requested)
if [[ -n "$WORKSPACE" && "$WORKSPACE" != "skip" ]]; then
    echo -e "\n[5/5] Installing to workspace: $WORKSPACE..."
    python "${BOT_PATH}/${BOT_NAME}_install.py" --ws="$WORKSPACE" && echo "  ✓ Install OK"
else
    echo -e "\n[5/5] Skipping install (pass workspace_id to run)"
fi

echo -e "\n=== Done ==="
[[ $MISSING -eq 0 ]] && echo "All checks passed!" || echo "Some files missing, see above."
