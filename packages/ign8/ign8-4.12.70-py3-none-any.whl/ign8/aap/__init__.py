# ign8 and control your ansible automation platform

from . import status
from . import serve
import argparse

def main():
    parser = argparse.ArgumentParser(description="ign8 and con5entrate on your ansible automation platform", usage="ign8_app <action> \n\n \
\
version : 0.0.1 (aap)\n\
actions:\n\
serve      ignite and control ansible automation platform\n\
status     \n\
init       \n\
start      \n\
stop       \n\
restart    \n\
setup      \n\
test       \n\
audit      \n\
\n\
\
2024 Jakob Holst\
")
    parser.add_argument('action', metavar='<action>', type=str, nargs='+', help='setup ign8_app')
    args = parser.parse_args()
    ready = False

    if args.action[0] == "status":
        status.main()
        return 0

    if args.action[0] == "serve":
        serve.main()
        return 0