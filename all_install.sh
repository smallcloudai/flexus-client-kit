set -ex
if [ -z "$1" ]; then
    echo "Usage: $0 <workspace_id>"
    exit 1
fi
WS_ID=$1
python -m flexus_simple_bots.frog.frog_install --ws "$WS_ID"
python -m flexus_simple_bots.slonik.slonik_install --ws "$WS_ID"
python -m flexus_simple_bots.karen.karen_install --ws "$WS_ID"
python -m flexus_simple_bots.boss.boss_install --ws "$WS_ID"

