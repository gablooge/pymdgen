#!/bin/env python

import argparse
import importlib
import inspect
import logging

from pymdgen import doc_module


def main():

    parser = argparse.ArgumentParser(
        description="Inspects given python modules and prints markdown")

    parser.add_argument("--debug", dest="debug", action="store_true",
                        help="display debug messages")
    parser.add_argument("--section-level", type=int, default=3,
                        help="markdown section lavel")
    parser.add_argument("modules", nargs="+")

    args = parser.parse_args()

    debug = args.debug
    modules = args.modules
    section_level = args.section_level

    if debug:
        logging.basicConfig(level=logging.DEBUG)

    for name in modules:
        md = doc_module(name, debug=debug, section_level=section_level)
        for line in md:
            print(line)

if __name__ == "__main__":
    main()

