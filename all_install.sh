set -ex
if [ -z "$1" ]; then
    echo "Usage: $0 <workspace_id>"
    exit 1
fi
export FLEXUS_WORKSPACE=$1
python -m flexus_simple_bots.frog.frog_install
python -m flexus_simple_bots.slonik.slonik_install
python -m flexus_simple_bots.karen.karen_install
python -m flexus_simple_bots.boss.boss_install
python -m flexus_simple_bots.admonster.admonster_install
python -m flexus_simple_bots.productman.productman_install
python -m flexus_simple_bots.telegram_groupmod.telegram_groupmod_install

