import argparse
import subprocess
from _utils import clear_terminal, cool_text
from todos import app
from Version.__init__ import VERSION

def main():
    parser = argparse.ArgumentParser(description="Task management CLI tool.")
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {VERSION}',
                        help="Show program's version number and exit.")
    parser.add_argument('--reset', action='store_true', help='Reset the application state.')

    args = parser.parse_args()

    if args.reset:
        subprocess.run(["python3", "scripts/reset.py"])
        return

    clear_terminal()
    cool_text("TASKLY")
    while True:
        done = app()
        if done == 0:
            break

if __name__ == "__main__":
    main()