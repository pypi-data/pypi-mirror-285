#!/usr/bin/env python3 
# coding=utf-8

"""
This script is used to remove special files (not regular, not directories) from a directory.
"""

import argparse
import os

from jutge import util

def sanitize(path):
    for file in os.listdir(path):
        if os.path.islink(file):
            os.remove(file)
        else:
            location = path + "/" + file
            if os.path.isdir(location):
                sanitize(location)
            elif not os.path.isfile(location):
                os.remove(location)    

def main():
    """main"""
    parser = argparse.ArgumentParser(
        description="Sanitizes the given directory, or the CWD if none is given, by removing all non directories and non regular files.",
    )
    parser.add_argument("--directory", help="The directory to sanitize",
        type = str, default=".")

    args = parser.parse_args()
    sanitize(args.directory)    

if __name__ == "__main__":
    main()    
