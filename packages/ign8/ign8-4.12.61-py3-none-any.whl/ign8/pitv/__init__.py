from . import pitv
import argparse
from ..common import prettyllog




def main():
    parser = argparse.ArgumentParser(description="Keep ign8 and automate", usage="ign8_pitv <action> \n\n \
               \
               version : 0.1.2 pitv  \n                                              \
               actions:\n                                                      \
               status        status pitv \n  \
               evacuate      evacuate this computer \n  \
               \
               2023 Knowit Miracle\
               ")
    parser.add_argument('action', metavar='<action>', type=str, nargs='+', help='setup jenkis')
    args = parser.parse_args()
    ready = False
    print("check if we are ready to go")


    if args.action[0] == "evacuate":
        pitv.evacuate()

    if args.action[0] == "status":
        print("status pitv")
        pitv.status()
