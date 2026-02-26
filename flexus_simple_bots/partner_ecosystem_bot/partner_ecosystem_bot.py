import sys
from pathlib import Path
from flexus_client_kit.runtime import no_special_code_bot

def main() -> None:
    bot_dir = Path(__file__).resolve().parent
    sys.argv = [sys.argv[0], str(bot_dir)]
    no_special_code_bot.main()

if __name__ == "__main__":
    main()
